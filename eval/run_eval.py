"""Score a cascade run against the frozen eval manifest (docs/decisions.md D-007).

Usage: python eval/run_eval.py --manifest data/eval_v1/manifest.jsonl --run runs/eval_v1_run1 --name eval_v1_run1
Reads <run>/gate.jsonl, <run>/findings.json, <run>/calls.jsonl. Writes eval/reports/<name>.md and .json.
Every headline number carries n and a 95 percent bootstrap CI (1000 resamples, seed 0).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cascade.ingest import read_manifest  # noqa: E402

IR = json.loads((ROOT / "eval/rubrics/ir_solar_class_map.json").read_text(encoding="utf-8"))
RN = json.loads((ROOT / "eval/rubrics/rescuenet_class_map.json").read_text(encoding="utf-8"))
CORR_ORD = json.loads((ROOT / "eval/rubrics/dacl10k_classes.json").read_text(encoding="utf-8"))["corrosion_ordinal"]


def bootstrap(values, stat, n_boot=1000, seed=0):
    values = list(values)
    if not values:
        return None, (None, None)
    rng = np.random.default_rng(seed)
    point = stat(values)
    boots = []
    n = len(values)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        boots.append(stat([values[i] for i in idx]))
    return point, (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))


def prf(pairs):
    tp = sum(1 for t, p in pairs if t and p)
    fp = sum(1 for t, p in pairs if (not t) and p)
    fn = sum(1 for t, p in pairs if t and (not p))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return prec, rec, f1


def qwk(truth, pred, k):
    """Quadratic weighted kappa."""
    O = np.zeros((k, k))
    for t, p in zip(truth, pred):
        O[t, p] += 1
    W = np.array([[(i - j) ** 2 / (k - 1) ** 2 for j in range(k)] for i in range(k)])
    E = np.outer(O.sum(1), O.sum(0)) / max(1, O.sum())
    denom = (W * E).sum()
    return 1.0 - (W * O).sum() / denom if denom else 0.0


def predicted_ordinal(asset_class, findings):
    """Worst (max) predicted ordinal across an image's findings; None if all U or unmappable."""
    vals = []
    for f in findings:
        nv = f["native_scale"]["value"]
        if f["unified"]["level"] == "U":
            continue
        if asset_class == "steel_coating":
            o = CORR_ORD.get(nv)
        elif asset_class == "pv_module":
            o = IR["ordinal"].get(nv)
        elif asset_class == "building_disaster":
            cls = RN["predicted_to_class"].get(nv)
            o = RN["ordinal"].get(cls) if cls else None
        else:
            o = None
        if o is not None:
            vals.append(o)
    return max(vals) if vals else None


def truth_ordinal(rec):
    ac, lab = rec.asset_class, rec.labels
    if ac == "steel_coating":
        return CORR_ORD.get(lab.get("grade_native"))
    if ac == "pv_module":
        return IR["ordinal"].get(lab.get("grade_native"))
    if ac == "building_disaster":
        return RN["ordinal"].get(lab.get("source_class"))
    if ac == "bridge_element" and lab.get("grade_source") == "team-graded" and lab.get("grade_native") is not None:
        return int(lab["grade_native"]) - 1
    return None


