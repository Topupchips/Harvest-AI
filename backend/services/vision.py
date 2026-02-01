from __future__ import annotations

import os
import base64
import logging

from openai import AsyncOpenAI

logger = logging.getLogger("geomarble")


class VisionClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def describe_product_image(self, image_bytes: bytes) -> str:
        """
        Use GPT-4o to generate a detailed description of a product image.
        Returns a precise text description suitable for 3D world generation.
        """
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Detect image type from magic bytes
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            media_type = "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            media_type = "image/jpeg"
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"  # Default fallback

        logger.info(f"Describing product image, size={len(image_bytes)}, type={media_type}")

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Describe this product/object in extreme detail for 3D world generation.

Include:
- Exact shape and form factor (cylindrical, rectangular, organic, etc.)
- Colors (specific shades like "cobalt blue", gradients, patterns)
- Material and texture (glossy plastic, matte metal, transparent glass, brushed aluminum, etc.)
- Approximate size/dimensions
- Any text, logos, or branding visible
- Distinctive features (handles, caps, buttons, seams, etc.)
- Surface details (reflections, scratches, embossing)

Be extremely precise and visual. Write as a single flowing description.
Output ONLY the description, no preamble or explanation.""",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=600,
        )

        description = response.choices[0].message.content
        logger.info(f"GPT-4o description: {description[:100]}...")

        return description
