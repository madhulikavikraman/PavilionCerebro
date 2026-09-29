"""Stage D: deterministic work-queue scoring (docs/PRD.md section 8).

score = severity_weight[S] * criticality * consequence * urgency
Any S4 sorts above every non-S4 and is escalated same day. U is listed, never scored as S0.
Weights are the team's own assumption; the levers come from research note R05.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, List, Optional

from .schema import Finding

SEVERITY_WEIGHT = {"S0": 0.0, "S1": 1.0, "S2": 3.0, "S3": 9.0, "S4": 27.0}


def consequence_for(f: Finding, asset_meta: Optional[dict] = None) -> float:
    asset_meta = asset_meta or {}
    if f.asset_class == "pv_module":
        # estimated production loss multiplier supplied per asset (default 1)
        return float(asset_meta.get("production_loss_factor", 1.0))
    if f.asset_class in ("bridge_element", "steel_coating"):
        return 2.0 if "load_posting_review" in f.unified.flags or "section_loss" in f.unified.flags else 1.0
    if f.asset_class == "building_disaster":
        return float(asset_meta.get("occupancy_factor", 1.0))
    return 1.0


def urgency_for(found_on: Optional[str], today: Optional[date] = None) -> float:
    if not found_on:
        return 1.0
    today = today or date.today()
    try:
        d = date.fromisoformat(found_on)
    except ValueError:
        return 1.0
    days = max(0, (today - d).days)
    return min(2.0, 1.0 + days / 30.0)


def score(f: Finding, *, criticality: float = 1.0, asset_meta: Optional[dict] = None, found_on: Optional[str] = None, today: Optional[date] = None) -> Optional[float]:
    lvl = f.unified.level
    if lvl == "U":
        return None
    crit = min(3.0, max(1.0, float(criticality)))
    return SEVERITY_WEIGHT[lvl] * crit * consequence_for(f, asset_meta) * urgency_for(found_on, today)


def rank(findings: Iterable[Finding], *, criticality_by_image: Optional[dict] = None, asset_meta_by_image: Optional[dict] = None, found_on_by_image: Optional[dict] = None, today: Optional[date] = None) -> List[Finding]:
    criticality_by_image = criticality_by_image or {}
    asset_meta_by_image = asset_meta_by_image or {}
    found_on_by_image = found_on_by_image or {}
    scored: List[Finding] = []
    for f in findings:
        img = f.evidence.image_ids[0] if f.evidence.image_ids else ""
        f.queue_score = score(
            f,
            criticality=criticality_by_image.get(img, 1.0),
            asset_meta=asset_meta_by_image.get(img),
            found_on=found_on_by_image.get(img),
            today=today,
        )
        if f.unified.level == "S4":
            f.action.code = "escalate"
            f.action.sla_days = 0
        scored.append(f)

    def key(f: Finding):
        is_s4 = 0 if f.unified.level == "S4" else 1
        is_u = 1 if f.unified.level == "U" else 0
        return (is_s4, is_u, -(f.queue_score or 0.0), f.finding_id)

    scored.sort(key=key)
    for i, f in enumerate(scored, start=1):
        f.queue_rank = i
    return scored
