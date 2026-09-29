"""Stage 0: folder or manifest in, run manifest out.

Reads JPEG/PNG files, hashes them, records dimensions and EXIF date, and merges an
optional metadata sidecar (JSON keyed by filename) carrying asset_class, gsd_mm_per_px,
irradiance_wm2, captured_on. Missing values stay null; nothing is defaulted.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Iterator, Optional

from PIL import ExifTags, Image

from .schema import AssetClass, ImageRecord

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def exif_date(img: Image.Image) -> Optional[str]:
    try:
        exif = img.getexif()
    except Exception:
        return None
    if not exif:
        return None
    for tag_id, value in exif.items():
        if ExifTags.TAGS.get(tag_id) in ("DateTimeOriginal", "DateTime") and isinstance(value, str):
            # EXIF format: YYYY:MM:DD HH:MM:SS
            d = value.split(" ")[0].replace(":", "-")
            if len(d) == 10:
                return d
    return None


def iter_images(folder: Path) -> Iterator[Path]:
    for p in sorted(folder.rglob("*")):
        if p.suffix.lower() in IMAGE_EXTS and p.is_file():
            yield p


def ingest_folder(
    folder: Path,
    *,
    asset_class: AssetClass,
    sidecar: Optional[Path] = None,
    source_dataset: str = "",
    split: str = "",
    id_prefix: str = "img",
) -> list[ImageRecord]:
    meta: dict = {}
    if sidecar and sidecar.exists():
        meta = json.loads(sidecar.read_text(encoding="utf-8"))
    records: list[ImageRecord] = []
    for i, p in enumerate(iter_images(folder)):
        with Image.open(p) as img:
            w, h = img.size
            captured = exif_date(img)
        m = meta.get(p.name, {})
        records.append(
            ImageRecord(
                image_id=m.get("image_id", f"{id_prefix}_{i:05d}"),
                path=str(p),
                sha256=sha256_of(p),
                width=w,
                height=h,
                asset_class=m.get("asset_class", asset_class),
                gsd_mm_per_px=m.get("gsd_mm_per_px"),
                irradiance_wm2=m.get("irradiance_wm2"),
                captured_on=m.get("captured_on", captured),
                source_dataset=source_dataset,
                split=split,
                labels=m.get("labels", {}),
            )
        )
    return records


def write_manifest(records: Iterable[ImageRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")


def read_manifest(path: Path) -> list[ImageRecord]:
    out = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(ImageRecord.model_validate_json(line))
    return out
