import logging
import traceback

from fastapi import APIRouter, UploadFile, File, HTTPException

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

        return {
            "viewer_url": world.get("world_marble_url"),
            "world_id": world.get("id"),
            "thumbnail_url": world.get("assets", {}).get("thumbnail_url"),
            "splat_urls": world.get("assets", {}).get("splats", {}).get("spz_urls"),
        }

    except TimeoutError:
        raise HTTPException(status_code=504, detail="World generation timed out")
    except Exception as e:
        logger.error(f"World Labs API error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=502, detail=f"World Labs API error: {str(e)}"
        )
