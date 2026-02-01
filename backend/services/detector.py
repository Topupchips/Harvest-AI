from __future__ import annotations

import asyncio
import base64
import io
import json
import logging
import os
import uuid
from pathlib import Path
from typing import AsyncGenerator

import cv2
import httpx
import numpy as np
from PIL import Image

logger = logging.getLogger("geomarble.detector")

DATA_PREVIEW_DIR = Path("data_preview")
ANNOTATED_DIR = DATA_PREVIEW_DIR / "annotated"
REFERENCE_DIR = DATA_PREVIEW_DIR / "references"

# Lazy-loaded YOLO model
_yolo_model = None


def _get_yolo_model():
    """Lazy-load YOLO11 nano model. First call downloads weights (~6MB)."""
    global _yolo_model
    if _yolo_model is None:
        from ultralytics import YOLO
        logger.info("Loading YOLO11n model (first load may download weights)...")
        _yolo_model = YOLO("yolo11n.pt")
        logger.info("YOLO11n model loaded.")
    return _yolo_model


def save_reference_image(image_bytes: bytes) -> str:
    """
    Save a reference image and remove its background.
    Returns a reference_id for later use.
    """
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    reference_id = uuid.uuid4().hex[:12]

    # Save original
    original_path = REFERENCE_DIR / f"ref_{reference_id}.png"
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img.save(original_path, format="PNG")
    logger.info(f"Saved reference image: {original_path}")

    # Remove background
    try:
        from rembg import remove as rembg_remove
        nobg = rembg_remove(img)
        nobg_path = REFERENCE_DIR / f"ref_{reference_id}_nobg.png"
        nobg.save(nobg_path, format="PNG")
        logger.info(f"Background removed: {nobg_path}")
    except Exception as e:
        logger.warning(f"Background removal failed, using original: {e}")
        # Copy original as the nobg version
        nobg_path = REFERENCE_DIR / f"ref_{reference_id}_nobg.png"
        img.save(nobg_path, format="PNG")

    return reference_id


def _detect_candidates_sync(
    image_path: str,
    object_class: str,
    confidence_threshold: float = 0.25,
) -> list[dict]:
    """
    Run YOLO11 inference on an image and return candidates of the target class.
    """
    model = _get_yolo_model()
    results = model(image_path, verbose=False)
    candidates = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])

            if class_name == object_class and confidence >= confidence_threshold:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                candidates.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": confidence,
                    "class_name": class_name,
                })

    return candidates


async def _verify_with_vision(
    reference_b64: str,
    candidate_b64: str,
    api_key: str,
    object_class: str,
) -> tuple[bool, float, str]:
    """
    Use GPT-4 Vision via Keywords AI to verify if a candidate matches the reference.
    Returns (is_match, confidence, reasoning).
    """
    prompt = (
        f"You are comparing two images. "
        f"IMAGE 1 is the reference {object_class}. "
        f"IMAGE 2 is a detected candidate from a scene. "
        f"Determine if IMAGE 2 contains the SAME TYPE of object as IMAGE 1. "
        f"Respond with ONLY valid JSON: "
        f'{{"is_match": true/false, "confidence": 0.0-1.0, "reasoning": "brief"}}'
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.keywordsai.co/api/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{reference_b64}"
                                    },
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{candidate_b64}"
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 300,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        response_text = data["choices"][0]["message"]["content"]

        # Parse JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text.strip())
        return (
            result.get("is_match", False),
            result.get("confidence", 0.0),
            result.get("reasoning", ""),
        )
    except Exception as e:
        logger.error(f"Vision verification error: {e}")
        return False, 0.0, str(e)


def _draw_boxes_sync(
    image_path: str,
    verified_detections: list[dict],
    output_path: str,
):
    """Draw bounding boxes on verified detections and save."""
    img = cv2.imread(image_path)
    if img is None:
        return

    for det in verified_detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det.get("confidence", 0.0)
        vision_conf = det.get("vision_confidence", 0.0)

        # Green box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Label
        label = f"{det.get('class_name', 'match')} {conf:.2f}"
        label_y = max(y1 - 10, 20)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, label_y - th - 6), (x1 + tw + 6, label_y + 4), (0, 255, 0), -1)
        cv2.putText(img, label, (x1 + 3, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    cv2.imwrite(output_path, img)


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


async def run_detection(
    reference_id: str,
    object_class: str,
) -> AsyncGenerator[dict, None]:
    """
    Run hybrid YOLO + Vision LLM detection on all extracted images.
    Yields SSE events for real-time progress.
    """
    api_key = os.environ.get("KEYWORDS_AI_API_KEY")
    if not api_key:
        yield {"event": "error", "data": {"message": "KEYWORDS_AI_API_KEY not set", "fatal": True}}
        return

    # Check reference exists
    nobg_path = REFERENCE_DIR / f"ref_{reference_id}_nobg.png"
    if not nobg_path.exists():
        yield {"event": "error", "data": {"message": f"Reference {reference_id} not found", "fatal": True}}
        return

    # Load reference as base64
    with open(nobg_path, "rb") as f:
        reference_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Find images to process (top-level PNGs only, skip subdirs)
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
            "object_class": object_class,
            "num_images": len(image_files),
        },
    }

    total_matches = 0
    all_annotated = []

    for img_file in image_files:
        img_path = str(img_file)
        filename = img_file.name

        # Step 1: YOLO candidates
        try:
            candidates = await asyncio.to_thread(
                _detect_candidates_sync, img_path, object_class
            )
        except Exception as e:
            logger.error(f"YOLO failed on {filename}: {e}")
            candidates = []

        yield {
            "event": "candidates_found",
            "data": {"filename": filename, "count": len(candidates)},
        }

        # Step 2: Vision verification for each candidate
        verified = []
        for candidate in candidates:
            try:
                candidate_b64 = await asyncio.to_thread(
                    _crop_and_encode, img_path, candidate["bbox"]
                )
                is_match, confidence, reasoning = await _verify_with_vision(
                    reference_b64, candidate_b64, api_key, object_class
                )

                if is_match:
                    candidate["vision_confidence"] = confidence
                    candidate["vision_reasoning"] = reasoning
                    verified.append(candidate)
                    yield {
                        "event": "match_verified",
                        "data": {
                            "filename": filename,
                            "bbox": candidate["bbox"],
                            "confidence": confidence,
                        },
                    }
            except Exception as e:
                logger.error(f"Vision verify failed for candidate in {filename}: {e}")

        # Step 3: Draw boxes and save
        annotated_filename = filename
        output_path = str(ANNOTATED_DIR / annotated_filename)

        if verified:
            await asyncio.to_thread(
                _draw_boxes_sync, img_path, verified, output_path
            )
        else:
            # Copy original without boxes
            import shutil
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
