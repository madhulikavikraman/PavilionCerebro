"""Exports: queue CSV and findings JSON. Bridge rows carry element / condition-state columns
so they can be pasted into a state system entry form."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List

from .schema import Finding

QUEUE_COLUMNS = [
    "queue_rank",
    "queue_score",
    "finding_id",
    "image_id",
    "asset_class",
    "defect_type",
    "standard",
    "native_value",
    "unified_level",
    "uncertainty",
    "flags",
    "action_code",
    "sla_days",
    "action_basis",
    "confidence",
    "criteria_matched",
    "justification",
    "review_status",
    "reviewer",
    "prior_level",
    "bbox",
    "tile",
    "model",
    "usd",
    "seconds",
]


def finding_row(f: Finding) -> dict:
    return {
        "queue_rank": f.queue_rank,
        "queue_score": f.queue_score,
        "finding_id": f.finding_id,
        "image_id": f.evidence.image_ids[0] if f.evidence.image_ids else "",
        "asset_class": f.asset_class,
        "defect_type": f.defect_type,
        "standard": f.native_scale.standard,
        "native_value": f.native_scale.value,
        "unified_level": f.unified.level,
        "uncertainty": f.unified.uncertainty,
        "flags": ";".join(f.unified.flags),
        "action_code": f.action.code,
        "sla_days": f.action.sla_days,
        "action_basis": f.action.basis,
        "confidence": f.measurements.confidence,
        "criteria_matched": " | ".join(f.native_scale.criteria_matched),
        "justification": f.justification,
        "review_status": f.review.status,
        "reviewer": f.review.reviewer,
        "prior_level": f.review.prior_level,
        "bbox": ",".join(str(v) for v in f.evidence.bbox),
        "tile": f.evidence.tile,
        "model": f.model,
        "usd": round(f.usd, 6),
        "seconds": round(f.seconds, 3),
    }


def write_queue_csv(findings: Iterable[Finding], path: Path) -> List[dict]:
    rows = [finding_row(f) for f in findings]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=QUEUE_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return rows


BRIDGE_COLUMNS = [
    "image_id",
    "finding_id",
    "element",
    "defect",
    "standard",
    "condition_state",
    "quantity",
    "unit",
    "unified_level",
    "flags",
    "criteria_matched",
    "confidence",
    "review_status",
    "reviewer",
    "prior_level",
    "justification",
]


def bridge_row(f: Finding) -> dict:
    """One SNBI-style entry row (FR-17). Quantity is only filled from a measured area; a
    condition state with no measurable quantity leaves quantity blank rather than guessing."""
    area = f.measurements.area_cm2
    return {
        "image_id": f.evidence.image_ids[0] if f.evidence.image_ids else "",
        "finding_id": f.finding_id,
        "element": f.defect_type.split(" (")[-1].rstrip(")") if " (" in f.defect_type else "",
        "defect": f.defect_type,
        "standard": f.native_scale.standard,
        "condition_state": f.native_scale.value,
        "quantity": round(area / 10_000, 4) if area is not None else "",
        "unit": "m2" if area is not None else "",
        "unified_level": f.unified.level,
        "flags": ";".join(f.unified.flags),
        "criteria_matched": " | ".join(f.native_scale.criteria_matched),
        "confidence": f.measurements.confidence,
        "review_status": f.review.status,
        "reviewer": f.review.reviewer,
        "prior_level": f.review.prior_level,
        "justification": f.justification,
    }


def write_bridge_csv(findings: Iterable[Finding], path: Path) -> List[dict]:
    rows = [bridge_row(f) for f in findings if f.asset_class == "bridge_element"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=BRIDGE_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return rows


def write_findings_json(findings: Iterable[Finding], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([f.model_dump() for f in findings], indent=1), encoding="utf-8")
