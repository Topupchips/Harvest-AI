from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import re
import zipfile

from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse

from services.data_factory import extract_views_from_world
from services.detector import save_reference_image, run_detection

logger = logging.getLogger("geomarble.routes.data_factory")

router = APIRouter(prefix="/data-factory", tags=["data-factory"])


@router.get("/extract")
async def extract_views(
    world_id: str = Query(default=""),
    viewer_url: str = Query(default=""),
    num_views: int = Query(default=10, ge=1, le=30),
):
    """
    Extract perspective views from an existing world's panorama.
    Returns Server-Sent Events with real-time progress.
    """
    if not world_id and not viewer_url:
        raise HTTPException(
            status_code=400,
            detail="Either world_id or viewer_url is required",
        )

    async def event_generator():
        try:
            async for event in extract_views_from_world(
                world_id=world_id or None,
                viewer_url=viewer_url or None,
                num_views=num_views,
            ):
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"]),
                }
        except Exception as e:
            logger.error(f"Extraction error: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps(
                    {"message": f"Extraction failed: {str(e)}", "fatal": True}
                ),
            }

    return EventSourceResponse(event_generator())


@router.get("/preview/{filename}")
async def get_preview_image(
    filename: str,
    annotated: bool = Query(default=False),
):
    """Serve a saved image from data_preview/ or data_preview/annotated/."""
    if not re.match(r"^[\w\-]+\.png$", filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    if annotated:
        path = os.path.join("data_preview", "annotated", filename)
    else:
        path = os.path.join("data_preview", filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(path, media_type="image/png")


@router.post("/upload-reference")
async def upload_reference(image: UploadFile = File(...)):
    """Upload a reference image for object detection. Returns reference_id."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file")
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    reference_id = await asyncio.to_thread(save_reference_image, image_bytes)
    return {"reference_id": reference_id}


@router.get("/detect")
async def detect_objects(
    reference_id: str = Query(...),
    object_class: str = Query(default="car"),
):
    """Run object detection on extracted images. Returns SSE stream."""

    async def event_generator():
        try:
            async for event in run_detection(
                reference_id=reference_id,
                object_class=object_class,
            ):
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"]),
                }
        except Exception as e:
            logger.error(f"Detection error: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": json.dumps(
                    {"message": f"Detection failed: {str(e)}", "fatal": True}
                ),
            }

    return EventSourceResponse(event_generator())


@router.get("/download-annotated")
async def download_annotated():
    """Download all annotated images as a zip file."""
    annotated_dir = os.path.join("data_preview", "annotated")
    if not os.path.exists(annotated_dir):
        raise HTTPException(status_code=404, detail="No annotated images found")

    from pathlib import Path
    files = list(Path(annotated_dir).glob("*.png"))
    if not files:
        raise HTTPException(status_code=404, detail="No annotated images found")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f.name)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=annotated_images.zip"},
    )
