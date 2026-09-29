"""Pydantic models for the finding contract (docs/PRD.md appendix A) and pipeline records.

GraderOutput is exactly what a model must return; Finding adds evidence, review and
provenance that the pipeline fills in. Keep GraderOutput free of defaults so every
field is required in the JSON schema sent to the model (nullable where allowed).
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

AssetClass = Literal["bridge_element", "steel_coating", "pv_module", "building_disaster"]
Level = Literal["S0", "S1", "S2", "S3", "S4", "U"]
Standard = Literal["NBI-0-9", "MBEI-CS", "ISO-4628-3", "IEC-62446-3-CoA", "FEMA-PDA", "CorrosionCS"]
ActionCode = Literal["record", "monitor", "schedule", "prioritize", "escalate"]
Flag = Literal["fire_shock_pathway", "load_posting_review", "section_loss", "not_measurable"]

LEVEL_ORDER = {"S0": 0, "S1": 1, "S2": 2, "S3": 3, "S4": 4}


class GateOutput(BaseModel):
    """Stage A output. Two questions only."""

    usable: bool
    damage_present: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class NativeScale(BaseModel):
    standard: Standard
    value: str
    criteria_matched: List[str]


class Unified(BaseModel):
    level: Level
    uncertainty: str
    flags: List[Flag]


class Measurements(BaseModel):
    area_cm2: Optional[float]
    crack_width_mm: Optional[float]
    delta_t_k: Optional[float]
    percent_area_rusted: Optional[float]
    section_loss_pct: Optional[float]
    confidence: float = Field(ge=0.0, le=1.0)


class Action(BaseModel):
    code: ActionCode
    sla_days: Optional[int]
    basis: str


class GraderOutput(BaseModel):
    """What the heavy grader returns for one crop. All fields required."""

    defect_type: str
    native_scale: NativeScale
    unified: Unified
    measurements: Measurements
    action: Action
    justification: str


class Evidence(BaseModel):
    image_ids: List[str] = []
    bbox: List[int] = []  # x0, y0, x1, y1 in original image pixels
    tile: Optional[str] = None
    gsd_mm_per_px: Optional[float] = None
    irradiance_wm2: Optional[float] = None


class Review(BaseModel):
    status: Literal["pending", "accepted", "overridden", "marked_u"] = "pending"
    reviewer: Optional[str] = None
    reviewed_at: Optional[str] = None
    prior_level: Optional[Level] = None


class Finding(BaseModel):
    finding_id: str
    asset_class: AssetClass
    defect_type: str
    native_scale: NativeScale
    unified: Unified
    measurements: Measurements
    action: Action
    justification: str
    evidence: Evidence
    review: Review = Review()
    model: str = ""
    usd: float = 0.0
    seconds: float = 0.0
    queue_score: Optional[float] = None
    queue_rank: Optional[int] = None

    @classmethod
    def from_grader(
        cls,
        out: GraderOutput,
        *,
        finding_id: str,
        asset_class: AssetClass,
        evidence: Evidence,
        model: str,
        usd: float,
        seconds: float,
    ) -> "Finding":
        return cls(
            finding_id=finding_id,
            asset_class=asset_class,
            defect_type=out.defect_type,
            native_scale=out.native_scale,
            unified=out.unified,
            measurements=out.measurements,
            action=out.action,
            justification=out.justification,
            evidence=evidence,
            model=model,
            usd=usd,
            seconds=seconds,
        )


def unassessable_finding(
    *,
    finding_id: str,
    asset_class: AssetClass,
    standard: Standard,
    evidence: Evidence,
    reason: str,
    model: str = "",
) -> Finding:
    """A U finding for images that are unusable, refused, or otherwise not gradable."""

    return Finding(
        finding_id=finding_id,
        asset_class=asset_class,
        defect_type="not_assessable",
        native_scale=NativeScale(standard=standard, value="U", criteria_matched=[]),
        unified=Unified(level="U", uncertainty="+/-1", flags=["not_measurable"]),
        measurements=Measurements(
            area_cm2=None,
            crack_width_mm=None,
            delta_t_k=None,
            percent_area_rusted=None,
            section_loss_pct=None,
            confidence=0.0,
        ),
        action=Action(code="monitor", sla_days=None, basis=f"Not assessable: {reason}. Re-image or use other NDT."),
        justification=reason,
        evidence=evidence,
        model=model,
    )


class ImageRecord(BaseModel):
    """One row of a run or eval manifest."""

    image_id: str
    path: str
    sha256: str
    width: int
    height: int
    asset_class: AssetClass
    gsd_mm_per_px: Optional[float] = None
    irradiance_wm2: Optional[float] = None
    captured_on: Optional[str] = None  # YYYY-MM-DD
    source_dataset: str = ""
    split: str = ""
    labels: dict = {}


class GateRecord(BaseModel):
    image_id: str
    usable: bool
    damage_present: bool
    confidence: float
    reason: str
    routed: bool
    model: str
    seconds: float
    usd: float
