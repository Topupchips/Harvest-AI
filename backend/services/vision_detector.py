"""
GPT Vision-based object detection.
Uses GPT-4o to directly locate objects in images and return bounding box coordinates.
"""
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
from PIL import Image

logger = logging.getLogger("geomarble.vision_detector")

DATA_PREVIEW_DIR = Path("data_preview")
ANNOTATED_DIR = DATA_PREVIEW_DIR / "annotated"
REFERENCE_DIR = DATA_PREVIEW_DIR / "references"


def save_reference_image(image_bytes: bytes) -> str:
    """
    Save a reference image for later detection.
    Returns a reference_id for later use.
    """
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    reference_id = uuid.uuid4().hex[:12]

    # Save original
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


async def _detect_with_gpt_vision(
    reference_b64: str,
    scene_b64: str,
    scene_width: int,
    scene_height: int,
    api_key: str,
) -> list[dict]:
    """
    Use GPT-4o Vision to find instances of the reference object in the scene.
    Returns list of bounding boxes as {x1, y1, x2, y2}.
    """
    prompt = f"""You are an object detection system.

IMAGE 1 (first image): This is the REFERENCE object you need to find.
IMAGE 2 (second image): This is the SCENE where you need to locate the reference object.

The scene image dimensions are: {scene_width}px wide x {scene_height}px tall.

Your task:
1. Carefully analyze the reference object - note its shape, color, texture, and distinctive features
2. Search the entire scene image for any instances of this object or very similar objects
3. For each instance found, provide the bounding box coordinates

IMPORTANT: Return coordinates as pixel values where:
- x1, y1 = top-left corner of the bounding box
- x2, y2 = bottom-right corner of the bounding box
- All values must be within the image bounds (0 to {scene_width} for x, 0 to {scene_height} for y)

Respond with ONLY valid JSON in this exact format:
{{
  "found": true/false,
  "objects": [
    {{"x1": 100, "y1": 150, "x2": 200, "y2": 300, "confidence": 0.95}},
    {{"x1": 400, "y1": 200, "x2": 500, "y2": 350, "confidence": 0.85}}
  ],
  "reasoning": "Brief explanation of what was found or why nothing was found"
}}

If the object is not found in the scene, return:
{{"found": false, "objects": [], "reasoning": "explanation"}}"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # GPT-5.2 uses the Responses API with input_image/input_text types
            resp = await client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-5.2",
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_image",
                                    "image_url": f"data:image/png;base64,{reference_b64}",
                                    "detail": "high",
                                },
                                {
                                    "type": "input_image",
                                    "image_url": f"data:image/png;base64,{scene_b64}",
                                    "detail": "high",
                                },
                                {"type": "input_text", "text": prompt},
                            ],
                        }
                    ],
                    "temperature": 0.1,
                    "max_output_tokens": 1000,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        # Responses API returns output in a different structure
        response_text = data["output"][0]["content"][0]["text"]
        logger.info(f"GPT Vision response: {response_text[:500]}")

        # Parse JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text.strip())

        if not result.get("found", False):
            return []

        # Validate and clamp bounding boxes to image bounds
        valid_boxes = []
        for obj in result.get("objects", []):
            x1 = max(0, min(int(obj.get("x1", 0)), scene_width))
            y1 = max(0, min(int(obj.get("y1", 0)), scene_height))
            x2 = max(0, min(int(obj.get("x2", 0)), scene_width))
            y2 = max(0, min(int(obj.get("y2", 0)), scene_height))

            # Ensure valid box (x2 > x1, y2 > y1, minimum size)
            if x2 > x1 + 10 and y2 > y1 + 10:
                valid_boxes.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(obj.get("confidence", 0.5)),
                })

        return valid_boxes

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse GPT response as JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"GPT Vision detection error: {e}")
        return []


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

        # Green box with thickness 3
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        # Label with confidence
        label = f"match {conf:.0%}"
        label_y = max(y1 - 10, 20)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(img, (x1, label_y - th - 8), (x1 + tw + 8, label_y + 4), (0, 255, 0), -1)
        cv2.putText(img, label, (x1 + 4, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    cv2.imwrite(output_path, img)


async def run_vision_detection(
    reference_id: str,
) -> AsyncGenerator[dict, None]:
    """
    Run GPT Vision detection on all extracted images.
    Yields SSE events for real-time progress.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        yield {"event": "error", "data": {"message": "OPENAI_API_KEY not set", "fatal": True}}
        return

    # Check reference exists
    ref_path = REFERENCE_DIR / f"ref_{reference_id}.png"
    if not ref_path.exists():
        yield {"event": "error", "data": {"message": f"Reference {reference_id} not found", "fatal": True}}
        return

    # Load reference as base64
    reference_b64 = _image_to_base64(str(ref_path))

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

        # Run GPT Vision detection
        yield {
            "event": "analyzing",
            "data": {"filename": filename, "status": "Analyzing with GPT Vision..."},
        }

        try:
            detections = await _detect_with_gpt_vision(
                reference_b64, scene_b64, width, height, api_key
            )
        except Exception as e:
            logger.error(f"Detection failed on {filename}: {e}")
            detections = []

        # Draw boxes and save
        annotated_filename = filename
        output_path = str(ANNOTATED_DIR / annotated_filename)

        if detections:
            await asyncio.to_thread(
                _draw_boxes_sync, img_path, detections, output_path
            )
        else:
            # Copy original without boxes
            import shutil
            await asyncio.to_thread(shutil.copy, img_path, output_path)

        total_matches += len(detections)
        all_annotated.append({
            "filename": filename,
            "annotated_filename": annotated_filename,
            "matches": len(detections),
        })

        yield {
            "event": "image_processed",
            "data": {
                "filename": filename,
                "matches": len(detections),
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
