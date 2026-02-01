from __future__ import annotations

import io
import logging

import numpy as np
from PIL import Image

logger = logging.getLogger("geomarble.panorama")


def equirect_to_perspective(
    pano_image: Image.Image,
    yaw_deg: float,
    pitch_deg: float,
    hfov_deg: float = 90.0,
    output_width: int = 1024,
    output_height: int = 1024,
) -> Image.Image:
    """
    Extract a perspective view from an equirectangular panorama.

    Args:
        pano_image: PIL Image of the equirectangular panorama.
        yaw_deg: Horizontal rotation in degrees (0=front, 90=right, etc.)
        pitch_deg: Vertical rotation in degrees (0=horizon, +up, -down)
        hfov_deg: Horizontal field of view in degrees.
        output_width: Width of output image in pixels.
        output_height: Height of output image in pixels.

    Returns:
        PIL Image of the perspective crop.
    """
    pano_w, pano_h = pano_image.size
    pano_array = np.array(pano_image)

    yaw = np.radians(yaw_deg)
    pitch = np.radians(pitch_deg)
    hfov = np.radians(hfov_deg)

    aspect = output_width / output_height
    vfov = 2 * np.arctan(np.tan(hfov / 2) / aspect)

    # Normalised pixel grid [-1, 1]
    u = np.linspace(-1, 1, output_width)
    v = np.linspace(-1, 1, output_height)
    u_grid, v_grid = np.meshgrid(u, v)

    # 3D ray directions in camera space (camera looks along +Z, +Y is up)
    x = u_grid * np.tan(hfov / 2)
    y = -v_grid * np.tan(vfov / 2)  # negate: screen top (-1) → +Y (up)
    z = np.ones_like(x)

    norm = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    x /= norm
    y /= norm
    z /= norm

    # Pitch rotation (around X axis)
    cos_p, sin_p = np.cos(pitch), np.sin(pitch)
    y2 = y * cos_p - z * sin_p
    z2 = y * sin_p + z * cos_p
    x2 = x

    # Yaw rotation (around Y axis)
    cos_y, sin_y = np.cos(yaw), np.sin(yaw)
    x3 = x2 * cos_y + z2 * sin_y
    z3 = -x2 * sin_y + z2 * cos_y
    y3 = y2

    # Spherical coordinates
    lon = np.arctan2(x3, z3)
    lat = np.arcsin(np.clip(y3, -1, 1))

    # Map to equirectangular pixel coords
    px = ((lon / np.pi + 1) / 2) * (pano_w - 1)
    py = (0.5 - lat / np.pi) * (pano_h - 1)

    px = np.clip(px, 0, pano_w - 1).astype(np.float32)
    py = np.clip(py, 0, pano_h - 1).astype(np.float32)

    # Bilinear interpolation
    px0 = np.floor(px).astype(int)
    py0 = np.floor(py).astype(int)
    px1 = np.minimum(px0 + 1, pano_w - 1)
    py1 = np.minimum(py0 + 1, pano_h - 1)

    fx = (px - px0)[..., np.newaxis]
    fy = (py - py0)[..., np.newaxis]

    c00 = pano_array[py0, px0]
    c01 = pano_array[py0, px1]
    c10 = pano_array[py1, px0]
    c11 = pano_array[py1, px1]

    result = (
        c00 * (1 - fx) * (1 - fy)
        + c01 * fx * (1 - fy)
        + c10 * (1 - fx) * fy
        + c11 * fx * fy
    )

    return Image.fromarray(result.astype(np.uint8))


# 10 diverse view configurations:
# 6 at horizon, 2 looking up, 2 looking down
VIEW_CONFIGS = [
    (0, 0), (60, 0), (120, 0), (180, 0), (240, 0), (300, 0),
    (45, 30), (225, 30),
    (135, -20), (315, -20),
]


def generate_perspective_views(
    pano_bytes: bytes,
    num_views: int = 10,
) -> list[tuple[Image.Image, float, float]]:
    """
    Generate multiple perspective views from a panorama.

    Returns list of (image, yaw_deg, pitch_deg) tuples.
    """
    pano_image = Image.open(io.BytesIO(pano_bytes)).convert("RGB")

    results = []
    for yaw, pitch in VIEW_CONFIGS[:num_views]:
        crop = equirect_to_perspective(pano_image, yaw, pitch)
        results.append((crop, yaw, pitch))
        logger.info(f"Extracted perspective view yaw={yaw}, pitch={pitch}")

    return results
