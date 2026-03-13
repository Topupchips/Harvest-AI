from __future__ import annotations

import os
import asyncio
import logging

import httpx

logger = logging.getLogger("geomarble")

WORLDLABS_BASE_URL = "https://api.worldlabs.ai/marble/v1"


class WorldLabsClient:
    def __init__(self):
        self.api_key = os.environ.get("WORLDLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("WORLDLABS_API_KEY not set in environment")
        self.headers = {
            "WLT-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def upload_image(
        self, image_bytes: bytes, filename: str = "viewport.png"
    ) -> str:
        """
        Upload an image to World Labs media assets.

        Flow:
        1. POST /media-assets:prepare_upload → get signed URL + media_asset_id
        2. PUT image bytes to the signed URL
        3. Return media_asset_id
        """
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Prepare upload
            prepare_resp = await client.post(
                f"{WORLDLABS_BASE_URL}/media-assets:prepare_upload",
                headers=self.headers,
                json={
                    "file_name": filename,
                    "kind": "image",
                    "extension": ext,
                },
            )
            logger.info(f"prepare_upload status={prepare_resp.status_code}")
            if prepare_resp.status_code != 200:
                logger.error(f"prepare_upload failed: {prepare_resp.text}")
            prepare_resp.raise_for_status()
            prepare_data = prepare_resp.json()
            logger.info(f"prepare_upload response: {prepare_data}")

            media_asset_id = prepare_data["media_asset"]["media_asset_id"]
            upload_url = prepare_data["upload_info"]["upload_url"]
            upload_method = prepare_data["upload_info"]["upload_method"]
            required_headers = prepare_data["upload_info"].get(
                "required_headers", {}
            )

            # Step 2: Upload image bytes to signed URL
            upload_headers = {**required_headers}
            if "Content-Type" not in upload_headers:
                upload_headers["Content-Type"] = f"image/{ext}"

            if upload_method.upper() == "PUT":
                upload_resp = await client.put(
                    upload_url,
                    content=image_bytes,
                    headers=upload_headers,
                )
            else:
                upload_resp = await client.post(
                    upload_url,
                    content=image_bytes,
                    headers=upload_headers,
                )
            logger.info(f"upload status={upload_resp.status_code}")
            if upload_resp.status_code >= 400:
                logger.error(f"upload failed: {upload_resp.text}")
            upload_resp.raise_for_status()

        return media_asset_id

    async def generate_world(
        self, media_asset_id: str, text_prompt: str | None = None
    ) -> str:
        """
        Initiate world generation from an uploaded image.
        Returns the operation_id for polling.
        """
        body = {
            "display_name": "WorldScout World",
            "model": "Marble 0.1-mini",
            "permission": {
                "public": True
            },
            "world_prompt": {
                "type": "image",
                "image_prompt": {
                    "source": "media_asset",
                    "media_asset_id": media_asset_id,
                },
            },
        }

        if text_prompt:
            body["world_prompt"]["text_prompt"] = text_prompt

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{WORLDLABS_BASE_URL}/worlds:generate",
                headers=self.headers,
                json=body,
            )
            logger.info(f"generate status={resp.status_code}")
            if resp.status_code >= 400:
                logger.error(f"generate failed: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"generate response: {data}")

        return data["operation_id"]
    
    async def poll_operation(
        self,
        operation_id: str,
        max_attempts: int = 120,
        interval: float = 5.0,
    ) -> dict:
        """
        Poll an operation until it completes or fails.
        Returns the World object from the completed operation.
        Raises TimeoutError after max_attempts * interval seconds.
        """
        async with httpx.AsyncClient(timeout=15.0) as client:
            for _ in range(max_attempts):
                resp = await client.get(
                    f"{WORLDLABS_BASE_URL}/operations/{operation_id}",
                    headers=self.headers,
                )
                resp.raise_for_status()
                data = resp.json()

                if data.get("done"):
                    logger.info(f"Operation done. Full response: {data}")
                    if data.get("error"):
                        raise RuntimeError(
                            f"Generation failed: {data['error']}"
                        )
                    return data.get("response", data)

                status = (
                    data.get("metadata", {})
                    .get("progress", {})
                    .get("status", "")
                )
                if status == "FAILED":
                    raise RuntimeError("World generation failed")

                await asyncio.sleep(interval)

        raise TimeoutError(
            f"Operation {operation_id} did not complete within "
            f"{max_attempts * interval}s"
        )

    async def generate_world_multi(
        self,
        images: list[tuple[bytes, str, int | float]],
        text_prompt: str | None = None,
    ) -> str:
        """
        Initiate world generation from multiple images with azimuth values.

        Args:
            images: List of (image_bytes, filename, azimuth) tuples.
                    Azimuth is the viewing angle in degrees (0-360).
            text_prompt: Optional text description for the world.

        Returns:
            The operation_id for polling.
        """
        if not images:
            raise ValueError("At least one image is required")

        # Upload all images and build the multi_image_prompt array
        multi_image_prompt = []
        for image_bytes, filename, azimuth in images:
            media_asset_id = await self.upload_image(image_bytes, filename)
            logger.info(f"Uploaded image {filename} with azimuth={azimuth}, media_asset_id={media_asset_id}")
            multi_image_prompt.append({
                "azimuth": azimuth,
                "content": {
                    "source": "media_asset",
                    "media_asset_id": media_asset_id,
                },
            })

        body = {
            "display_name": "WorldScout Multi-Image World",
            "model": "Marble 0.1-plus",
            "permission": {
                "public": True
            },
            "world_prompt": {
                "type": "multi-image",
                "multi_image_prompt": multi_image_prompt,
            },
        }

        if text_prompt:
            body["world_prompt"]["text_prompt"] = text_prompt

        logger.info(f"generate_multi request body: {body}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{WORLDLABS_BASE_URL}/worlds:generate",
                headers=self.headers,
                json=body,
            )
            logger.info(f"generate_multi status={resp.status_code}")
            if resp.status_code >= 400:
                logger.error(f"generate_multi failed: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"generate_multi response: {data}")

        return data["operation_id"]
