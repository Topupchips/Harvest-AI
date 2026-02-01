"""
Routes for managing stored worlds.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services.supabase_client import store_world, get_all_worlds, get_world_by_id

logger = logging.getLogger("geomarble")

router = APIRouter()


class WorldCreate(BaseModel):
    world_id: Optional[str] = None
    viewer_url: str
    thumbnail_url: Optional[str] = None
    splat_urls: Optional[list] = None
    place_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    text_prompt: Optional[str] = None


@router.get("/worlds")
async def list_worlds():
    """Get all stored worlds."""
    try:
        worlds = await get_all_worlds()
        return {"worlds": worlds}
    except Exception as e:
        logger.error(f"Failed to get worlds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worlds")
async def create_world(world: WorldCreate):
    """Manually add a world to the database."""
    try:
        # Extract world_id from viewer_url if not provided
        world_id = world.world_id
        if not world_id and world.viewer_url:
            # Extract from URL like https://marble.worldlabs.ai/world/a99f96c3-...
            parts = world.viewer_url.rstrip("/").split("/")
            if parts:
                world_id = parts[-1]

        result = await store_world(
            world_id=world_id or "unknown",
            viewer_url=world.viewer_url,
            thumbnail_url=world.thumbnail_url,
            splat_urls=world.splat_urls,
            place_name=world.place_name,
            lat=world.lat,
            lng=world.lng,
            text_prompt=world.text_prompt,
        )
        return {"success": True, "world": result}
    except Exception as e:
        logger.error(f"Failed to create world: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/worlds/{world_id}")
async def get_world(world_id: str):
    """Get a specific world by ID."""
    try:
        world = await get_world_by_id(world_id)
        if not world:
            raise HTTPException(status_code=404, detail="World not found")
        return world
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get world: {e}")
        raise HTTPException(status_code=500, detail=str(e))
