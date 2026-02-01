import json
import logging
import traceback
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.worldlabs import WorldLabsClient

logger = logging.getLogger("geomarble")
logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.post("/generate-world")
async def generate_world(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await image.read()
    logger.info(f"Received image: {image.filename}, size={len(image_bytes)} bytes, type={image.content_type}")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file")
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    client = WorldLabsClient()

    try:
        # Step 1: Upload image to World Labs
        logger.info("Step 1: Uploading image to World Labs...")
        media_asset_id = await client.upload_image(
            image_bytes, image.filename or "viewport.png"
        )
        logger.info(f"Step 1 done: media_asset_id={media_asset_id}")

        # Step 2: Initiate world generation
        logger.info("Step 2: Generating world...")
        operation_id = await client.generate_world(media_asset_id)
        logger.info(f"Step 2 done: operation_id={operation_id}")

        # Step 3: Poll until completion (holds connection ~30-60s)
        logger.info("Step 3: Polling for completion...")
        world = await client.poll_operation(operation_id)
        logger.info(f"Step 3 done: world keys={list(world.keys()) if isinstance(world, dict) else type(world)}")

        return _extract_world_response(world)

    except TimeoutError:
        raise HTTPException(status_code=504, detail="World generation timed out")
    except Exception as e:
        logger.error(f"World Labs API error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=502, detail=f"World Labs API error: {str(e)}"
        )


@router.post("/generate-world-multi")
async def generate_world_multi(
    images: List[UploadFile] = File(...),
    text_prompt: str = Form(default=None),
    azimuths: str = Form(...),
):
    """
    Generate a world from multiple images with azimuth values.

    Args:
        images: List of image files
        text_prompt: Optional text description for the world
        azimuths: JSON string of azimuth values (e.g., "[0, 90, 180, 270]")
    """
    # Parse azimuths JSON string
    try:
        azimuth_list = json.loads(azimuths)
        if not isinstance(azimuth_list, list):
            raise ValueError("azimuths must be a JSON array")
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid azimuths JSON: {str(e)}"
        )

    # Validate that we have matching counts
    if len(images) != len(azimuth_list):
        raise HTTPException(
            status_code=400,
            detail=f"Number of images ({len(images)}) must match number of azimuths ({len(azimuth_list)})"
        )

    if len(images) == 0:
        raise HTTPException(status_code=400, detail="At least one image is required")

    # Validate and read all images
    image_data = []
    for i, (image, azimuth) in enumerate(zip(images, azimuth_list)):
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {i + 1} ({image.filename}) must be an image"
            )

        image_bytes = await image.read()
        logger.info(f"Received image {i + 1}: {image.filename}, size={len(image_bytes)} bytes, type={image.content_type}, azimuth={azimuth}")

        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"Image {i + 1} ({image.filename}) is empty"
            )
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Image {i + 1} ({image.filename}) too large (max 10MB)"
            )

        # Validate azimuth value
        if not isinstance(azimuth, (int, float)):
            raise HTTPException(
                status_code=400,
                detail=f"Azimuth {i + 1} must be a number, got {type(azimuth).__name__}"
            )

        image_data.append((image_bytes, image.filename or f"image_{i}.png", azimuth))

    client = WorldLabsClient()

    try:
        # Step 1: Upload all images and initiate world generation
        logger.info(f"Step 1: Uploading {len(image_data)} images and generating world...")
        operation_id = await client.generate_world_multi(
            image_data,
            text_prompt=text_prompt,
        )
        logger.info(f"Step 1 done: operation_id={operation_id}")

        # Step 2: Poll until completion
        logger.info("Step 2: Polling for completion...")
        world = await client.poll_operation(operation_id)
        logger.info(f"Step 2 done: world keys={list(world.keys()) if isinstance(world, dict) else type(world)}")

        return _extract_world_response(world)

    except TimeoutError:
        raise HTTPException(status_code=504, detail="World generation timed out")
    except Exception as e:
        logger.error(f"World Labs API error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=502, detail=f"World Labs API error: {str(e)}"
        )


def _extract_world_response(world: dict) -> dict:
    """Extract relevant fields from the World Labs response, including full assets."""
    assets = world.get("assets", {})
    logger.info(f"Full world assets: {json.dumps(assets, default=str)[:2000]}")
    return {
        "viewer_url": world.get("world_marble_url"),
        "world_id": world.get("id"),
        "thumbnail_url": assets.get("thumbnail_url"),
        "splat_urls": assets.get("splats", {}).get("spz_urls"),
        "world_assets": assets,
    }
