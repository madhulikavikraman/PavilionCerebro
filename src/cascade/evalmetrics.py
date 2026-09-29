"""Grading and gate metrics for a run, computed against dataset labels (docs/decisions.md D-007).

Used by the UI's Eval matrix tab and the run report. The ordinal maps are the frozen files under
`eval/rubrics/`, written before any model output. `eval/run_eval.py` remains the scored, CI-bearing
reference; this module reuses its definitions so the app never shows a number the eval would not.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .schema import ImageRecord

ROOT = Path(__file__).resolve().parents[2]
_RUBRICS = ROOT / "eval" / "rubrics"


def _load(name: str) -> dict:
    p = _RUBRICS / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


IR = _load("ir_solar_class_map.json")
RN = _load("rescuenet_class_map.json")
CORR_ORD = _load("dacl10k_classes.json").get("corrosion_ordinal", {})

# ordinal index -> human label per asset class; the eval script's k_for() gives the same sizes
ORDINAL_LABELS: Dict[str, List[str]] = {
    "steel_coating": [k for k, _ in sorted(CORR_ORD.items(), key=lambda kv: kv[1])] or ["Good", "Fair", "Poor", "Severe"],
    "pv_module": [k for k, _ in sorted(IR.get("ordinal", {}).items(), key=lambda kv: kv[1])] or ["CoA 1", "CoA 2", "CoA 3"],
    "building_disaster": [k for k, _ in sorted(RN.get("ordinal", {}).items(), key=lambda kv: kv[1])] or ["Intact", "Damaged", "Collapsed"],
    "bridge_element": ["CS1", "CS2", "CS3", "CS4"],
}

TRUTH_SOURCE = {
    "steel_coating": "dataset inspector grade (Corrosion Condition State, CC0)",
    "pv_module": "12 InfraredSolarModules classes mapped to IEC TS 62446-3 CoA before any model output",
    "building_disaster": "RescueNet scene label Intact / Damaged / Collapsed; FEMA PDA values collapsed to three levels",
    "bridge_element": "team-graded MBEI condition state only (dacl10k has defect classes, not grades)",
}


def truth_ordinal(rec: ImageRecord) -> Optional[int]:
    ac, lab = rec.asset_class, rec.labels or {}
    if ac == "steel_coating":
        return CORR_ORD.get(lab.get("grade_native"))
    if ac == "pv_module":
        return IR.get("ordinal", {}).get(lab.get("grade_native"))
    if ac == "building_disaster":
        return RN.get("ordinal", {}).get(lab.get("source_class"))
    if ac == "bridge_element" and lab.get("grade_source") == "team-graded" and lab.get("grade_native") is not None:
        try:
            return int(lab["grade_native"]) - 1
        except (TypeError, ValueError):
            return None
    return None


def predicted_ordinal(asset_class: str, findings: Iterable[dict]) -> Optional[int]:
    """Worst (max) predicted ordinal across an image's findings; None if all U or unmappable."""
    vals = []
    for f in findings:
        if f["unified"]["level"] == "U":
            continue
        nv = f["native_scale"]["value"]
        o = None
        if asset_class == "steel_coating":
            o = CORR_ORD.get(nv)
        elif asset_class == "pv_module":
            o = IR.get("ordinal", {}).get(nv)
        elif asset_class == "building_disaster":
            cls = RN.get("predicted_to_class", {}).get(nv)
            o = RN.get("ordinal", {}).get(cls) if cls else None
        elif asset_class == "bridge_element":
            digits = "".join(ch for ch in str(nv) if ch.isdigit())
            o = int(digits) - 1 if digits and 1 <= int(digits) <= 4 else None
        if o is not None:
            vals.append(o)
    return max(vals) if vals else None


