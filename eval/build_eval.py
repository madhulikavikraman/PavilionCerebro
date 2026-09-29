"""Build the frozen eval_v1 and dev manifests (docs/decisions.md D-007, research note R07).

Usage (from repo root, inside the venv):
  python eval/build_eval.py --download
Writes data/eval_v1/manifest.jsonl, data/dev/manifest.jsonl and data/eval_v1/FROZEN.sha256.
Sampling is seeded so the same command reproduces the same sets. Team-graded labels for
dacl10k are added later from eval/team_grades/ without changing image selection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cascade.ingest import sha256_of, write_manifest  # noqa: E402
from cascade.schema import ImageRecord  # noqa: E402

RAW = ROOT / "data" / "raw"
SEED = 20260925
IR_MAP = json.loads((ROOT / "eval/rubrics/ir_solar_class_map.json").read_text(encoding="utf-8"))["map"]
RN_MAP = json.loads((ROOT / "eval/rubrics/rescuenet_class_map.json").read_text(encoding="utf-8"))["map"]
DACL = json.loads((ROOT / "eval/rubrics/dacl10k_classes.json").read_text(encoding="utf-8"))
IR_NAMES = ["Cell", "Cell-Multi", "Cracking", "Diode", "Diode-Multi", "Hot-Spot", "Hot-Spot-Multi", "No-Anomaly", "Offline-Module", "Shadowing", "Soiling", "Vegetation"]


def fetch(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    r = requests.get(url, timeout=180, allow_redirects=True)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def rec(path: Path, image_id: str, asset_class: str, source: str, split: str, labels: dict) -> ImageRecord:
    with Image.open(path) as im:
        w, h = im.size
    return ImageRecord(image_id=image_id, path=str(path), sha256=sha256_of(path), width=w, height=h, asset_class=asset_class, source_dataset=source, split=split, labels=labels)


def corrosion(rng: random.Random):
    rows = list(csv.DictReader((RAW / "corrosion_cs" / "index.csv").open(encoding="utf-8")))
    test = [r for r in rows if r["split"] == "test"]
    train = [r for r in rows if r["split"] == "train"]
    by_cls = defaultdict(list)
    for r in train:
        by_cls[r["worst_class"]].append(r)
    dev_rows = []
    for cls in ("Fair", "Poor", "Severe"):
        pool = by_cls[cls][:]
        rng.shuffle(pool)
        dev_rows += pool[:5]

    def mk(r, split):
        labels = {"damage_present": True, "classes_present": ["steel_corrosion"], "grade_native": r["worst_class"], "grade_scale": "CorrosionCS", "grade_source": "dataset", "area_fracs": {"Fair": float(r["fair_frac"]), "Poor": float(r["poor_frac"]), "Severe": float(r["severe_frac"])}}
        return rec(Path(r["image"]), f"corr_{r['split']}_{r['name']}", "steel_coating", "corrosion_cs", split, labels)

    return [mk(r, "eval_v1") for r in test], [mk(r, "dev") for r in dev_rows]


def dacl10k(rng: random.Random, download: bool):
    rows = list(csv.DictReader((RAW / "dacl10k" / "val_index.csv").open(encoding="utf-8")))
    dmg = set(DACL["damage_classes"])
    for r in rows:
        r["_labels"] = set(filter(None, r["labels"].split(";")))
        r["_damage"] = sorted(r["_labels"] & dmg)
        r["_fracs"] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in r["area_fracs"].split(";") if kv}
    clean = [r for r in rows if not r["_damage"]]
    rng.shuffle(clean)
    chosen, used = [], set()
    for cls in DACL["eval_target_classes"]:
        pool = [r for r in rows if cls in r["_damage"] and r["name"] not in used]
        rng.shuffle(pool)
        for r in pool[: (5 if cls == "ACrack" else 10)]:
            chosen.append(r)
            used.add(r["name"])
    extra = [r for r in rows if r["_damage"] and r["name"] not in used]
    rng.shuffle(extra)
    while len(chosen) < 50 and extra:
        r = extra.pop()
        chosen.append(r)
        used.add(r["name"])
    eval_rows = chosen + clean[:10]
    for r in eval_rows:
        used.add(r["name"])
    rest_d = [r for r in rows if r["_damage"] and r["name"] not in used]
    rest_c = [r for r in clean if r["name"] not in used]
    rng.shuffle(rest_d)
    dev_rows = rest_d[:10] + rest_c[:5]

    def mk(r, split):
        dest = RAW / "dacl10k" / "images" / Path(r["filepath"]).name
        if download:
            fetch(f"https://huggingface.co/datasets/Voxel51/dacl10k/resolve/main/{r['filepath']}", dest)
        labels = {"damage_present": bool(r["_damage"]), "classes_present": r["_damage"], "all_labels": sorted(r["_labels"]), "grade_native": None, "grade_scale": "MBEI-CS", "grade_source": None, "area_fracs": r["_fracs"]}
        return rec(dest, f"dacl_{r['name']}", "bridge_element", "dacl10k", split, labels)

    return [mk(r, "eval_v1") for r in eval_rows], [mk(r, "dev") for r in dev_rows]


def ir_solar(rng: random.Random):
    import pyarrow.parquet as pq

    t = pq.read_table(RAW / "ir_solar" / "test-00000-of-00001.parquet")
    labels = t.column("label").to_pylist()
    images = t.column("image").to_pylist()
    by_cls = defaultdict(list)
    for i, lab in enumerate(labels):
        by_cls[IR_NAMES[int(lab)]].append(i)
    for k in by_cls:
        rng.shuffle(by_cls[k])
    anomalies = [c for c in IR_NAMES if c != "No-Anomaly"]
    eval_idx = [(i, "No-Anomaly") for i in by_cls["No-Anomaly"][:15]]
    for c in anomalies:
        eval_idx += [(i, c) for i in by_cls[c][:2]]
    for c in ("Cell", "Hot-Spot", "Diode"):
        eval_idx += [(i, c) for i in by_cls[c][2:3]]
    dev_idx = [(i, "No-Anomaly") for i in by_cls["No-Anomaly"][15:19]]
    for c in anomalies[:8]:
        dev_idx += [(i, c) for i in by_cls[c][3:4]]
    out_dir = RAW / "ir_solar" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    def mk(i, cls, split):
        dest = out_dir / f"test_{i:05d}.png"
        if not dest.exists():
            b = images[i]["bytes"] if isinstance(images[i], dict) else images[i]
            Image.open(io.BytesIO(b)).save(dest)
        m = IR_MAP[cls]
        labels_ = {"damage_present": cls != "No-Anomaly", "classes_present": [] if cls == "No-Anomaly" else [cls], "source_class": cls, "grade_native": m["coa"], "grade_scale": "IEC-62446-3-CoA", "grade_source": "dataset-class-mapped", "unified_truth": m["s"]}
        return rec(dest, f"ir_test_{i:05d}", "pv_module", "ir_solar", split, labels_)

    return [mk(i, c, "eval_v1") for i, c in eval_idx], [mk(i, c, "dev") for i, c in dev_idx]


def rescuenet(rng: random.Random, download: bool):
    idx = json.loads((RAW / "rescuenet" / "index.json").read_text(encoding="utf-8"))
    test_by_cls = defaultdict(list)
    for f, split in idx["split"].items():
        if split == "test" and f in idx["label"]:
            test_by_cls[idx["label"][f]].append(f)
    for k in test_by_cls:
        test_by_cls[k].sort()
        rng.shuffle(test_by_cls[k])
    want = {"Intact": 13, "Damaged": 14, "Collapsed": 13}
    dev_want = {"Intact": 3, "Damaged": 3, "Collapsed": 2}
    out_dir = RAW / "rescuenet" / "images"

    def mk(f, cls, split):
        dest = out_dir / f
        if download:
            fetch(f"https://huggingface.co/datasets/USF-IAE/RescueNet-BDA-Split/resolve/main/test/{f}", dest)
        m = RN_MAP[cls]
        labels_ = {"damage_present": cls != "Intact", "classes_present": [] if cls == "Intact" else [cls], "source_class": cls, "grade_native": cls, "grade_scale": "RescueNet-3", "grade_source": "dataset", "fema_group": m["fema_group"], "unified_truth": m["s"]}
        return rec(dest, f"rn_test_{Path(f).stem}", "building_disaster", "rescuenet", split, labels_)

    ev, dv = [], []
    for cls, n in want.items():
        ev += [mk(f, cls, "eval_v1") for f in test_by_cls[cls][:n]]
        dv += [mk(f, cls, "dev") for f in test_by_cls[cls][n : n + dev_want[cls]]]
    return ev, dv


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true", help="fetch dacl10k and RescueNet images from Hugging Face")
    ap.add_argument("--skip", nargs="*", default=[], choices=["corrosion", "dacl10k", "ir_solar", "rescuenet"])
    args = ap.parse_args()
    rng = random.Random(SEED)
    ev, dv = [], []
    for name, fn in (("corrosion", lambda: corrosion(rng)), ("dacl10k", lambda: dacl10k(rng, args.download)), ("ir_solar", lambda: ir_solar(rng)), ("rescuenet", lambda: rescuenet(rng, args.download))):
        if name in args.skip:
            continue
        e, d = fn()
        print(f"{name}: eval {len(e)}  dev {len(d)}")
        ev += e
        dv += d
    write_manifest(ev, ROOT / "data/eval_v1/manifest.jsonl")
    write_manifest(dv, ROOT / "data/dev/manifest.jsonl")
    digest = hashlib.sha256((ROOT / "data/eval_v1/manifest.jsonl").read_bytes()).hexdigest()
    (ROOT / "data/eval_v1/FROZEN.sha256").write_text(digest + "  manifest.jsonl\n")
    print(f"eval_v1: {len(ev)} images, dev: {len(dv)} images, manifest sha256 {digest[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
