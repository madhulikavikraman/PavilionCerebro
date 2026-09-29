"""The cascade as a reusable function: gate -> crop -> grade -> prioritize -> export.

The CLI (`cascade.run`), surge mode (`cascade.surge`) and the Streamlit app all call
`run_cascade`. It is resumable: gate rows and findings are appended to JSONL files as
they are produced, and a rerun over the same output folder skips finished images.
A `progress` callback receives a `Progress` snapshot after every image so a UI can
tick stage counters, cost and latency live.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from PIL import Image

from .costlog import CallLog
from .crop import make_tiles
from .export import write_bridge_csv, write_findings_json, write_queue_csv
from .gate import run_gate
from .grade import Exemplar, grade_image, load_rubric
from .prioritize import rank
from .schema import Evidence, Finding, GateRecord, ImageRecord, unassessable_finding

ExemplarProvider = Callable[[str], List[Exemplar]]
LEVELS = ("S0", "S1", "S2", "S3", "S4", "U")


@dataclass
class Progress:
    """Live counters for one run. Mutated in place and handed to the progress callback."""

    images: int = 0
    gated: int = 0
    routed: int = 0
    unusable: int = 0
    graded: int = 0
    findings: int = 0
    usd: float = 0.0
    seconds_gate: float = 0.0
    seconds_grade: float = 0.0
    current_image: str = ""
    stage: str = "idle"
    levels: Dict[str, int] = field(default_factory=lambda: {k: 0 for k in LEVELS})

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class RunConfig:
    gate: str = "local"  # local | claude | none
    grader: str = "claude"  # claude | local | none
    tiles: bool = False
    gate_min_conf: float = 0.7
    rubric_file: Optional[str] = None  # bridge rubric override (bridge_nbi.json); other classes keep their default
    limit: int = 0
    # Asset classes whose images go to the grader regardless of the gate verdict. The local gate routed 0 of 12
    # thermal PV crops on the dev set (eval/reports/dev_gate02.md), so pv_module is forced by default. The gate
    # still runs and its verdict is kept in gate.jsonl; only `routed` is overridden and the reason says so.
    force_route_classes: Tuple[str, ...] = ("pv_module",)


def _read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _append(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text + "\n")


def _count(values) -> dict:
    out: dict = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def load_run(out: Path) -> dict:
    """Read whatever a finished or partial run has written, for the UI and eval."""
    out = Path(out)
    findings_json = out / "findings.json"
    if findings_json.exists():
        findings = [Finding.model_validate(f) for f in json.loads(findings_json.read_text(encoding="utf-8"))]
    else:
        findings = [Finding.model_validate(f) for f in _read_jsonl(out / "findings.jsonl")]
    summary_path = out / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    return {"gate": _read_jsonl(out / "gate.jsonl"), "findings": findings, "calls": _read_jsonl(out / "calls.jsonl"), "summary": summary}


def save_findings(findings: List[Finding], out: Path, records: Optional[List[ImageRecord]] = None) -> List[Finding]:
    """Re-rank and rewrite findings.json, queue.csv and the bridge CSV (used after a review action)."""
    out = Path(out)
    found_on = {r.image_id: r.captured_on for r in records} if records else {}
    ranked = rank(findings, found_on_by_image=found_on)
    write_findings_json(ranked, out / "findings.json")
    write_queue_csv(ranked, out / "queue.csv")
    if any(f.asset_class == "bridge_element" for f in ranked):
        write_bridge_csv(ranked, out / "bridge_entry.csv")
    return ranked


def summarize(records: List[ImageRecord], gate_rows: List[dict], ranked: List[Finding], log: CallLog, cfg: RunConfig) -> dict:
    routed = sum(1 for r in gate_rows if r["routed"])
    usd_total = sum(r["usd"] for r in log.rows)
    return {
        "images": len(records),
        "gated": len(gate_rows),
        "routed_to_grader": routed,
        "routing_fraction": (routed / len(gate_rows)) if gate_rows else None,
        "unusable": sum(1 for r in gate_rows if not r["usable"]),
        "findings": len(ranked),
        "levels": {lvl: sum(1 for f in ranked if f.unified.level == lvl) for lvl in LEVELS},
        "native_values": _count(f.native_scale.value for f in ranked),
        "asset_classes": _count(r.asset_class for r in records),
        "config": asdict(cfg),
        "cost_by_stage": log.totals(),
        "usd_total": round(usd_total, 4),
        "usd_per_image": round(usd_total / len(records), 5) if records else None,
        "seconds_total": round(sum(r["seconds"] for r in log.rows), 1),
    }


def run_cascade(
    records: List[ImageRecord],
    out: Path,
    cfg: Optional[RunConfig] = None,
    *,
    exemplars: Optional[ExemplarProvider] = None,
    progress: Optional[Callable[[Progress], None]] = None,
    log: Optional[CallLog] = None,
    gate_fn=run_gate,
    grade_fn=grade_image,
) -> dict:
    """Run the cascade over `records`, writing into `out`. Returns the summary dict.

    `gate_fn` and `grade_fn` exist so tests can substitute fake backends without a model.
    """
    cfg = cfg or RunConfig()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    log = log or CallLog(path=out / "calls.jsonl")
    if cfg.limit:
        records = records[: cfg.limit]

    gate_path, findings_path = out / "gate.jsonl", out / "findings.jsonl"
    done_gate = {row["image_id"]: row for row in _read_jsonl(gate_path)}
    gate_rows: List[dict] = list(done_gate.values())
    findings: List[Finding] = [Finding.model_validate(f) for f in _read_jsonl(findings_path)]
    graded_images = {f.evidence.image_ids[0] for f in findings if f.evidence.image_ids}

    prog = Progress(
        images=len(records),
        gated=len(gate_rows),
        routed=sum(1 for r in gate_rows if r["routed"]),
        unusable=sum(1 for r in gate_rows if not r["usable"]),
        graded=len(graded_images),
        findings=len(findings),
    )
    for f in findings:
        prog.levels[f.unified.level] = prog.levels.get(f.unified.level, 0) + 1
    rubric_cache: dict = {}
    exemplar_cache: dict = {}

    def tick(stage: str, image_id: str = "") -> None:
        prog.stage, prog.current_image = stage, image_id
        prog.usd = round(sum(r["usd"] for r in log.rows), 5)
        prog.seconds_gate = round(sum(r["seconds"] for r in log.rows if r["stage"] == "gate"), 1)
        prog.seconds_grade = round(sum(r["seconds"] for r in log.rows if r["stage"] == "grade"), 1)
        if progress:
            progress(prog)

    def add_finding(f: Finding) -> None:
        findings.append(f)
        prog.findings += 1
        prog.levels[f.unified.level] = prog.levels.get(f.unified.level, 0) + 1
        _append(findings_path, f.model_dump_json())

    def rubric_for(asset_class: str) -> dict:
        if asset_class not in rubric_cache:
            override = cfg.rubric_file if asset_class == "bridge_element" else None
            rubric_cache[asset_class] = load_rubric(asset_class, override)
        return rubric_cache[asset_class]

    for rec in records:
        tick("gate", rec.image_id)
        img: Optional[Image.Image] = None
        if rec.image_id in done_gate:
            g = GateRecord.model_validate(done_gate[rec.image_id])
            if not g.routed or cfg.grader == "none" or rec.image_id in graded_images:
                continue
        else:
            img = Image.open(rec.path)
            img.load()
            g = gate_fn(img, rec.image_id, backend=cfg.gate, log=log, no_damage_min_conf=cfg.gate_min_conf)
            if rec.asset_class in cfg.force_route_classes and not g.routed:
                g = g.model_copy(update={"routed": True, "reason": f"{g.reason} [forced: asset class {rec.asset_class}]"})
            gate_rows.append(g.model_dump())
            _append(gate_path, json.dumps(g.model_dump()))
            prog.gated += 1
            prog.routed += int(g.routed)
            prog.unusable += int(not g.usable)
        if not g.routed or cfg.grader == "none":
            tick("gate", rec.image_id)
            continue
        if img is None:
            img = Image.open(rec.path)
            img.load()
        tick("grade", rec.image_id)
        rubric = rubric_for(rec.asset_class)
        full_box = [0, 0, rec.width, rec.height]
        if not g.usable:
            add_finding(
                unassessable_finding(
                    finding_id=f"{rec.image_id}/full",
                    asset_class=rec.asset_class,
                    standard=rubric["standard"],
                    evidence=Evidence(image_ids=[rec.image_id], bbox=full_box, tile="full", gsd_mm_per_px=rec.gsd_mm_per_px, irradiance_wm2=rec.irradiance_wm2),
                    reason=f"gate marked image unusable: {g.reason}",
                    model=g.model,
                )
            )
            prog.graded += 1
            graded_images.add(rec.image_id)
            tick("grade", rec.image_id)
            continue
        ex_list: List[Exemplar] = []
        if exemplars is not None:
            if rec.asset_class not in exemplar_cache:
                exemplar_cache[rec.asset_class] = exemplars(rec.asset_class)
            # never show an image its own label
            ex_list = [e for e in exemplar_cache[rec.asset_class] if e.image_id != rec.image_id]
        metadata = {
            "asset_class": rec.asset_class,
            "gsd_mm_per_px": rec.gsd_mm_per_px,
            "irradiance_wm2": rec.irradiance_wm2,
            "captured_on": rec.captured_on,
            "image_size": f"{rec.width}x{rec.height}",
        }
        tiles = make_tiles(img, rec.image_id) if cfg.tiles else []
        if len(tiles) <= 1:
            targets = [("full", full_box, img)]
        else:
            targets = [(t.name.split("/")[-1], list(t.box), t.image) for t in tiles]
        for tile_name, box, tile_img in targets:
            ev = Evidence(image_ids=[rec.image_id], bbox=box, tile=tile_name, gsd_mm_per_px=rec.gsd_mm_per_px, irradiance_wm2=rec.irradiance_wm2)
            fnd = grade_fn(
                tile_img,
                finding_id=f"{rec.image_id}/{tile_name}",
                image_id=rec.image_id,
                asset_class=rec.asset_class,
                backend=cfg.grader,
                rubric=rubric,
                metadata=metadata,
                exemplars=ex_list or None,
                evidence=ev,
                log=log,
            )
            add_finding(fnd)
        prog.graded += 1
        graded_images.add(rec.image_id)
        tick("grade", rec.image_id)

    tick("prioritize")
    ranked = save_findings(findings, out, records)
    summary = summarize(records, gate_rows, ranked, log, cfg)
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    tick("done")
    return summary
