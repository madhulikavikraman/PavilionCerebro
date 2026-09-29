"""FR-20 surge mode: triage-first batch run over post-disaster imagery with the FEMA PDA rubric.

Same cascade, different posture: every image is treated as `building_disaster`, graded on
the whole downscaled frame (no tiles, one call per image), and the output is a map-free
ranked list plus counts per FEMA class, per unified level, and the number of images the
model could not assess (U). Nothing is defaulted to Undamaged: Inaccessible and refusals
stay U.

Usage:
  python -m cascade.surge --folder data/raw/rescuenet/images --out runs/surge01 --gate local --grader claude --limit 40
  python -m cascade.surge --manifest data/dev/manifest.jsonl --out runs/surge_dev --grader local
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Callable, List, Optional

from dotenv import load_dotenv

from .grade import load_rubric
from .ingest import ingest_folder, read_manifest
from .pipeline import LEVELS, Progress, RunConfig, load_run, run_cascade
from .schema import Finding, ImageRecord

ROOT = Path(__file__).resolve().parents[2]
FEMA_CLASSES = load_rubric("building_disaster")["allowed_values"]


def surge_records(folder: Optional[Path] = None, manifest: Optional[Path] = None, limit: int = 0) -> List[ImageRecord]:
    if manifest:
        records = [r for r in read_manifest(Path(manifest)) if r.asset_class == "building_disaster"]
    elif folder:
        records = ingest_folder(Path(folder), asset_class="building_disaster", source_dataset=Path(folder).name, split="surge", id_prefix="surge")
    else:
        raise ValueError("surge needs --folder or --manifest")
    return records[:limit] if limit else records


def surge_counts(findings: List[Finding]) -> dict:
    """Counts per FEMA class and unified level, U count, mean confidence, ranked list."""
    by_class = Counter(f.native_scale.value for f in findings)
    by_level = Counter(f.unified.level for f in findings)
    assessed = [f for f in findings if f.unified.level != "U"]
    conf = [f.measurements.confidence for f in assessed]
    ranked = sorted(findings, key=lambda f: (f.queue_rank if f.queue_rank is not None else 10**9))
    by_fema = {c: by_class.get(c, 0) for c in FEMA_CLASSES}
    by_fema.update({k: v for k, v in by_class.items() if k not in FEMA_CLASSES})
    return {
        "n_findings": len(findings),
        "n_images": len({f.evidence.image_ids[0] for f in findings if f.evidence.image_ids}),
        "by_fema_class": by_fema,
        "by_level": {lvl: by_level.get(lvl, 0) for lvl in LEVELS},
        "u_count": by_level.get("U", 0),
        "u_rate": (by_level.get("U", 0) / len(findings)) if findings else None,
        "mean_confidence": (sum(conf) / len(conf)) if conf else None,
        "ranked": [
            {
                "rank": f.queue_rank,
                "finding_id": f.finding_id,
                "image_id": f.evidence.image_ids[0] if f.evidence.image_ids else "",
                "native_value": f.native_scale.value,
                "level": f.unified.level,
                "confidence": f.measurements.confidence,
                "action": f.action.code,
                "sla_days": f.action.sla_days,
                "justification": f.justification,
            }
            for f in ranked
        ],
    }


def write_surge_report(counts: dict, summary: dict, out: Path) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "surge_counts.json").write_text(json.dumps({k: v for k, v in counts.items() if k != "summary"}, indent=1), encoding="utf-8")
    lines = [
        "# Surge triage report",
        "",
        f"Images: {summary.get('images', counts['n_images'])}. Routed to grader: {summary.get('routed_to_grader', 'n/a')}. Findings: {counts['n_findings']}. Cost: ${summary.get('usd_total', 0)} total, {summary.get('seconds_total', 0)} s of model time.",
        "",
        "Counts are model output on UAV imagery, not a field damage assessment. Every U row needs a human look or a re-image.",
        "",
        "| FEMA PDA class | Count |",
        "|---|---|",
    ]
    lines += [f"| {c} | {n} |" for c, n in counts["by_fema_class"].items()]
    lines += ["", "| Unified level | Count |", "|---|---|"]
    lines += [f"| {lvl} | {n} |" for lvl, n in counts["by_level"].items()]
    mc = counts["mean_confidence"]
    conf_line = f"Unassessable (U): {counts['u_count']}." + (f" Mean grader confidence on assessed rows: {mc:.2f}." if mc is not None else "")
    lines += ["", conf_line, "", "## Ranked list (S4 first, then by score)", "", "| Rank | Image | FEMA class | Level | Confidence | Action |", "|---|---|---|---|---|---|"]
    for r in counts["ranked"]:
        lines.append(f"| {r['rank']} | {r['image_id']} | {r['native_value']} | {r['level']} | {r['confidence']:.2f} | {r['action']} |")
    path = out / "surge_report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_surge(
    out: Path,
    *,
    folder: Optional[Path] = None,
    manifest: Optional[Path] = None,
    gate: str = "local",
    grader: str = "claude",
    limit: int = 0,
    gate_min_conf: float = 0.7,
    progress: Optional[Callable[[Progress], None]] = None,
    **pipeline_kwargs,
) -> dict:
    """Run the cascade in surge posture and write the surge report. Returns the counts dict."""
    records = surge_records(folder, manifest, limit)
    cfg = RunConfig(gate=gate, grader=grader, tiles=False, gate_min_conf=gate_min_conf)
    summary = run_cascade(records, Path(out), cfg, progress=progress, **pipeline_kwargs)
    findings = load_run(Path(out))["findings"]
    counts = surge_counts(findings)
    write_surge_report(counts, summary, Path(out))
    counts["summary"] = summary
    return counts


def main(argv=None) -> int:
    load_dotenv(ROOT / ".env")
    ap = argparse.ArgumentParser(prog="python -m cascade.surge", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--folder", help="folder of post-event JPEG/PNG images")
    src.add_argument("--manifest", help="manifest; only building_disaster rows are used")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate", choices=["local", "claude", "none"], default="local")
    ap.add_argument("--grader", choices=["claude", "local", "none"], default="claude")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--gate-min-conf", type=float, default=0.7)
    args = ap.parse_args(argv)
    counts = run_surge(
        Path(args.out),
        folder=Path(args.folder) if args.folder else None,
        manifest=Path(args.manifest) if args.manifest else None,
        gate=args.gate,
        grader=args.grader,
        limit=args.limit,
        gate_min_conf=args.gate_min_conf,
    )
    print(json.dumps({k: v for k, v in counts.items() if k != "ranked"}, indent=1))
    print(f"report: {Path(args.out) / 'surge_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
