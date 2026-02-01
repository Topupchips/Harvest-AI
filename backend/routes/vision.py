from __future__ import annotations

import logging
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException

router = APIRouter()
logger = logging.getLogger("geomarble")


@router.post("/describe-image")
async def describe_image(image: UploadFile = File(...)):
    """
    Use GPT-4o to generate a detailed description of a product image.
    Returns a precise text description suitable for 3D world generation.
    """
    try:
        from services.vision import VisionClient

        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image bytes
        image_bytes = await image.read()

        if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        logger.info(f"Describing image: {image.filename}, size: {len(image_bytes)}")

        # Get description from GPT-4o
        client = VisionClient()
        description = await client.describe_product_image(image_bytes)

        return {"description": description}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error describing image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove-background")
async def remove_background_endpoint(image: UploadFile = File(...)):
    """
    Remove background from a product image using rembg.
    Returns the image with transparent background as PNG.
    """
    try:
        from services.compositor import remove_background
        import io

        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_bytes = await image.read()

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

        logger.info(f"Removing background from: {image.filename}")

        # Remove background
        rgba_image = remove_background(image_bytes)

        # Convert to PNG bytes
        buffer = io.BytesIO()
        rgba_image.save(buffer, format='PNG')
        buffer.seek(0)

        from fastapi.responses import Response

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=product_nobg.png"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing background: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
