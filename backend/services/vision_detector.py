"""
GPT Vision-based object detection with judge iteration system.

Uses GPT-5.2 via the Keywords AI gateway to:
1. Detect objects in scene images using a reference image
2. Judge / verify each bounding box for accuracy
3. Iteratively correct inaccurate bounding boxes (up to 2 attempts)
4. Remove detections where the object is not actually present

All LLM calls are routed through Keywords AI for logging, prompt management,
and tracing.

---------------------------------------------------------------------
KEYWORDS AI PROMPT SETUP
---------------------------------------------------------------------
Create these two prompts in the Keywords AI UI and set their IDs in .env:

### Prompt: bbox_detector  (BBOX_DETECTOR_PROMPT_ID)
Model: gpt-5.2 | Temperature: 0.1 | Max tokens: 1000
Variables: {{scene_width}}, {{scene_height}}
Content (user message):
  You are an object detection system.

  IMAGE 1 (first image): This is the REFERENCE object you need to find.
  IMAGE 2 (second image): This is the SCENE where you need to locate the reference object.

  The scene image dimensions are: {{scene_width}}px wide x {{scene_height}}px tall.

  Your task:
  1. Carefully analyze the reference object - note its shape, color, texture, and distinctive features
  2. Search the entire scene image for any instances of this object or very similar objects
  3. For each instance found, provide the bounding box coordinates

  IMPORTANT: Return coordinates as pixel values where:
  - x1, y1 = top-left corner of the bounding box
  - x2, y2 = bottom-right corner of the bounding box
  - All values must be within the image bounds (0 to {{scene_width}} for x, 0 to {{scene_height}} for y)

  Respond with ONLY valid JSON in this exact format:
  {"found": true/false, "objects": [{"x1": 100, "y1": 150, "x2": 200, "y2": 300, "confidence": 0.95}], "reasoning": "Brief explanation"}

  If the object is not found in the scene, return:
  {"found": false, "objects": [], "reasoning": "explanation"}


### Prompt: bbox_judge  (BBOX_JUDGE_PROMPT_ID)
Model: gpt-5.2 | Temperature: 0.1 | Max tokens: 1000
Variables: {{scene_width}}, {{scene_height}}, {{bbox_x1}}, {{bbox_y1}}, {{bbox_x2}}, {{bbox_y2}}
Content (user message):
  You are a bounding box verification judge.

  IMAGE 1: The REFERENCE object.
  IMAGE 2: A CROPPED region from the scene at the proposed bounding box coordinates.
  IMAGE 3: The FULL SCENE with the bounding box drawn on it.

  The proposed bounding box is: x1={{bbox_x1}}, y1={{bbox_y1}}, x2={{bbox_x2}}, y2={{bbox_y2}}
  Scene dimensions: {{scene_width}}px wide x {{scene_height}}px tall.

  Evaluate whether this bounding box accurately bounds an instance of the reference object.

  Rules:
  - CORRECT: The bbox tightly and accurately contains the reference object
  - INCORRECT: The object is present but the bbox is misaligned, too large, or too small. Provide corrected coordinates.
  - NOT_FOUND: The cropped region does not contain the reference object at all.

  Respond with ONLY valid JSON:
  {"verdict": "CORRECT"|"INCORRECT"|"NOT_FOUND", "confidence": 0.0-1.0, "reasoning": "brief explanation", "corrected_bbox": {"x1": ..., "y1": ..., "x2": ..., "y2": ...}}

  Only include corrected_bbox when verdict is INCORRECT.
---------------------------------------------------------------------
"""
from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import AsyncGenerator

import cv2
import numpy as np
from PIL import Image

from services.keywords_client import (
    call_gateway,
    get_detector_prompt_id,
    get_judge_prompt_id,
)

try:
    from keywordsai_tracing.decorators import workflow, task
except ImportError:
    # Fallback no-op decorators if tracing package not installed
    def _noop_decorator(**kwargs):
        def wrapper(fn):
            return fn
        return wrapper
    workflow = _noop_decorator
    task = _noop_decorator

