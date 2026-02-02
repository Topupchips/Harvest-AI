"""
Vision-based object detection with coarse-to-fine refinement and judge iteration.

Uses xAI Grok Vision models directly to:
1. Detect objects in full scene images using a reference image (coarse pass)
2. Crop around each rough detection and re-detect for precise coordinates (refine pass)
3. Judge / verify each refined bounding box for accuracy
4. Iteratively correct inaccurate bounding boxes (up to 2 attempts)

Requires env var:
  XAI_API_KEY  - Your xAI API key
"""
from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

import cv2
import httpx
import numpy as np
from PIL import Image

logger = logging.getLogger("geomarble.vision_detector")

DATA_PREVIEW_DIR = Path("data_preview")
ANNOTATED_DIR = DATA_PREVIEW_DIR / "annotated"
REFERENCE_DIR = DATA_PREVIEW_DIR / "references"

MAX_JUDGE_ITERATIONS = 2
PROCESS_MAX_SIZE = 1024   # Standardize images before processing
REFINE_PADDING = 0.6      # Crop 60% padding around coarse detection for refinement

# ---------------------------------------------------------------------------
# xAI model config
# ---------------------------------------------------------------------------
DETECTOR_MODEL = "grok-4-1-fast-non-reasoning"
JUDGE_MODEL = "grok-4-1-fast-non-reasoning"

XAI_BASE_URL = "https://api.x.ai/v1"


# ---------------------------------------------------------------------------
# xAI API call
# ---------------------------------------------------------------------------

def _get_xai_api_key() -> str:
    key = os.environ.get("XAI_API_KEY", "")
    if not key:
        raise RuntimeError("XAI_API_KEY env var is not set")
    return key


