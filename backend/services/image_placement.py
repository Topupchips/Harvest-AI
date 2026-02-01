"""
AI-powered object placement using Google Gemini 3 Pro.

Uses the official Google GenAI SDK for natural image compositing.
"""
from __future__ import annotations

import os
import io
import logging
from PIL import Image

logger = logging.getLogger("geomarble")


async def place_object_with_gemini(
    background_bytes: bytes,
    product_bytes: bytes,
    product_description: str | None = None,
    position: str = "ground-center",
    scale: float = 0.25,
) -> bytes:
    """
    Use Gemini 3 Pro to naturally place a product into a scene.

    Sends both images to Gemini and asks it to generate a composite
    where the product is naturally placed in the scene.

    Args:
        background_bytes: The scene/background image
        product_bytes: The product image to place
        product_description: Optional description of the product
        position: Position hint ("ground-center", "ground-left", "ground-right", "ground-random")
        scale: Size hint for the product (0.0-1.0)

    Returns:
        The composited image as PNG bytes
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set, falling back to simple composite")
        from services.compositor import composite_product_on_background, remove_background
        product_rgba = remove_background(product_bytes)
        return composite_product_on_background(background_bytes, product_rgba, position, scale)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.error("google-genai not installed, falling back to simple composite")
        from services.compositor import composite_product_on_background, remove_background
        product_rgba = remove_background(product_bytes)
        return composite_product_on_background(background_bytes, product_rgba, position, scale)

    # Convert bytes to PIL Images
    background_image = Image.open(io.BytesIO(background_bytes))
    product_image = Image.open(io.BytesIO(product_bytes))

    # Get dimensions for size calculations
    bg_width, bg_height = background_image.size
    prod_width, prod_height = product_image.size
    prod_aspect_ratio = prod_width / prod_height if prod_height > 0 else 1.0

    # Build position description
    position_desc = {
        "ground-center": "in the center foreground, standing on the ground",
        "ground-left": "on the left side of the foreground, standing on the ground",
        "ground-right": "on the right side of the foreground, standing on the ground",
        "ground-random": "somewhere in the foreground, standing naturally on the ground",
    }.get(position, "in the center foreground, standing on the ground")

    # Calculate target pixel dimensions based on scale
    # Keep objects realistically small - a water bottle in a street scene should be tiny
    if scale < 0.2:
        target_height = int(bg_height * 0.06)  # ~6% of image height (small)
    elif scale < 0.3:
        target_height = int(bg_height * 0.10)  # ~10% of image height (medium)
    else:
        target_height = int(bg_height * 0.14)  # ~14% of image height (large)

    target_width = int(target_height * prod_aspect_ratio)

    # Build size description with actual pixel dimensions
    size_desc = f"approximately {target_width}x{target_height} pixels (width x height)"

    # Build product description section
    product_info = ""
    if product_description:
        product_info = f"\n\nThe product is: {product_description}"

    # Build the prompt
    prompt = f"""Edit the first image to add a SMALL object from the second image.{product_info}

CRITICAL SIZE REQUIREMENT:
- The object MUST be rendered at {size_desc} in the output image
- This is a SMALL everyday object (like a water bottle ~25cm tall)
- In a street scene, such an object should appear TINY - like something someone dropped on the sidewalk
- If a person were standing in the scene, the object should reach only to their ankle/shin

Placement:
- Position: {position_desc}
- The object should look like it was casually left/dropped there

Other requirements:
- PRESERVE the original background exactly
- Match lighting and add realistic shadow
- Blend edges naturally

Output a single photorealistic image with the object at the correct small scale."""

    logger.info(f"Gemini prompt: placing product {position_desc}, {size_desc}")

    try:
        # Initialize client with API key
        client = genai.Client(api_key=api_key)

        # Generate content with both images
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=[
                prompt,
                background_image,
                product_image,
            ],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
            )
        )

        # Extract the generated image from response
        for part in response.parts:
            if part.inline_data is not None:
                # Get raw image data directly from inline_data
                logger.info("Successfully extracted generated image from Gemini")
                return part.inline_data.data
            elif part.text:
                logger.info(f"Gemini text response: {part.text[:200]}")

        raise ValueError("No image in Gemini response")

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        # Fallback to simple composite
        from services.compositor import composite_product_on_background, remove_background
        product_rgba = remove_background(product_bytes)
        return composite_product_on_background(background_bytes, product_rgba, position, scale)


async def describe_product(image_bytes: bytes) -> str:
    """
    Use Gemini to describe a product image.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "a product"

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "a product"

    # Convert bytes to PIL Image
    product_image = Image.open(io.BytesIO(image_bytes))

    prompt = """Describe this product/object in detail for image compositing.
Include: exact shape, colors, materials, textures, key visual features, and any distinctive characteristics.
Be specific about what makes this object unique.
Example: 'a tall cylindrical cobalt blue powder-coated stainless steel water bottle with matte finish and black plastic screw-cap lid'"""

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, product_image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT'],
            )
        )

        for part in response.parts:
            if part.text:
                description = part.text.strip()
                logger.info(f"Product description: {description}")
                return description

        return "a product"

    except Exception as e:
        logger.error(f"Gemini describe error: {e}")
        return "a product"


# Alias for backward compatibility
place_object_with_inpainting = place_object_with_gemini
