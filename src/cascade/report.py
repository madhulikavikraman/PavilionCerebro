"""Per-run report: metrics dict for the UI's Reports tab and a stored `report.md` + `report.json`.

Every number is measured from the run's own files (`summary.json`, `gate.jsonl`, `calls.jsonl`,
`findings.json`). Accuracy numbers appear only when the run's images carry dataset labels, and then
come from `evalmetrics.eval_matrix`, the same definitions `eval/run_eval.py` scores with.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .evalmetrics import eval_matrix
from .pipeline import LEVELS, load_run
from .schema import ImageRecord

REPORT_FIELDS = ["run", "generated_at", "mode", "gate", "grader", "images", "gated", "routed", "unusable", "graded_images", "findings",
                 "S0", "S1", "S2", "S3", "S4", "U", "usd_total", "usd_per_image", "seconds_gate", "seconds_grade", "reviews"]


def run_metrics(out: Path, records: Optional[Dict[str, ImageRecord]] = None) -> dict:
    """Flat metrics for one run folder. Safe on partial runs; missing files count as zero."""
    out = Path(out)
    run = load_run(out)
    findings, gate_rows, calls, summary = run["findings"], run["gate"], run["calls"], run["summary"]
    cfg = summary.get("config", {}) if summary else {}
    levels = {lvl: 0 for lvl in LEVELS}
    for f in findings:
        levels[f.unified.level] = levels.get(f.unified.level, 0) + 1
    n_images = summary.get("images", len(gate_rows)) if summary else len(gate_rows)
    usd = round(sum(c["usd"] for c in calls), 4)
    m = {
        "run": out.name,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": "surge" if (out / "surge_counts.json").exists() else "inspect",
        "gate": cfg.get("gate", ""),
        "grader": cfg.get("grader", ""),
        "images": n_images,
        "gated": len(gate_rows),
        "routed": sum(1 for g in gate_rows if g["routed"]),
        "unusable": sum(1 for g in gate_rows if not g["usable"]),
        "graded_images": len({f.evidence.image_ids[0] for f in findings if f.evidence.image_ids}),
        "findings": len(findings),
        **levels,
        "usd_total": usd,
        "usd_per_image": round(usd / n_images, 5) if n_images else None,
        "seconds_gate": round(sum(c["seconds"] for c in calls if c["stage"] == "gate"), 1),
        "seconds_grade": round(sum(c["seconds"] for c in calls if c["stage"] == "grade"), 1),
        "reviews": sum(1 for f in findings if f.review.status != "pending"),
        "asset_classes": sorted({f.asset_class for f in findings}),
        "models": sorted({c["model"] for c in calls}),
    }
    ranked = sorted(findings, key=lambda x: x.queue_rank or 10**9)
    m["top_queue"] = [
        {"rank": f.queue_rank, "finding_id": f.finding_id, "image_id": f.evidence.image_ids[0] if f.evidence.image_ids else "",
         "level": f.unified.level, "native_value": f.native_scale.value, "standard": f.native_scale.standard,
         "action": f.action.code, "sla_days": f.action.sla_days, "score": f.queue_score}
        for f in ranked[:10]
    ]
    if records:
        m["eval"] = eval_matrix(records, gate_rows, [f.model_dump() for f in findings])
    return m


def _pct(x) -> str:
    return "n/a" if x is None else f"{100 * x:.1f}%"


def render_markdown(m: dict) -> str:
    lines: List[str] = [
        f"# Run report: {m['run']}",
        "",
        f"Generated {m['generated_at']}. Mode {m['mode']}, gate `{m['gate'] or '?'}`, grader `{m['grader'] or '?'}`. "
        "All numbers are measured from this run's call log and outputs on public datasets; do not extrapolate to field performance.",
        "",
        "## Throughput and cost",
        "",
        "| Images | Gated | Routed | Unusable | Graded images | Findings | USD total | USD / image | Gate s | Grade s |",
        "|---|---|---|---|---|---|---|---|---|---|",
        f"| {m['images']} | {m['gated']} | {m['routed']} | {m['unusable']} | {m['graded_images']} | {m['findings']} | {m['usd_total']} | {m['usd_per_image']} | {m['seconds_gate']} | {m['seconds_grade']} |",
        "",
        "## Findings by unified level",
        "",
        "| " + " | ".join(LEVELS) + " |",
        "|" + "---|" * len(LEVELS),
        "| " + " | ".join(str(m[lvl]) for lvl in LEVELS) + " |",
        "",
        f"Models: {', '.join(m['models']) or 'none'}. Reviewer decisions logged: {m['reviews']}.",
        "",
        "## Top of the work queue",
        "",
    ]
    if m["top_queue"]:
        lines += ["| Rank | Image | Level | Native | Action | SLA days | Score |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {t['rank']} | {t['image_id']} | {t['level']} | {t['native_value']} ({t['standard']}) | {t['action']} | {t['sla_days']} | {t['score']} |" for t in m["top_queue"]]
    else:
        lines.append("Empty queue.")
    ev = m.get("eval")
    if ev:
        g = ev["gate"]
        lines += ["", "## Gate against dataset labels", "",
                  f"n labelled {g['n']} (unlabelled {g['unlabelled']}): TP {g['tp']}, FP {g['fp']}, FN {g['fn']}, TN {g['tn']}; recall {_pct(g['recall'])}, precision {_pct(g['precision'])}."]
        if g["misses"]:
            lines.append(f"Missed damaged images: {', '.join(g['misses'])}.")
        for ac, gr in ev["grading"].items():
            lines += ["", f"## Grading matrix: {ac}", "", f"Truth: {gr['truth_source']}. n routed with truth {gr['n_routed_with_truth']}, assessed {gr['n_assessed']}, U rate {_pct(gr['u_rate'])}.", ""]
            if gr["n_assessed"]:
                lines += [f"Exact {_pct(gr['exact_match'])}, within one grade {_pct(gr['within_one_grade'])}, MAE {gr['mae']:.2f}, QWK {gr['qwk']:.2f}, over-graded {gr['over_graded']}, under-graded {gr['under_graded']}.", "",
                          "| truth \\ predicted | " + " | ".join(gr["labels"]) + " |", "|---|" + "---|" * len(gr["labels"])]
                lines += [f"| {lab} | " + " | ".join(str(v) for v in row) + " |" for lab, row in zip(gr["labels"], gr["matrix"])]
    return "\n".join(lines) + "\n"


def write_run_report(out: Path, records: Optional[Dict[str, ImageRecord]] = None) -> Path:
    """Write `<run>/report.md` and `<run>/report.json`; returns the markdown path."""
    out = Path(out)
    m = run_metrics(out, records)
    (out / "report.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    p = out / "report.md"
    p.write_text(render_markdown(m), encoding="utf-8")
    return p
