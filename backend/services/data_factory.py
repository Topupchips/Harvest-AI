from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import AsyncGenerator

import httpx

from services.worldlabs import WorldLabsClient
from services.panorama import generate_perspective_views

logger = logging.getLogger("geomarble.data_factory")

WORLDLABS_BASE_URL = "https://api.worldlabs.ai/marble/v1"


async def _fetch_world(world_id: str) -> dict:
    """Fetch a world's data from World Labs API by its ID."""
    client = WorldLabsClient()
    async with httpx.AsyncClient(timeout=30.0) as http:
        resp = await http.get(
            f"{WORLDLABS_BASE_URL}/worlds/{world_id}",
            headers={"WLT-Api-Key": client.api_key},
        )
        resp.raise_for_status()
        return resp.json()


async def _download_image(url: str) -> bytes:
    """Download an image by URL."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


async def extract_views_from_world(
    world_id: str | None = None,
    viewer_url: str | None = None,
    num_views: int = 10,
) -> AsyncGenerator[dict, None]:
    """
    Extract perspective views from a generated world's panorama.
    The World Labs API returns a panoramic render at assets.imagery.pano_url.
    We download it and project perspective views at different angles.
    """
    output_dir = Path("data_preview")
    output_dir.mkdir(exist_ok=True)

    # Clear previous run
    for f in output_dir.glob("*.png"):
        f.unlink()

    # Extract world_id from viewer_url if needed
    if not world_id and viewer_url:
        match = re.search(r"/world/([a-f0-9\-]+)", viewer_url)
        if match:
            world_id = match.group(1)
            logger.info(f"Extracted world_id from viewer_url: {world_id}")

    if not world_id:
        yield {"event": "error", "data": {"message": "No world ID available.", "fatal": True}}
        return

    yield {
        "event": "extract_start",
        "data": {"world_id": world_id, "num_views": num_views},
    }

    # Fetch world data
    try:
        world = await _fetch_world(world_id)
        logger.info(f"Fetched world {world_id}, keys: {list(world.keys())}")
        logger.info(f"World assets: {json.dumps(world.get('assets', {}), default=str)[:2000]}")
    except Exception as e:
        logger.error(f"Failed to fetch world {world_id}: {e}")
        yield {"event": "error", "data": {"message": f"Failed to fetch world: {e}", "fatal": True}}
        return

    # Get panorama URL — World Labs returns this at assets.imagery.pano_url
    pano_url = world.get("assets", {}).get("imagery", {}).get("pano_url")
    if not pano_url:
        logger.error(f"No pano_url in world response. Assets: {json.dumps(world.get('assets', {}), default=str)}")
        yield {"event": "error", "data": {"message": "World has no panorama image. Try generating with a different model.", "fatal": True}}
        return

    yield {"event": "panorama_found", "data": {"url": pano_url}}

    # Download panorama
    try:
        pano_bytes = await _download_image(pano_url)
    except Exception as e:
        logger.error(f"Panorama download failed: {e}")
        yield {"event": "error", "data": {"message": f"Panorama download failed: {e}", "fatal": True}}
        return

    yield {"event": "panorama_downloaded", "data": {"size_bytes": len(pano_bytes)}}

    # Extract perspective views from the panorama
    try:
        views = generate_perspective_views(pano_bytes, num_views=num_views)
    except Exception as e:
        logger.error(f"Perspective extraction failed: {e}")
        yield {"event": "error", "data": {"message": f"View extraction failed: {e}", "fatal": True}}
        return

    yield {"event": "views_extracted", "data": {"num_views": len(views)}}

    # Save each view
    saved = []
    for idx, (view_image, yaw, pitch) in enumerate(views):
        filename = f"view_{idx:02d}_yaw{int(yaw)}_pitch{int(pitch)}.png"
        view_image.save(output_dir / filename)

        info = {
            "filename": filename,
            "yaw": yaw,
            "pitch": pitch,
            "image_index": idx + 1,
            "total_images": len(views),
        }
        saved.append(info)
        yield {"event": "image_saved", "data": info}

    yield {"event": "pipeline_complete", "data": {"total_saved": len(saved), "images": saved}}
