import json
import logging
import traceback
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from services.worldlabs import WorldLabsClient
from services.supabase_client import store_world

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

        response = _extract_world_response(world)

        # Store in Supabase
        try:
            await store_world(
                world_id=response.get("world_id"),
                viewer_url=response.get("viewer_url"),
                thumbnail_url=response.get("thumbnail_url"),
                splat_urls=response.get("splat_urls"),
            )
        except Exception as e:
            logger.warning(f"Failed to store world in Supabase: {e}")

        return response

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
    product_image: UploadFile = File(default=None),
    product_position: str = Form(default="bottom-center"),
    product_scale: float = Form(default=0.2),
):
    """
    Generate a world from multiple images with azimuth values.

    Args:
        images: List of image files
        text_prompt: Optional text description for the world
        azimuths: JSON string of azimuth values (e.g., "[0, 90, 180, 270]")
        product_image: Optional product image to composite into one of the views
        product_position: Position for product ("center", "bottom-center", "left", "right")
        product_scale: Size of product relative to background (0.0-1.0)
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

    # If product image provided, composite it onto one random directional image
    if product_image is not None:
        if not product_image.content_type or not product_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Product file must be an image"
            )

        product_bytes = await product_image.read()
        logger.info(f"Product image received: {product_image.filename}, size={len(product_bytes)}")

        if len(product_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Product image too large (max 10MB)"
            )

        # Use AI-powered placement if GEMINI_API_KEY is available
        import os
        use_ai = os.environ.get("GEMINI_API_KEY") is not None

        direction_images = [(data[0], data[2]) for data in image_data]  # (bytes, azimuth)

        if use_ai:
            logger.info("Using Gemini 2.0 Flash for natural product placement...")
            from services.compositor import composite_product_random_direction_async
            composited_images = await composite_product_random_direction_async(
                direction_images,
                product_bytes,
                position=product_position,
                scale=product_scale,
            )
        else:
            logger.info("Using simple compositing (set GEMINI_API_KEY for AI placement)...")
            from services.compositor import composite_product_random_direction
            composited_images = composite_product_random_direction(
                direction_images,
                product_bytes,
                position=product_position,
                scale=product_scale,
            )

        # Rebuild image_data with composited results
        image_data = [
            (img_bytes, image_data[i][1], azimuth)
            for i, (img_bytes, azimuth) in enumerate(composited_images)
        ]
        logger.info("Product composited onto one directional image")

    # Save input images to a folder for inspection
    import os
    from datetime import datetime

    output_dir = os.path.join(os.path.dirname(__file__), "..", "debug_images")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, (img_bytes, filename, azimuth) in enumerate(image_data):
        output_path = os.path.join(output_dir, f"{timestamp}_view_{azimuth}.png")
        with open(output_path, "wb") as f:
            f.write(img_bytes)
        logger.info(f"Saved debug image: {output_path}")

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

        response = _extract_world_response(world)

        # Store in Supabase
        try:
            await store_world(
                world_id=response.get("world_id"),
                viewer_url=response.get("viewer_url"),
                thumbnail_url=response.get("thumbnail_url"),
                splat_urls=response.get("splat_urls"),
                text_prompt=text_prompt,
            )
        except Exception as e:
            logger.warning(f"Failed to store world in Supabase: {e}")

        return response

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
