"""Stage B: tiling and model-ready resizing.

Images above MAX_SIDE on the long side are cut into overlapping tiles so the grader
sees defects at native resolution. Each tile carries its box in original pixels so
findings can be placed back on the source image.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import List

from PIL import Image

MAX_SIDE = 1568  # Claude standard-tier long-side cap (research note R06)


@dataclass
class Tile:
    name: str
    image: Image.Image
    box: tuple  # (x0, y0, x1, y1) in original pixels


def tile_boxes(width: int, height: int, tile: int = MAX_SIDE, overlap: float = 0.15) -> List[tuple]:
    if max(width, height) <= tile:
        return [(0, 0, width, height)]
    step = max(1, int(tile * (1 - overlap)))

    def starts(n: int) -> List[int]:
        if n <= tile:
            return [0]
        s = list(range(0, n - tile, step))
        s.append(n - tile)
        return sorted(set(s))

    return [(x, y, min(x + tile, width), min(y + tile, height)) for y in starts(height) for x in starts(width)]


def make_tiles(img: Image.Image, image_id: str, tile: int = MAX_SIDE, overlap: float = 0.15) -> List[Tile]:
    boxes = tile_boxes(img.width, img.height, tile, overlap)
    if len(boxes) == 1:
        return [Tile(name=f"{image_id}/full", image=img, box=boxes[0])]
    return [Tile(name=f"{image_id}/t{i:02d}", image=img.crop(b), box=b) for i, b in enumerate(boxes)]


def fit_for_model(img: Image.Image, max_side: int = MAX_SIDE) -> Image.Image:
    if max(img.size) <= max_side:
        return img
    scale = max_side / max(img.size)
    return img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)


def to_base64_jpeg(img: Image.Image, quality: int = 90) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality)
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def to_base64_png(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


def upscale_small(img: Image.Image, min_side: int = 224) -> Image.Image:
    """Tiny inputs (e.g. 24x40 thermal module crops) are upscaled with nearest-neighbour so
    the model sees pixels, not interpolation artefacts."""
    if min(img.size) >= min_side:
        return img
    scale = min_side / min(img.size)
    return img.resize((int(img.width * scale), int(img.height * scale)), Image.NEAREST)
