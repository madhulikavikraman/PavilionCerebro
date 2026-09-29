"""FR-13: few-shot exemplars for the grader, taken from the dev set only (D-007).

For an asset class, pick up to `k` dev images that carry a native grade, spread across
distinct grade values (one per value first, then fill), so the model sees what each
grade looks like on this dataset. Eval images are never used as exemplars.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional

from PIL import Image

from .grade import Exemplar
from .ingest import read_manifest
from .schema import ImageRecord


def candidates(records: List[ImageRecord], asset_class: str) -> List[ImageRecord]:
    """Dev records of this class with a usable native grade, stable order."""
    out = []
    for r in records:
        if r.asset_class != asset_class or r.split == "eval":
            continue
        grade = r.labels.get("grade_native")
        if grade is None or r.labels.get("grade_source") in (None, ""):
            continue
        out.append(r)
    return sorted(out, key=lambda r: r.image_id)


def select_exemplars(records: List[ImageRecord], asset_class: str, k: int = 3, exclude_ids: Optional[set] = None) -> List[ImageRecord]:
    """Round-robin across grade values so exemplars cover the scale, up to k (2 to 5 per PRD)."""
    k = max(0, min(5, k))
    exclude_ids = exclude_ids or set()
    by_grade: Dict[str, List[ImageRecord]] = {}
    for r in candidates(records, asset_class):
        if r.image_id in exclude_ids:
            continue
        by_grade.setdefault(str(r.labels["grade_native"]), []).append(r)
    chosen: List[ImageRecord] = []
    while len(chosen) < k and any(by_grade.values()):
        for grade in sorted(by_grade):
            if by_grade[grade] and len(chosen) < k:
                chosen.append(by_grade[grade].pop(0))
    return chosen


def to_exemplar(r: ImageRecord) -> Exemplar:
    img = Image.open(r.path)
    img.load()
    labels = r.labels
    note_bits = []
    if labels.get("classes_present"):
        note_bits.append("visible: " + ", ".join(labels["classes_present"]))
    if labels.get("source_class"):
        note_bits.append(f"dataset class: {labels['source_class']}")
    return Exemplar(image=img, native_value=str(labels["grade_native"]), note="; ".join(note_bits), image_id=r.image_id)


def exemplar_provider(dev_manifest: Path, k: int = 3) -> Callable[[str], List[Exemplar]]:
    """Returns a function asset_class -> exemplars, loading the dev manifest once."""
    records = read_manifest(Path(dev_manifest))
    cache: Dict[str, List[Exemplar]] = {}

    def provide(asset_class: str) -> List[Exemplar]:
        if asset_class not in cache:
            cache[asset_class] = [to_exemplar(r) for r in select_exemplars(records, asset_class, k)]
        return cache[asset_class]

    return provide