async def _call_xai(
    *,
    messages: list[dict],
    model: str = DETECTOR_MODEL,
    temperature: float = 0.1,
    max_tokens: int = 1000,
    call_type: str = "detect",
) -> dict[str, Any]:
    api_key = _get_xai_api_key()
    url = f"{XAI_BASE_URL}/chat/completions"

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
            resp.raise_for_status()
            data = resp.json()

        elapsed_ms = round((time.perf_counter() - start) * 1000)
        usage = data.get("usage", {})
        response_text = data["choices"][0]["message"]["content"]

        return {
            "response_text": response_text,
            "tokens_in": usage.get("prompt_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0),
            "latency_ms": elapsed_ms,
            "model": model,
            "call_type": call_type,
            "status": "success",
        }

    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.error(f"xAI call failed ({call_type}): {e}")
        return {
            "response_text": "",
            "tokens_in": 0,
            "tokens_out": 0,
            "latency_ms": elapsed_ms,
            "model": model,
            "call_type": call_type,
            "status": "error",
            "error": str(e),
        }


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def save_reference_image(image_bytes: bytes) -> str:
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    reference_id = uuid.uuid4().hex[:12]
    original_path = REFERENCE_DIR / f"ref_{reference_id}.png"

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.save(original_path, format="PNG")

    # Remove background using rembg for cleaner matching
    try:
        from rembg import remove as rembg_remove
        logger.info(f"Removing background from reference image...")
        img_rgba = Image.open(io.BytesIO(image_bytes))
        nobg = rembg_remove(img_rgba)
        # Paste onto white background so it stays RGB PNG
        white_bg = Image.new("RGB", nobg.size, (255, 255, 255))
        white_bg.paste(nobg, mask=nobg.split()[3] if nobg.mode == "RGBA" else None)
        white_bg.save(original_path, format="PNG")
        logger.info(f"Saved background-removed reference image: {original_path}")
    except Exception as e:
        logger.warning(f"Background removal failed, using original: {e}")
        # original_path already has the unprocessed image saved above

    return reference_id


def _image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _cv2_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")


def _get_image_dimensions(image_path: str) -> tuple[int, int]:
    img = cv2.imread(image_path)
    if img is None:
        return 0, 0
    h, w = img.shape[:2]
    return w, h


def _standardize_image(image_path: str) -> tuple[np.ndarray, int, int, float]:
    """
    Load and resize image so its longest side is <= PROCESS_MAX_SIZE.
    Returns (cv2_image, new_w, new_h, scale_factor).
    scale_factor: standardized_coord / scale = original_coord
    """
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    if max(w, h) <= PROCESS_MAX_SIZE:
        return img, w, h, 1.0
    scale = PROCESS_MAX_SIZE / max(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    logger.info(f"Standardized {w}x{h} -> {new_w}x{new_h} (scale={scale:.3f})")
    return resized, new_w, new_h, scale


def _crop_region(img: np.ndarray, bbox: list[int], padding_ratio: float) -> tuple[np.ndarray, int, int]:
    """
    Crop a region around a bbox with extra padding.
    Returns (cropped_img, offset_x, offset_y) where offsets are the top-left
    corner of the crop in the original image coordinate space.
    """
    h, w = img.shape[:2]
    x1, y1, x2, y2 = bbox
    bw = x2 - x1
    bh = y2 - y1
    pad_x = int(bw * padding_ratio)
    pad_y = int(bh * padding_ratio)

    cx1 = max(0, x1 - pad_x)
    cy1 = max(0, y1 - pad_y)
    cx2 = min(w, x2 + pad_x)
    cy2 = min(h, y2 + pad_y)

    return img[cy1:cy2, cx1:cx2].copy(), cx1, cy1


def _crop_and_encode(image_path: str, bbox: list[int], padding: int = 10) -> str:
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    x1, y1, x2, y2 = bbox
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)
    cropped = img[y1:y2, x1:x2]
    return _cv2_to_base64(cropped)


def _draw_bbox_on_scene(scene_b64: str, bbox: list[int]) -> str:
    raw = base64.b64decode(scene_b64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    x1, y1, x2, y2 = bbox
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
    return _cv2_to_base64(img)


# ---------------------------------------------------------------------------
# Coordinate grid
# ---------------------------------------------------------------------------

def _add_coordinate_grid(img: np.ndarray) -> str:
    """
    Draw a labeled coordinate grid (8 divisions per axis) for spatial anchoring.
    Returns base64 PNG.
    """
    h, w = img.shape[:2]
    overlay = img.copy()

    num_divs = 8
    step_x = max(2, w // num_divs)
    step_y = max(2, h // num_divs)

    for i in range(num_divs + 1):
        x = min(i * step_x, w - 1)
        cv2.line(overlay, (x, 0), (x, h), (0, 255, 255), 1)
        cv2.putText(overlay, str(x), (x + 3, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    for i in range(num_divs + 1):
        y = min(i * step_y, h - 1)
        cv2.line(overlay, (0, y), (w, y), (0, 255, 255), 1)
        cv2.putText(overlay, str(y), (3, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    cv2.putText(overlay, f"{w}x{h}", (w - 100, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    return _cv2_to_base64(overlay)


# ---------------------------------------------------------------------------
# Coordinate helpers
# ---------------------------------------------------------------------------

def _maybe_rescale_coords(obj: dict, scene_width: int, scene_height: int) -> dict:
    vals = [
        float(obj.get("x1", 0)),
        float(obj.get("y1", 0)),
        float(obj.get("x2", 0)),
        float(obj.get("y2", 0)),
    ]
    if all(0 <= v <= 1.0 for v in vals):
        logger.info(f"Rescaling normalised coords {vals}")
        return {
            "x1": vals[0] * scene_width, "y1": vals[1] * scene_height,
            "x2": vals[2] * scene_width, "y2": vals[3] * scene_height,
            "confidence": obj.get("confidence", 0.5),
        }
    if (scene_width > 200 and scene_height > 200
            and all(0 <= v <= 100 for v in vals) and max(vals) <= 100):
        logger.info(f"Rescaling percentage coords {vals}")
        return {
            "x1": vals[0] / 100.0 * scene_width, "y1": vals[1] / 100.0 * scene_height,
            "x2": vals[2] / 100.0 * scene_width, "y2": vals[3] / 100.0 * scene_height,
            "confidence": obj.get("confidence", 0.5),
        }
    return obj


def _parse_json_response(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def _clamp_and_validate_bbox(obj: dict, w: int, h: int) -> list[int] | None:
    x1 = max(0, min(int(obj.get("x1", 0)), w))
    y1 = max(0, min(int(obj.get("y1", 0)), h))
    x2 = max(0, min(int(obj.get("x2", 0)), w))
    y2 = max(0, min(int(obj.get("y2", 0)), h))
    if x2 > x1 + 10 and y2 > y1 + 10:
        return [x1, y1, x2, y2]
    return None


def _draw_boxes_sync(image_path: str, detections: list[dict], output_path: str):
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
        cv2.rectangle(img, (x1, label_y - th - 8), (x1 + tw + 8, label_y + 4), (0, 255, 0), -1)
        cv2.putText(img, label, (x1 + 4, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.imwrite(output_path, img)


# ---------------------------------------------------------------------------
# Pass 0: Describe the reference object (colors, shape, features)
# ---------------------------------------------------------------------------

async def _describe_reference(reference_b64: str) -> tuple[str, dict]:
    """
    Ask the vision model to describe the reference object's key visual features.
    Returns (description_text, call_meta).
    """
    prompt_text = (
        "Describe this object in detail for identification purposes. Focus on:\n"
        "1. COLORS — list all prominent colors (e.g. 'dark green body with white label and red cap')\n"
        "2. SHAPE — overall silhouette and proportions\n"
        "3. DISTINCTIVE FEATURES — logos, text, patterns, textures, unique markings\n"
        "4. SIZE ESTIMATE — relative to common objects (e.g. 'roughly 30cm tall')\n\n"
        "Be specific about colors — include shades (dark blue vs light blue), "
        "color placement (red stripe near top), and color combinations.\n\n"
        "Return ONLY valid JSON:\n"
        '{"colors": ["color1", "color2"], "shape": "brief shape description", '
        '"features": "distinctive features", "description": "one-sentence summary for matching"}'
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_b64}"}},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    result = await _call_xai(messages=messages, model=DETECTOR_MODEL, call_type="detect", max_tokens=500)

    if result["status"] != "success":
        logger.error(f"Reference description failed: {result.get('error')}")
        return "", result

    try:
        parsed = _parse_json_response(result["response_text"])
        desc = parsed.get("description", "")
        colors = parsed.get("colors", [])
        shape = parsed.get("shape", "")
        features = parsed.get("features", "")

        # Build a rich description string for use in detection prompts
        parts = []
        if colors:
            parts.append(f"Colors: {', '.join(colors)}")
        if shape:
            parts.append(f"Shape: {shape}")
        if features:
            parts.append(f"Features: {features}")
        if desc:
            parts.append(f"Summary: {desc}")

        description = ". ".join(parts)
        logger.info(f"Reference description: {description}")
        return description, result

    except Exception as e:
        logger.error(f"Failed to parse reference description: {e}")
        # Fall back to empty description — detection still works, just less guided
        return "", result


# ---------------------------------------------------------------------------
# Pass 1: Coarse detection on full image
# ---------------------------------------------------------------------------

async def _detect_coarse(
    reference_b64: str,
    std_img: np.ndarray,
    std_w: int,
    std_h: int,
    ref_description: str = "",
) -> tuple[list[dict], dict]:
    """
    Full-image detection to find approximate locations of the reference object.
    Returns (coarse_detections, call_meta).
    """
    gridded_b64 = _add_coordinate_grid(std_img)

    cx, cy = std_w // 2, std_h // 2
    ex_x1, ex_y1 = cx - std_w // 8, cy - std_h // 8
    ex_x2, ex_y2 = cx + std_w // 8, cy + std_h // 8

    # Build description block if available
    desc_block = ""
    if ref_description:
        desc_block = (
            f"\nREFERENCE OBJECT DESCRIPTION (from prior analysis):\n"
            f"{ref_description}\n"
            f"Use these visual features — especially the COLORS — to identify matches.\n"
            f"Only count objects that match these specific colors and features.\n\n"
        )

    prompt_text = (
        "You are a precise object detection system.\n\n"
        "IMAGE 1 (first image): The REFERENCE object you need to find.\n"
        "IMAGE 2 (second image): The SCENE image with a yellow coordinate grid overlay. "
        "The grid numbers along the edges show pixel positions.\n\n"
        f"Scene size: {std_w}px wide x {std_h}px tall.\n"
        f"{desc_block}\n"
        "INSTRUCTIONS:\n"
        "1. Study the reference object carefully — note its exact COLORS, shape, texture, and any markings.\n"
        "2. Scan the ENTIRE scene systematically (left-to-right, top-to-bottom) for every instance.\n"
        "3. COLOR MATCHING IS CRITICAL: Only match objects with the same colors as the reference. "
        "A red car is NOT a match for a blue car. A green bottle is NOT a match for a clear bottle.\n"
        "4. Look in ALL areas: foreground, background, partially occluded, small or distant.\n"
        "5. For each instance, return the bounding box as PIXEL coordinates.\n\n"
        "COORDINATE RULES:\n"
        "- x1, y1 = TOP-LEFT corner of the object\n"
        "- x2, y2 = BOTTOM-RIGHT corner of the object\n"
        f"- x values: 0 to {std_w},  y values: 0 to {std_h}\n"
        "- Use the yellow grid numbers to estimate positions.\n"
        "- Do NOT return normalised (0-1) or percentage (0-100) values.\n\n"
        f"EXAMPLE for a centred object: "
        f'{{"x1": {ex_x1}, "y1": {ex_y1}, "x2": {ex_x2}, "y2": {ex_y2}, "confidence": 0.9}}\n\n'
        "Return ONLY valid JSON:\n"
        '{"found": true/false, "objects": [{"x1": int, "y1": int, "x2": int, "y2": int, "confidence": float}], "reasoning": "brief"}\n'
        'If not found: {"found": false, "objects": [], "reasoning": "..."}'
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{gridded_b64}"}},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    result = await _call_xai(messages=messages, model=DETECTOR_MODEL, call_type="detect")

    if result["status"] != "success":
        logger.error(f"Coarse detection failed: {result.get('error')}")
        return [], result

    try:
        response_text = result["response_text"]
        logger.info(f"Coarse detection response: {response_text[:500]}")
        parsed = _parse_json_response(response_text)

        if not parsed.get("found", False):
            return [], result

        detections = []
        for obj in parsed.get("objects", []):
            obj = _maybe_rescale_coords(obj, std_w, std_h)
            bbox = _clamp_and_validate_bbox(obj, std_w, std_h)
            if bbox:
                detections.append({
                    "bbox": bbox,
                    "confidence": float(obj.get("confidence", 0.5)),
                })

        return detections, result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse coarse detection JSON: {e}")
        return [], result
    except Exception as e:
        logger.error(f"Coarse detection error: {e}")
        return [], result


# ---------------------------------------------------------------------------
# Pass 2: Refine each coarse detection on a cropped region
# ---------------------------------------------------------------------------

async def _refine_detection(
    reference_b64: str,
    std_img: np.ndarray,
    coarse_bbox: list[int],
    ref_description: str = "",
) -> tuple[list[int] | None, dict]:
    """
    Crop around a coarse detection with generous padding, add grid,
    and re-detect for more precise coordinates.
    Returns (refined_bbox_in_full_coords | None, call_meta).
    """
    cropped, offset_x, offset_y = _crop_region(std_img, coarse_bbox, REFINE_PADDING)
    crop_h, crop_w = cropped.shape[:2]

    gridded_crop_b64 = _add_coordinate_grid(cropped)

    # Build description block if available
    desc_block = ""
    if ref_description:
        desc_block = (
            f"\nREFERENCE OBJECT: {ref_description}\n"
            f"Match by these specific colors and features.\n\n"
        )

    prompt_text = (
        "You are a precise object detection system doing a REFINEMENT pass.\n\n"
        "IMAGE 1: The REFERENCE object.\n"
        "IMAGE 2: A CROPPED region of the scene containing (or near) the object. "
        "It has a yellow coordinate grid overlay.\n\n"
        f"This crop is {crop_w}px wide x {crop_h}px tall.\n"
        f"{desc_block}\n"
        "The reference object should be somewhere in this crop. "
        "Find the object that matches the reference's EXACT COLORS and shape, "
        "then give a TIGHT bounding box.\n\n"
        "COORDINATE RULES:\n"
        "- Coordinates are relative to THIS CROP (not the full image).\n"
        f"- x values: 0 to {crop_w},  y values: 0 to {crop_h}\n"
        "- Use the yellow grid numbers to read positions precisely.\n"
        "- The box should be TIGHT around the object — not too big, not too small.\n\n"
        "Return ONLY valid JSON:\n"
        '{"found": true/false, "objects": [{"x1": int, "y1": int, "x2": int, "y2": int, "confidence": float}], "reasoning": "brief"}\n'
        'If not found: {"found": false, "objects": [], "reasoning": "..."}'
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{gridded_crop_b64}"}},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    result = await _call_xai(messages=messages, model=DETECTOR_MODEL, call_type="detect")

    if result["status"] != "success":
        logger.error(f"Refine detection failed: {result.get('error')}")
        return None, result

    try:
        response_text = result["response_text"]
        logger.info(f"Refine response: {response_text[:300]}")
        parsed = _parse_json_response(response_text)

        if not parsed.get("found", False) or not parsed.get("objects"):
            return None, result

        # Take the highest confidence detection from the crop
        best = max(parsed["objects"], key=lambda o: float(o.get("confidence", 0)))
        best = _maybe_rescale_coords(best, crop_w, crop_h)
        bbox = _clamp_and_validate_bbox(best, crop_w, crop_h)

        if bbox is None:
            return None, result

        # Map crop-relative coordinates back to full standardized image coords
        refined = [
            bbox[0] + offset_x,
            bbox[1] + offset_y,
            bbox[2] + offset_x,
            bbox[3] + offset_y,
        ]
        logger.info(f"Refined bbox: coarse {coarse_bbox} -> refined {refined}")
        return refined, result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse refine JSON: {e}")
        return None, result
    except Exception as e:
        logger.error(f"Refine detection error: {e}")
        return None, result


# ---------------------------------------------------------------------------
# Judge system
# ---------------------------------------------------------------------------

async def _judge_bbox(
    reference_b64: str,
    scene_b64: str,
    cropped_b64: str,
    bbox: list[int],
    scene_width: int,
    scene_height: int,
) -> tuple[dict, dict]:
    annotated_scene_b64 = await asyncio.to_thread(
        _draw_bbox_on_scene, scene_b64, bbox
    )

    x1, y1, x2, y2 = bbox

    prompt_text = (
        "You are a bounding box verification judge.\n\n"
        "IMAGE 1: The REFERENCE object.\n"
        "IMAGE 2: A CROPPED region from the scene at the proposed bounding box.\n"
        "IMAGE 3: The FULL SCENE with the RED bounding box drawn on it.\n\n"
        f"Proposed bbox: x1={x1}, y1={y1}, x2={x2}, y2={y2}  (absolute pixels)\n"
        f"Scene size: {scene_width}px wide x {scene_height}px tall.\n\n"
        "Does the red box in IMAGE 3 tightly surround an instance of the reference object?\n\n"
        "Verdicts:\n"
        "- CORRECT — box tightly contains the object.\n"
        "- INCORRECT — object IS there but box is wrong. Provide corrected PIXEL coordinates.\n"
        "- NOT_FOUND — no instance of the reference object in the cropped region.\n\n"
        "IMPORTANT: All coordinates must be absolute pixel values.\n"
        f"x range: 0 – {scene_width}.  y range: 0 – {scene_height}.\n"
        "Do NOT use normalised (0-1) or percentage values.\n\n"
        "Respond with ONLY valid JSON:\n"
        '{"verdict": "CORRECT"|"INCORRECT"|"NOT_FOUND", "confidence": 0.0-1.0, '
        '"reasoning": "brief", "corrected_bbox": {"x1": int, "y1": int, "x2": int, "y2": int}}\n'
        "Only include corrected_bbox when verdict is INCORRECT."
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{cropped_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{annotated_scene_b64}"}},
                {"type": "text", "text": prompt_text},
            ],
        }
    ]

    result = await _call_xai(messages=messages, model=JUDGE_MODEL, call_type="judge")

    if result["status"] != "success":
        return {"verdict": "NOT_FOUND", "confidence": 0.0, "reasoning": result.get("error", "API error")}, result

    try:
        parsed = _parse_json_response(result["response_text"])
        verdict = {
            "verdict": parsed.get("verdict", "NOT_FOUND"),
            "confidence": float(parsed.get("confidence", 0.0)),
            "reasoning": parsed.get("reasoning", ""),
        }
        if parsed.get("corrected_bbox"):
            verdict["corrected_bbox"] = parsed["corrected_bbox"]
        return verdict, result

    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse judge response: {e}")
        return {"verdict": "NOT_FOUND", "confidence": 0.0, "reasoning": str(e)}, result


async def _judge_and_correct_detections(
    reference_b64: str,
    scene_b64: str,
    scene_path: str,
    detections: list[dict],
    scene_width: int,
    scene_height: int,
) -> tuple[list[dict], list[dict], list[dict]]:
    verified = []
    judge_logs = []
    api_calls = []

    for det_idx, detection in enumerate(detections):
        current_bbox = list(detection["bbox"])
        original_bbox = list(detection["bbox"])

        for iteration in range(1, MAX_JUDGE_ITERATIONS + 1):
            cropped_b64 = await asyncio.to_thread(
                _crop_and_encode, scene_path, current_bbox
            )

            verdict, call_meta = await _judge_bbox(
                reference_b64, scene_b64, cropped_b64,
                current_bbox, scene_width, scene_height,
            )
            api_calls.append(call_meta)

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
                break
            elif verdict["verdict"] == "INCORRECT":
                corrected = verdict.get("corrected_bbox")
                if corrected and iteration < MAX_JUDGE_ITERATIONS:
                    new_bbox = _clamp_and_validate_bbox(corrected, scene_width, scene_height)
                    if new_bbox:
                        log_entry["corrected_bbox"] = new_bbox
                        judge_logs.append(log_entry)
                        current_bbox = new_bbox
                        continue
                judge_logs.append(log_entry)
                break
            else:
                judge_logs.append(log_entry)
                break

    return verified, judge_logs, api_calls


# ---------------------------------------------------------------------------
# Main detection pipeline
# ---------------------------------------------------------------------------

async def run_vision_detection(
    reference_id: str,
) -> AsyncGenerator[dict, None]:
    """
    Run coarse-to-fine Grok Vision detection + judge verification.

    Pipeline per image:
    1. Standardize to max 1024px
    2. Coarse detection on full image (finds rough locations)
    3. Refine each detection on a cropped+padded region (precise bbox)
    4. Map back to original image coordinates
    5. Judge/verify each refined detection
    6. Draw boxes on the original image
    """
    ref_path = REFERENCE_DIR / f"ref_{reference_id}.png"
    if not ref_path.exists():
        yield {"event": "error", "data": {"message": f"Reference {reference_id} not found", "fatal": True}}
        return

    reference_b64 = _image_to_base64(str(ref_path))

    image_files = sorted([
        f for f in DATA_PREVIEW_DIR.glob("*.png")
        if f.is_file()
    ])

    if not image_files:
        yield {"event": "error", "data": {"message": "No extracted images found. Extract views first.", "fatal": True}}
        return

    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
    for f in ANNOTATED_DIR.glob("*.png"):
        f.unlink()

    # --- Pass 0: Describe the reference object ---
    ref_description, desc_meta = await _describe_reference(reference_b64)
    yield {"event": "gateway_call", "data": desc_meta}
    if ref_description:
        logger.info(f"Reference description: {ref_description}")
    else:
        logger.warning("Could not describe reference — proceeding without description")

    yield {
        "event": "detection_start",
        "data": {"reference_id": reference_id, "num_images": len(image_files), "ref_description": ref_description},
    }

    total_matches = 0
    all_annotated = []

    for img_file in image_files:
        img_path = str(img_file)
        filename = img_file.name

        orig_width, orig_height = await asyncio.to_thread(_get_image_dimensions, img_path)
        if orig_width == 0 or orig_height == 0:
            logger.error(f"Could not read image {filename}")
            continue

        # Standardize image for processing
        std_img, std_w, std_h, scale = await asyncio.to_thread(
            _standardize_image, img_path
        )

        yield {
            "event": "analyzing",
            "data": {"filename": filename, "status": "Scanning with Grok Vision..."},
        }

        # --- Pass 1: Coarse detection on full image ---
        try:
            coarse_dets, coarse_meta = await _detect_coarse(
                reference_b64, std_img, std_w, std_h, ref_description,
            )
        except Exception as e:
            logger.error(f"Coarse detection failed on {filename}: {e}")
            coarse_dets = []
            coarse_meta = {
                "call_type": "detect", "status": "error", "error": str(e),
                "model": DETECTOR_MODEL, "latency_ms": 0,
                "tokens_in": 0, "tokens_out": 0,
            }

        yield {"event": "gateway_call", "data": coarse_meta}

        if not coarse_dets:
            logger.info(f"{filename}: No objects found in coarse pass")
            # No detections — copy original and continue
            output_path = str(ANNOTATED_DIR / filename)
            await asyncio.to_thread(shutil.copy, img_path, output_path)
            all_annotated.append({"filename": filename, "annotated_filename": filename, "matches": 0})
            yield {"event": "image_processed", "data": {"filename": filename, "matches": 0, "annotated_filename": filename}}
            continue

        logger.info(f"{filename}: Coarse pass found {len(coarse_dets)} candidates, refining...")

        # --- Pass 2: Refine each coarse detection ---
        refined_dets = []
        for coarse_det in coarse_dets:
            refined_bbox, refine_meta = await _refine_detection(
                reference_b64, std_img, coarse_det["bbox"], ref_description,
            )
            yield {"event": "gateway_call", "data": refine_meta}

            if refined_bbox:
                refined_dets.append({
                    "bbox": refined_bbox,
                    "confidence": coarse_det["confidence"],
                })
            else:
                # Refinement didn't find it — fall back to coarse bbox
                logger.info(f"Refine failed, keeping coarse bbox {coarse_det['bbox']}")
                refined_dets.append(coarse_det)

        # Map standardized coordinates back to original image space
        if scale != 1.0:
            for det in refined_dets:
                det["bbox"] = [
                    int(det["bbox"][0] / scale),
                    int(det["bbox"][1] / scale),
                    int(det["bbox"][2] / scale),
                    int(det["bbox"][3] / scale),
                ]

        # Scene base64 for judge (original size)
        scene_b64 = await asyncio.to_thread(_image_to_base64, img_path)

        # --- Pass 3: Judge ---
        if refined_dets:
            yield {
                "event": "judging",
                "data": {"filename": filename, "num_detections": len(refined_dets)},
            }

            verified, judge_logs, judge_api_calls = await _judge_and_correct_detections(
                reference_b64, scene_b64, img_path, refined_dets,
                orig_width, orig_height,
            )

            for call_meta in judge_api_calls:
                yield {"event": "gateway_call", "data": call_meta}

            for log in judge_logs:
                log["filename"] = filename
                yield {"event": "judge_verdict", "data": log}

            corrected_count = sum(
                1 for l in judge_logs
                if l.get("corrected_bbox") and l["verdict"] == "INCORRECT"
            )
            removed_count = len(refined_dets) - len(verified)
            yield {
                "event": "judge_complete",
                "data": {
                    "filename": filename,
                    "original_count": len(refined_dets),
                    "verified_count": len(verified),
                    "removed_count": removed_count,
                    "corrected_count": corrected_count,
                },
            }
        else:
            verified = []

        # Draw boxes and save
        annotated_filename = filename
        output_path = str(ANNOTATED_DIR / annotated_filename)

        if verified:
            await asyncio.to_thread(_draw_boxes_sync, img_path, verified, output_path)
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
            "data": {"filename": filename, "matches": len(verified), "annotated_filename": annotated_filename},
        }

    yield {
        "event": "detection_complete",
        "data": {
            "total_images": len(image_files),
            "total_matches": total_matches,
            "annotated_images": all_annotated,
        },
    }