logger = logging.getLogger("geomarble.vision_detector")

DATA_PREVIEW_DIR = Path("data_preview")
ANNOTATED_DIR = DATA_PREVIEW_DIR / "annotated"
REFERENCE_DIR = DATA_PREVIEW_DIR / "references"

MAX_JUDGE_ITERATIONS = 2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def save_reference_image(image_bytes: bytes) -> str:
    """Save a reference image for later detection. Returns a reference_id."""
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    reference_id = uuid.uuid4().hex[:12]

    original_path = REFERENCE_DIR / f"ref_{reference_id}.png"
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.save(original_path, format="PNG")
    logger.info(f"Saved reference image: {original_path}")

    return reference_id


def _image_to_base64(image_path: str) -> str:
    """Read an image file and return base64 encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get width and height of an image."""
    img = cv2.imread(image_path)
    if img is None:
        return 0, 0
    h, w = img.shape[:2]
    return w, h


def _crop_and_encode(image_path: str, bbox: list[int], padding: int = 10) -> str:
    """Crop a region from an image and encode as base64 PNG."""
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    cropped = img[y1:y2, x1:x2]
    _, buffer = cv2.imencode(".png", cropped)
    return base64.b64encode(buffer).decode("utf-8")


def _draw_bbox_on_scene(scene_b64: str, bbox: list[int]) -> str:
    """Draw a red rectangle on the scene image and return as base64 PNG."""
    raw = base64.b64decode(scene_b64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    x1, y1, x2, y2 = bbox
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")


def _parse_json_response(text: str) -> dict:
    """Extract JSON from an LLM response that may contain code fences."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def _clamp_and_validate_bbox(
    obj: dict, scene_width: int, scene_height: int
) -> list[int] | None:
    """Clamp bbox coords to image bounds. Returns [x1,y1,x2,y2] or None if invalid."""
    x1 = max(0, min(int(obj.get("x1", 0)), scene_width))
    y1 = max(0, min(int(obj.get("y1", 0)), scene_height))
    x2 = max(0, min(int(obj.get("x2", 0)), scene_width))
    y2 = max(0, min(int(obj.get("y2", 0)), scene_height))
    if x2 > x1 + 10 and y2 > y1 + 10:
        return [x1, y1, x2, y2]
    return None


def _draw_boxes_sync(
    image_path: str,
    detections: list[dict],
    output_path: str,
):
    """Draw bounding boxes on detected objects and save."""
    img = cv2.imread(image_path)
    if img is None:
        return

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det.get("confidence", 0.0)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        label = f"match {conf:.0%}"
        label_y = max(y1 - 10, 20)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(
            img, (x1, label_y - th - 8), (x1 + tw + 8, label_y + 4), (0, 255, 0), -1
        )
        cv2.putText(
            img, label, (x1 + 4, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2
        )

    cv2.imwrite(output_path, img)


# ---------------------------------------------------------------------------
# Detection via Keywords AI Gateway
# ---------------------------------------------------------------------------

@task(name="gpt52_detect")
async def _detect_with_gpt_vision(
    reference_b64: str,
    scene_b64: str,
    scene_width: int,
    scene_height: int,
) -> tuple[list[dict], dict]:
    """
    Use GPT-5.2 via Keywords AI gateway to find instances of the reference
    object in the scene.

    Returns (valid_boxes, gateway_meta) where gateway_meta is the raw
    gateway call metadata for the UI log.
    """
    detector_prompt_id = get_detector_prompt_id()

    # Build the prompt text - inline when no managed prompt is configured
    if detector_prompt_id:
        prompt_text = "Detect the reference object in the scene."
    else:
        prompt_text = (
            "You are an object detection system.\n\n"
            "IMAGE 1 (first image): This is the REFERENCE object you need to find.\n"
            "IMAGE 2 (second image): This is the SCENE where you need to locate the reference object.\n\n"
            f"The scene image dimensions are: {scene_width}px wide x {scene_height}px tall.\n\n"
            "Your task:\n"
            "1. Carefully analyze the reference object - note its shape, color, texture, and distinctive features\n"
            "2. Search the entire scene image for any instances of this object or very similar objects\n"
            "3. For each instance found, provide the bounding box coordinates\n\n"
            "IMPORTANT: Return coordinates as pixel values where:\n"
            "- x1, y1 = top-left corner of the bounding box\n"
            "- x2, y2 = bottom-right corner of the bounding box\n"
            f"- All values must be within the image bounds (0 to {scene_width} for x, 0 to {scene_height} for y)\n\n"
            'Respond with ONLY valid JSON in this exact format:\n'
            '{"found": true/false, "objects": [{"x1": 100, "y1": 150, "x2": 200, "y2": 300, "confidence": 0.95}], "reasoning": "Brief explanation"}\n\n'
            'If the object is not found in the scene, return:\n'
            '{"found": false, "objects": [], "reasoning": "explanation"}'
        )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{reference_b64}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{scene_b64}"},
                },
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    gw = await call_gateway(
        messages=messages,
        prompt_id=detector_prompt_id,
        variables={
            "scene_width": str(scene_width),
            "scene_height": str(scene_height),
        } if detector_prompt_id else None,
        call_type="detect",
    )

    if gw["status"] != "success":
        logger.error(f"Detection gateway call failed: {gw.get('error')}")
        return [], gw

    try:
        response_text = gw["response_text"]
        logger.info(f"GPT Vision response: {response_text[:500]}")
        result = _parse_json_response(response_text)

        if not result.get("found", False):
            return [], gw

        valid_boxes = []
        for obj in result.get("objects", []):
            bbox = _clamp_and_validate_bbox(obj, scene_width, scene_height)
            if bbox:
                valid_boxes.append({
                    "bbox": bbox,
                    "confidence": float(obj.get("confidence", 0.5)),
                })

        return valid_boxes, gw

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response as JSON: {e}")
        return [], gw
    except Exception as e:
        logger.error(f"GPT Vision detection error: {e}")
        return [], gw


# ---------------------------------------------------------------------------
# Judge system
# ---------------------------------------------------------------------------

@task(name="bbox_judge")
async def _judge_bbox(
    reference_b64: str,
    scene_b64: str,
    cropped_b64: str,
    bbox: list[int],
    scene_width: int,
    scene_height: int,
) -> tuple[dict, dict]:
    """
    Judge whether a bounding box accurately bounds the reference object.

    Returns (verdict_dict, gateway_meta).
    verdict_dict keys: verdict, confidence, reasoning, corrected_bbox (optional)
    """
    judge_prompt_id = get_judge_prompt_id()

    # Draw the bbox on the full scene for visual context
    annotated_scene_b64 = await asyncio.to_thread(
        _draw_bbox_on_scene, scene_b64, bbox
    )

    x1, y1, x2, y2 = bbox

    # Build the prompt text - inline when no managed prompt is configured
    if judge_prompt_id:
        prompt_text = "Judge this bounding box."
    else:
        prompt_text = (
            "You are a bounding box verification judge.\n\n"
            "IMAGE 1: The REFERENCE object.\n"
            "IMAGE 2: A CROPPED region from the scene at the proposed bounding box coordinates.\n"
            "IMAGE 3: The FULL SCENE with the bounding box drawn on it.\n\n"
            f"The proposed bounding box is: x1={x1}, y1={y1}, x2={x2}, y2={y2}\n"
            f"Scene dimensions: {scene_width}px wide x {scene_height}px tall.\n\n"
            "Evaluate whether this bounding box accurately bounds an instance of the reference object.\n\n"
            "Rules:\n"
            "- CORRECT: The bbox tightly and accurately contains the reference object\n"
            "- INCORRECT: The object is present but the bbox is misaligned, too large, or too small. Provide corrected coordinates.\n"
            "- NOT_FOUND: The cropped region does not contain the reference object at all.\n\n"
            "Respond with ONLY valid JSON:\n"
            '{"verdict": "CORRECT"|"INCORRECT"|"NOT_FOUND", "confidence": 0.0-1.0, "reasoning": "brief explanation", "corrected_bbox": {"x1": ..., "y1": ..., "x2": ..., "y2": ...}}\n\n'
            "Only include corrected_bbox when verdict is INCORRECT."
        )

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{reference_b64}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{cropped_b64}"},
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{annotated_scene_b64}"},
                },
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    gw = await call_gateway(
        messages=messages,
        prompt_id=judge_prompt_id,
        variables={
            "scene_width": str(scene_width),
            "scene_height": str(scene_height),
            "bbox_x1": str(x1),
            "bbox_y1": str(y1),
            "bbox_x2": str(x2),
            "bbox_y2": str(y2),
        } if judge_prompt_id else None,
        call_type="judge",
    )

    if gw["status"] != "success":
        logger.error(f"Judge gateway call failed: {gw.get('error')}")
        return {"verdict": "NOT_FOUND", "confidence": 0.0, "reasoning": gw.get("error", "Gateway error")}, gw

    try:
        result = _parse_json_response(gw["response_text"])
        verdict = {
            "verdict": result.get("verdict", "NOT_FOUND"),
            "confidence": float(result.get("confidence", 0.0)),
            "reasoning": result.get("reasoning", ""),
        }
        if result.get("corrected_bbox"):
            verdict["corrected_bbox"] = result["corrected_bbox"]
        return verdict, gw

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse judge response: {e}")
        return {"verdict": "NOT_FOUND", "confidence": 0.0, "reasoning": str(e)}, gw


@task(name="judge_iteration_loop")
async def _judge_and_correct_detections(
    reference_b64: str,
    scene_b64: str,
    scene_path: str,
    detections: list[dict],
    scene_width: int,
    scene_height: int,
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    Iterative judge loop for all detections on a single image.

    Returns (verified_detections, judge_logs, gateway_calls) where:
      - verified_detections: list of detections that passed judging
      - judge_logs: per-verdict log entries for the frontend
      - gateway_calls: raw gateway metadata for each call
    """
    verified = []
    judge_logs = []
    gateway_calls = []

    for det_idx, detection in enumerate(detections):
        current_bbox = list(detection["bbox"])
        original_bbox = list(detection["bbox"])

        for iteration in range(1, MAX_JUDGE_ITERATIONS + 1):
            # Crop the current bbox region
            cropped_b64 = await asyncio.to_thread(
                _crop_and_encode, scene_path, current_bbox
            )

            verdict, gw_meta = await _judge_bbox(
                reference_b64, scene_b64, cropped_b64,
                current_bbox, scene_width, scene_height,
            )
            gateway_calls.append(gw_meta)

            log_entry = {
                "detection_index": det_idx,
                "iteration": iteration,
                "bbox": current_bbox,
                "original_bbox": original_bbox,
                "verdict": verdict["verdict"],
                "confidence": verdict["confidence"],
                "reasoning": verdict["reasoning"],
            }

            if verdict["verdict"] == "CORRECT":
                detection["bbox"] = current_bbox
                detection["judge_confidence"] = verdict["confidence"]
                verified.append(detection)
                judge_logs.append(log_entry)
                break

            elif verdict["verdict"] == "NOT_FOUND":
                judge_logs.append(log_entry)
                break  # discard this detection

            elif verdict["verdict"] == "INCORRECT":
                corrected = verdict.get("corrected_bbox")
                if corrected and iteration < MAX_JUDGE_ITERATIONS:
                    new_bbox = _clamp_and_validate_bbox(
                        corrected, scene_width, scene_height
                    )
                    if new_bbox:
                        log_entry["corrected_bbox"] = new_bbox
                        judge_logs.append(log_entry)
                        current_bbox = new_bbox
                        continue  # re-judge with corrected bbox
                # Max iterations reached or no valid correction
                judge_logs.append(log_entry)
                break  # discard
            else:
                judge_logs.append(log_entry)
                break

    return verified, judge_logs, gateway_calls


# ---------------------------------------------------------------------------
# Main detection pipeline
# ---------------------------------------------------------------------------

async def run_vision_detection(
    reference_id: str,
) -> AsyncGenerator[dict, None]:
    """
    Run GPT Vision detection + judge verification on all extracted images.
    Yields SSE events for real-time progress.
    """
    # Check reference exists
    ref_path = REFERENCE_DIR / f"ref_{reference_id}.png"
    if not ref_path.exists():
        yield {"event": "error", "data": {"message": f"Reference {reference_id} not found", "fatal": True}}
        return

    # Load reference as base64
    reference_b64 = _image_to_base64(str(ref_path))

    # Find images to process
    image_files = sorted([
        f for f in DATA_PREVIEW_DIR.glob("*.png")
        if f.is_file()
    ])

    if not image_files:
        yield {"event": "error", "data": {"message": "No extracted images found. Extract views first.", "fatal": True}}
        return

    # Clear annotated directory
    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
    for f in ANNOTATED_DIR.glob("*.png"):
        f.unlink()

    yield {
        "event": "detection_start",
        "data": {
            "reference_id": reference_id,
            "num_images": len(image_files),
        },
    }

    total_matches = 0
    all_annotated = []

    for img_file in image_files:
        img_path = str(img_file)
        filename = img_file.name

        # Get image dimensions
        width, height = await asyncio.to_thread(_get_image_dimensions, img_path)
        if width == 0 or height == 0:
            logger.error(f"Could not read image {filename}")
            continue

        # Load scene image as base64
        scene_b64 = await asyncio.to_thread(_image_to_base64, img_path)

        # --- Step 1: Detect ---
        yield {
            "event": "analyzing",
            "data": {"filename": filename, "status": "Analyzing with GPT Vision..."},
        }

        try:
            detections, detect_gw = await _detect_with_gpt_vision(
                reference_b64, scene_b64, width, height
            )
        except Exception as e:
            logger.error(f"Detection failed on {filename}: {e}")
            detections = []
            detect_gw = {"call_type": "detect", "status": "error", "error": str(e),
                         "model": "gpt-5.2", "prompt_id": "", "latency_ms": 0,
                         "tokens_in": 0, "tokens_out": 0}

        # Emit gateway call event for the detection
        yield {"event": "gateway_call", "data": detect_gw}

        # --- Step 2: Judge ---
        if detections:
            yield {
                "event": "judging",
                "data": {"filename": filename, "num_detections": len(detections)},
            }

            verified, judge_logs, judge_gw_calls = await _judge_and_correct_detections(
                reference_b64, scene_b64, img_path, detections,
                width, height,
            )

            # Emit gateway call events for each judge call
            for gw_call in judge_gw_calls:
                yield {"event": "gateway_call", "data": gw_call}

            # Emit per-detection judge verdicts
            for log in judge_logs:
                log["filename"] = filename
                yield {"event": "judge_verdict", "data": log}

            # Emit judge summary for this image
            corrected_count = sum(
                1 for l in judge_logs
                if l.get("corrected_bbox") and l["verdict"] == "INCORRECT"
            )
            removed_count = len(detections) - len(verified)
            yield {
                "event": "judge_complete",
                "data": {
                    "filename": filename,
                    "original_count": len(detections),
                    "verified_count": len(verified),
                    "removed_count": removed_count,
                    "corrected_count": corrected_count,
                },
            }
        else:
            verified = []

        # --- Step 3: Draw boxes and save ---
        annotated_filename = filename
        output_path = str(ANNOTATED_DIR / annotated_filename)

        if verified:
            await asyncio.to_thread(
                _draw_boxes_sync, img_path, verified, output_path
            )
        else:
            await asyncio.to_thread(shutil.copy, img_path, output_path)

        total_matches += len(verified)
        all_annotated.append({
            "filename": filename,
            "annotated_filename": annotated_filename,
            "matches": len(verified),
        })

        yield {
            "event": "image_processed",
            "data": {
                "filename": filename,
                "matches": len(verified),
                "annotated_filename": annotated_filename,
            },
        }

    yield {
        "event": "detection_complete",
        "data": {
            "total_images": len(image_files),
            "total_matches": total_matches,
            "annotated_images": all_annotated,
        },
    }