def k_for(asset_class):
    return {"steel_coating": 4, "pv_module": 3, "building_disaster": 3, "bridge_element": 4}[asset_class]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    run = Path(args.run)
    records = {r.image_id: r for r in read_manifest(Path(args.manifest))}
    gate = {}
    gp = run / "gate.jsonl"
    if gp.exists():
        for line in gp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                g = json.loads(line)
                gate[g["image_id"]] = g
    findings_by_img = defaultdict(list)
    fp = run / "findings.json"
    if fp.exists():
        for f in json.loads(fp.read_text(encoding="utf-8")):
            for iid in f["evidence"]["image_ids"]:
                findings_by_img[iid].append(f)
    calls = []
    cp = run / "calls.jsonl"
    if cp.exists():
        calls = [json.loads(line) for line in cp.read_text(encoding="utf-8").splitlines() if line.strip()]

    scored_ids = [i for i in records if i in gate]
    report = {"name": args.name, "n_images_in_run": len(scored_ids), "n_manifest": len(records)}

    pairs = [(bool(records[i].labels.get("damage_present")), bool(gate[i]["routed"])) for i in scored_ids]
    if pairs:
        p, (plo, phi) = bootstrap(pairs, lambda v: prf(v)[0])
        r, (rlo, rhi) = bootstrap(pairs, lambda v: prf(v)[1])
        f, (flo, fhi) = bootstrap(pairs, lambda v: prf(v)[2])
        report["gate"] = {
            "n": len(pairs),
            "precision": p, "precision_ci": [plo, phi],
            "recall": r, "recall_ci": [rlo, rhi],
            "f1": f, "f1_ci": [flo, fhi],
            "routing_fraction": sum(1 for _, x in pairs if x) / len(pairs),
            "unusable": sum(1 for i in scored_ids if not gate[i]["usable"]),
            "misses": [i for i in scored_ids if records[i].labels.get("damage_present") and not gate[i]["routed"]],
        }
        by_ds = defaultdict(list)
        for i in scored_ids:
            by_ds[records[i].source_dataset].append((bool(records[i].labels.get("damage_present")), bool(gate[i]["routed"])))
        report["gate"]["per_dataset"] = {ds: {"n": len(v), "precision": prf(v)[0], "recall": prf(v)[1], "routed": sum(1 for _, x in v if x)} for ds, v in by_ds.items()}

    grading = {}
    by_ac = defaultdict(list)
    for i in scored_ids:
        t = truth_ordinal(records[i])
        if t is None or not gate[i]["routed"]:
            continue
        pr = predicted_ordinal(records[i].asset_class, findings_by_img.get(i, []))
        by_ac[records[i].asset_class].append((t, pr, i))
    for ac, items in by_ac.items():
        assessed = [(t, p) for t, p, _ in items if p is not None]
        u_rate = 1 - len(assessed) / len(items) if items else None
        if not assessed:
            grading[ac] = {"n_routed_with_truth": len(items), "u_rate": u_rate}
            continue
        exact, exact_ci = bootstrap(assessed, lambda v: sum(1 for t, p in v if t == p) / len(v))
        within1, within1_ci = bootstrap(assessed, lambda v: sum(1 for t, p in v if abs(t - p) <= 1) / len(v))
        mae = statistics.mean(abs(t - p) for t, p in assessed)
        kappa = qwk([t for t, _ in assessed], [p for _, p in assessed], k_for(ac))
        conf = defaultdict(int)
        for t, p in assessed:
            conf[f"truth{t}->pred{p}"] += 1
        grading[ac] = {
            "n_routed_with_truth": len(items), "n_assessed": len(assessed), "u_rate": u_rate,
            "exact_match": exact, "exact_ci": list(exact_ci),
            "within_one_grade": within1, "within_one_ci": list(within1_ci),
            "mae": mae, "quadratic_weighted_kappa": kappa,
            "confusion": dict(sorted(conf.items())),
            "over_graded": sum(1 for t, p in assessed if p > t),
            "under_graded": sum(1 for t, p in assessed if p < t),
        }
    report["grading"] = grading

    ops = {}
    by_stage = defaultdict(list)
    for c in calls:
        by_stage[c["stage"]].append(c)
    for st, rows in by_stage.items():
        ops[st] = {"calls": len(rows), "median_seconds": statistics.median(r["seconds"] for r in rows), "usd_total": round(sum(r["usd"] for r in rows), 4), "models": sorted({r["model"] for r in rows})}
    ops["usd_per_image"] = round(sum(c["usd"] for c in calls) / len(scored_ids), 5) if scored_ids else None
    report["ops"] = ops

    out_json = ROOT / "eval/reports" / f"{args.name}.json"
    out_md = ROOT / "eval/reports" / f"{args.name}.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=1), encoding="utf-8")

    def pct(x):
        return "n/a" if x is None else f"{100 * x:.1f}%"

    lines = [f"# Eval report: {args.name}", "", f"Images scored: {len(scored_ids)} of {len(records)} in manifest. All CIs are 95 percent bootstrap (1000 resamples). Public datasets, not customer imagery; do not extrapolate to field performance.", ""]
    if "gate" in report:
        g = report["gate"]
        lines += ["## Gate (stage A): damage_present, positive = routed to grader", "", "| Metric | Value | 95% CI | n |", "|---|---|---|---|",
                  f"| Recall (headline) | {pct(g['recall'])} | {pct(g['recall_ci'][0])} to {pct(g['recall_ci'][1])} | {g['n']} |",
                  f"| Precision | {pct(g['precision'])} | {pct(g['precision_ci'][0])} to {pct(g['precision_ci'][1])} | {g['n']} |",
                  f"| F1 | {pct(g['f1'])} | {pct(g['f1_ci'][0])} to {pct(g['f1_ci'][1])} | {g['n']} |",
                  f"| Routing fraction | {pct(g['routing_fraction'])} | | {g['n']} |",
                  f"| Marked unusable | {g['unusable']} | | |", "", "Per dataset:", "", "| Dataset | n | Recall | Precision | Routed |", "|---|---|---|---|---|"]
        for ds, v in g["per_dataset"].items():
            lines.append(f"| {ds} | {v['n']} | {pct(v['recall'])} | {pct(v['precision'])} | {v['routed']} |")
        if g["misses"]:
            lines += ["", f"Missed damaged images ({len(g['misses'])}): " + ", ".join(g["misses"][:20])]
        lines.append("")
    lines += ["## Grading (stage C), per asset class, worst finding per image vs dataset truth", ""]
    for ac, v in grading.items():
        lines += [f"### {ac}", ""]
        if "exact_match" not in v:
            lines += [f"n routed with truth: {v['n_routed_with_truth']}; U rate {pct(v['u_rate'])}; nothing assessed.", ""]
            continue
        lines += ["| Metric | Value | 95% CI | n |", "|---|---|---|---|",
                  f"| Within one grade | {pct(v['within_one_grade'])} | {pct(v['within_one_ci'][0])} to {pct(v['within_one_ci'][1])} | {v['n_assessed']} |",
                  f"| Exact match | {pct(v['exact_match'])} | {pct(v['exact_ci'][0])} to {pct(v['exact_ci'][1])} | {v['n_assessed']} |",
                  f"| Mean absolute error (grades) | {v['mae']:.2f} | | {v['n_assessed']} |",
                  f"| Quadratic weighted kappa | {v['quadratic_weighted_kappa']:.2f} | | {v['n_assessed']} |",
                  f"| U rate | {pct(v['u_rate'])} | | {v['n_routed_with_truth']} |",
                  f"| Over-graded / under-graded | {v['over_graded']} / {v['under_graded']} | | |", "",
                  "Confusion (truth ordinal -> predicted ordinal): " + ", ".join(f"{k}: {n}" for k, n in v["confusion"].items()), ""]
    lines += ["## Ops (measured from call log)", "", "| Stage | Calls | Median seconds | USD total | Models |", "|---|---|---|---|---|"]
    for st, v in ops.items():
        if isinstance(v, dict):
            lines.append(f"| {st} | {v['calls']} | {v['median_seconds']:.2f} | {v['usd_total']} | {', '.join(v['models'])} |")
    lines += ["", f"USD per image (all stages): {ops.get('usd_per_image')}", ""]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
