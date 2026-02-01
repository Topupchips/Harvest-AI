"""
Supabase client for storing generated worlds and extracted images.
"""
from __future__ import annotations

import os
import io
import logging
import uuid
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger("geomarble")

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_KEY not set in environment. Using defaults for backwards compat.")
    SUPABASE_URL = SUPABASE_URL or "https://casjsrxyujujmygemutg.supabase.co"
    SUPABASE_KEY = SUPABASE_KEY or ""

# Storage bucket for extracted images
STORAGE_BUCKET = "extracted-images"

_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        logger.info(f"Initializing Supabase client with URL: {SUPABASE_URL}")
        logger.info(f"Using key starting with: {SUPABASE_KEY[:20]}...")
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
    return _client


def reset_supabase_client():
    """Reset the client singleton (useful after env changes)."""
    global _client
    _client = None
    logger.info("Supabase client reset")


async def upload_image_to_storage(
    image_bytes: bytes,
    world_id: str,
    filename: str,
) -> str:
    """
    Upload an image to Supabase Storage.

    Args:
        image_bytes: The image data
        world_id: World ID to organize images
        filename: Original filename

    Returns:
        Public URL of the uploaded image
    """
    client = get_supabase_client()

    # Create a unique path: world_id/unique_filename.png
    unique_id = uuid.uuid4().hex[:8]
    storage_path = f"{world_id}/{unique_id}_{filename}"

    logger.info(f"Uploading to bucket '{STORAGE_BUCKET}' path '{storage_path}'...")
    logger.info(f"Image size: {len(image_bytes)} bytes")

    # Upload to storage with upsert to handle existing files
    try:
        result = client.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=image_bytes,
            file_options={"content-type": "image/png", "upsert": "true"},
        )
        logger.info(f"Storage upload result type: {type(result)}, value: {result}")

        # Check if result indicates an error
        if hasattr(result, 'error') and result.error:
            logger.error(f"Storage upload returned error: {result.error}")
            raise Exception(f"Upload error: {result.error}")

    except Exception as e:
        logger.error(f"Storage upload failed: {e}", exc_info=True)
        raise

    # Get public URL
    public_url = client.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
    logger.info(f"Uploaded image to storage: {storage_path} -> {public_url}")

    return public_url


async def update_world_extracted_images(
    world_id: str,
    extracted_images: list[dict],
) -> dict:
    """
    Update a world's extracted_images field.

    Args:
        world_id: The World Labs world ID
        extracted_images: List of image data with URLs

    Returns:
        Updated row data
    """
    client = get_supabase_client()

    result = (
        client.table("worlds")
        .update({"extracted_images": extracted_images})
        .eq("world_id", world_id)
        .execute()
    )

    logger.info(f"Updated extracted_images for world {world_id}: {len(extracted_images)} images")
    return result.data[0] if result.data else {}


async def store_world(
    world_id: str,
    viewer_url: str,
    thumbnail_url: Optional[str] = None,
    splat_urls: Optional[list] = None,
    place_name: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    text_prompt: Optional[str] = None,
) -> dict:
    """
    Store a generated world in Supabase.

    Args:
        world_id: World Labs world ID
        viewer_url: The marble viewer URL
        thumbnail_url: URL to world thumbnail
        splat_urls: List of splat file URLs
        place_name: Name of the location
        lat: Latitude of the location
        lng: Longitude of the location
        text_prompt: Text prompt used for generation

    Returns:
        The inserted row data
    """
    client = get_supabase_client()

    data = {
        "world_id": world_id,
        "viewer_url": viewer_url,
        "thumbnail_url": thumbnail_url,
        "splat_urls": splat_urls,
        "place_name": place_name,
        "lat": lat,
        "lng": lng,
        "text_prompt": text_prompt,
    }

    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}

    result = client.table("worlds").insert(data).execute()
    logger.info(f"Stored world {world_id} in Supabase")

    return result.data[0] if result.data else data


async def get_all_worlds() -> list:
    """Get all stored worlds, ordered by creation time (newest first)."""
    client = get_supabase_client()
    result = client.table("worlds").select("*").order("created_at", desc=True).execute()
    return result.data


async def get_world_by_id(world_id: str) -> Optional[dict]:
    """Get a specific world by its World Labs ID."""
    client = get_supabase_client()
    result = client.table("worlds").select("*").eq("world_id", world_id).execute()
    return result.data[0] if result.data else None