def qwk(truth: List[int], pred: List[int], k: int) -> float:
    """Quadratic weighted kappa, pure Python."""
    if not truth:
        return 0.0
    O = [[0.0] * k for _ in range(k)]
    for t, p in zip(truth, pred):
        O[t][p] += 1
    n = float(len(truth))
    row = [sum(r) for r in O]
    col = [sum(O[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2 if k > 1 else 0.0
            e = row[i] * col[j] / n
            num += w * O[i][j]
            den += w * e
    return 1.0 - num / den if den else 0.0


def eval_matrix(records: Dict[str, ImageRecord], gate_rows: List[dict], findings: List[dict]) -> dict:
    """Gate 2x2 and per-asset-class confusion matrices for one run.

    Returns {"gate": {...}, "per_dataset": {...}, "grading": {asset_class: {...}}}. Every count is over the
    images that are both in the run and carry a label; images without truth are listed, never guessed.
    """
    gate = {g["image_id"]: g for g in gate_rows}
    by_img = defaultdict(list)
    for f in findings:
        for iid in f["evidence"]["image_ids"]:
            by_img[iid].append(f)
    scored = [i for i in records if i in gate]

    labelled = [i for i in scored if "damage_present" in (records[i].labels or {})]
    tp = fp = fn = tn = 0
    per_ds: Dict[str, dict] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    for i in labelled:
        t, p = bool(records[i].labels.get("damage_present")), bool(gate[i]["routed"])
        cell = "tp" if t and p else "fp" if p else "fn" if t else "tn"
        per_ds[records[i].source_dataset][cell] += 1
        if cell == "tp":
            tp += 1
        elif cell == "fp":
            fp += 1
        elif cell == "fn":
            fn += 1
        else:
            tn += 1

    def prf(d):
        prec = d["tp"] / (d["tp"] + d["fp"]) if d["tp"] + d["fp"] else None
        rec = d["tp"] / (d["tp"] + d["fn"]) if d["tp"] + d["fn"] else None
        return prec, rec

    gate_out = {"n": len(labelled), "tp": tp, "fp": fp, "fn": fn, "tn": tn, "unlabelled": len(scored) - len(labelled),
                "misses": [i for i in labelled if records[i].labels.get("damage_present") and not gate[i]["routed"]]}
    gate_out["precision"], gate_out["recall"] = prf(gate_out)
    for ds, d in per_ds.items():
        d["precision"], d["recall"] = prf(d)
        d["n"] = d["tp"] + d["fp"] + d["fn"] + d["tn"]

    grading: Dict[str, dict] = {}
    by_ac = defaultdict(list)
    for i in scored:
        t = truth_ordinal(records[i])
        if t is None or not gate[i]["routed"]:
            continue
        by_ac[records[i].asset_class].append((t, predicted_ordinal(records[i].asset_class, by_img.get(i, [])), i))
    for ac, items in by_ac.items():
        labels = ORDINAL_LABELS[ac]
        k = len(labels)
        matrix = [[0] * k for _ in range(k)]
        assessed = []
        u_images = []
        for t, p, iid in items:
            if p is None:
                u_images.append(iid)
                continue
            matrix[t][p] += 1
            assessed.append((t, p, iid))
        n_a = len(assessed)
        grading[ac] = {
            "labels": labels,
            "truth_source": TRUTH_SOURCE.get(ac, ""),
            "matrix": matrix,  # rows = truth, cols = predicted
            "n_routed_with_truth": len(items),
            "n_assessed": n_a,
            "u_rate": 1 - n_a / len(items) if items else None,
            "u_images": u_images,
            "exact_match": sum(1 for t, p, _ in assessed if t == p) / n_a if n_a else None,
            "within_one_grade": sum(1 for t, p, _ in assessed if abs(t - p) <= 1) / n_a if n_a else None,
            "mae": sum(abs(t - p) for t, p, _ in assessed) / n_a if n_a else None,
            "qwk": qwk([t for t, _, _ in assessed], [p for _, p, _ in assessed], k) if n_a else None,
            "over_graded": sum(1 for t, p, _ in assessed if p > t),
            "under_graded": sum(1 for t, p, _ in assessed if p < t),
            "pairs": [{"image_id": iid, "truth": labels[t], "pred": labels[p]} for t, p, iid in assessed],
        }
    return {"gate": gate_out, "per_dataset": dict(per_ds), "grading": grading}
