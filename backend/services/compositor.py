from __future__ import annotations

import io
import random
import logging
from PIL import Image

logger = logging.getLogger("geomarble")


def remove_background(image_bytes: bytes) -> Image.Image:
    """
    Remove background from product image using rembg.
    Returns RGBA image with transparent background.
    """
    try:
        from rembg import remove

        input_image = Image.open(io.BytesIO(image_bytes))
        output_image = remove(input_image)
        logger.info(f"Background removed, output size: {output_image.size}, mode: {output_image.mode}")
        return output_image
    except ImportError:
        logger.warning("rembg not installed, using image as-is")
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        return img


def composite_product_on_background(
    background_bytes: bytes,
    product_input: Image.Image | bytes,
    position: str = "ground-center",
    scale: float = 0.2,
    use_ai_placement: bool = False,
) -> bytes:
    """
    Composite a product image onto a background image naturally.
    Places objects on the ground/floor level so they look like they belong.

    Args:
        background_bytes: Background image as bytes (e.g., Street View image)
        product_input: Product image as PIL Image (RGBA) or raw bytes
        position: Where to place product:
            - "ground-center": On the ground, centered horizontally
            - "ground-left": On the ground, left side
            - "ground-right": On the ground, right side
            - "ground-random": On the ground, random horizontal position
        scale: Size of product relative to background (0.0-1.0)
        use_ai_placement: If True, attempts AI inpainting (requires async call)

    Returns:
        Composited image as PNG bytes
    """
    # Handle product input - can be PIL Image or bytes
    if isinstance(product_input, bytes):
        # Remove background from product bytes
        product_image = remove_background(product_input)
    else:
        product_image = product_input

    # Open background
    background = Image.open(io.BytesIO(background_bytes))
    if background.mode != 'RGBA':
        background = background.convert('RGBA')

    bg_width, bg_height = background.size

    # Resize product to fit within scale of background
    prod_width, prod_height = product_image.size
    max_dim = int(min(bg_width, bg_height) * scale)

    # Maintain aspect ratio
    ratio = min(max_dim / prod_width, max_dim / prod_height)
    new_width = int(prod_width * ratio)
    new_height = int(prod_height * ratio)

    product_resized = product_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Ground level is approximately at 65-75% of image height from top
    # This is where the floor/ground typically appears in Street View images
    ground_level = int(bg_height * 0.72)

    # Position the object so its BOTTOM edge sits on the ground
    # This makes it look like it's actually standing on the surface
    y = ground_level - new_height

    # Ensure object doesn't go above the image
    y = max(0, y)

    # Calculate horizontal position based on position parameter
    if position in ("ground-center", "bottom-center", "center"):
        # Center with slight random offset for naturalness
        offset = random.randint(-int(bg_width * 0.05), int(bg_width * 0.05))
        x = (bg_width - new_width) // 2 + offset

    elif position in ("ground-left", "left"):
        # Left third of image
        x = int(bg_width * 0.15) + random.randint(0, int(bg_width * 0.1))

    elif position in ("ground-right", "right"):
        # Right third of image
        x = bg_width - new_width - int(bg_width * 0.15) - random.randint(0, int(bg_width * 0.1))

    elif position in ("ground-random", "foreground"):
        # Random position along the ground, avoiding extreme edges
        margin = int(bg_width * 0.1)
        x = random.randint(margin, bg_width - new_width - margin)

    else:
        # Default to ground-center
        x = (bg_width - new_width) // 2

    # Clamp x to valid range
    x = max(0, min(x, bg_width - new_width))

    logger.info(
        f"Compositing product at ({x}, {y}), size: {new_width}x{new_height}, "
        f"ground_level: {ground_level}, position: {position}"
    )

    # Create composite using product's alpha channel as mask
    background.paste(product_resized, (x, y), product_resized)

    # Convert back to RGB for output (World Labs expects RGB)
    output = background.convert('RGB')

    # Save to bytes
    buffer = io.BytesIO()
    output.save(buffer, format='PNG')
    buffer.seek(0)

    return buffer.getvalue()


def composite_product_random_direction(
    direction_images: list[tuple[bytes, int]],
    product_bytes: bytes,
    position: str = "ground-center",
    scale: float = 0.2,
    use_ai_placement: bool = True,
) -> list[tuple[bytes, int]]:
    """
    Composite a product onto one randomly selected directional image.
    Uses AI inpainting for natural placement, or falls back to simple compositing.

    Args:
        direction_images: List of (image_bytes, azimuth) tuples
        product_bytes: Product image bytes
        position: Where to place product in the image (ground-center, ground-left, etc.)
        scale: Product size relative to background
        use_ai_placement: If True, use AI inpainting for natural placement

    Returns:
        List of (image_bytes, azimuth) with one image having the product composited
    """
    if not direction_images:
        return direction_images

    # Pick a random direction to composite onto
    idx = random.randint(0, len(direction_images) - 1)
    selected_azimuth = direction_images[idx][1]

    logger.info(f"Compositing product onto direction index {idx} (azimuth {selected_azimuth}°)")

    result = []
    for i, (img_bytes, azimuth) in enumerate(direction_images):
        if i == idx:
            # Composite product onto this image
            composited = composite_product_on_background(
                img_bytes, product_bytes, position, scale, use_ai_placement
            )
            result.append((composited, azimuth))
        else:
            # Keep original
            result.append((img_bytes, azimuth))

    return result


async def composite_product_random_direction_async(
    direction_images: list[tuple[bytes, int]],
    product_bytes: bytes,
    position: str = "ground-center",
    scale: float = 0.2,
) -> list[tuple[bytes, int]]:
    """
    Async version that uses AI inpainting for natural placement.

    Args:
        direction_images: List of (image_bytes, azimuth) tuples
        product_bytes: Product image bytes
        position: Where to place product in the image (ground-center, ground-left, etc.)
        scale: Product size relative to background

    Returns:
        List of (image_bytes, azimuth) with one image having the product composited
    """
    if not direction_images:
        return direction_images

    # Pick a random direction to composite onto
    idx = random.randint(0, len(direction_images) - 1)
    selected_azimuth = direction_images[idx][1]

    logger.info(f"AI compositing product onto direction index {idx} (azimuth {selected_azimuth}°)")

    # Import the AI placement module
    from services.image_placement import place_object_with_inpainting, describe_product

    # First, get an AI description of the product for better placement
    logger.info("Analyzing product image with AI...")
    product_description = await describe_product(product_bytes)
    logger.info(f"Product identified as: {product_description}")

    result = []
    for i, (img_bytes, azimuth) in enumerate(direction_images):
        if i == idx:
            # Use AI inpainting for natural placement with product description
            composited = await place_object_with_inpainting(
                img_bytes,
                product_bytes,
                product_description=product_description,
                position=position,
                scale=scale,
            )
            result.append((composited, azimuth))
        else:
            # Keep original
            result.append((img_bytes, azimuth))

    return result
