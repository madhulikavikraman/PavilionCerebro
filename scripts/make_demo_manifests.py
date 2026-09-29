"""Cut small per-dataset demo manifests from the dev set for the Streamlit walkthrough.

Writes data/demo/<source_dataset>/manifest.jsonl with up to --n rows each (default 10),
labelled rows first so the demo can show dataset truth next to the model grade. The rows
are copies of dev-manifest rows (image paths point at data/raw), so nothing is duplicated
on disk. Eval images are never used.

Usage: python scripts/make_demo_manifests.py [--n 10]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cascade.ingest import read_manifest, write_manifest  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", default=str(ROOT / "data" / "dev" / "manifest.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "data" / "demo"))
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--mixed", type=int, default=3, help="rows per dataset in the mixed sample (round-robin across all four asset classes)")
    args = ap.parse_args()
    records = read_manifest(Path(args.dev))
    by_ds: dict = {}
    for r in records:
        by_ds.setdefault(r.source_dataset, []).append(r)
    for ds, recs in sorted(by_ds.items()):
        recs = sorted(recs, key=lambda r: (r.labels.get("grade_native") is None, not r.labels.get("damage_present", False), r.image_id))
        chosen = [r for r in recs if Path(r.path).exists()][: args.n]
        out = Path(args.out) / ds / "manifest.jsonl"
        write_manifest(chosen, out)
        print(f"{ds}: {len(chosen)} rows -> {out}")
    # mixed sample: round-robin so the first rows already span every asset class
    per_ds = {}
    for ds, recs in sorted(by_ds.items()):
        recs = sorted(recs, key=lambda r: (r.labels.get("grade_native") is None, not r.labels.get("damage_present", False), r.image_id))
        per_ds[ds] = [r for r in recs if Path(r.path).exists()][: args.mixed]
    mixed = [r for i in range(args.mixed) for ds in sorted(per_ds) if i < len(per_ds[ds]) for r in [per_ds[ds][i]]]
    out = Path(args.out) / "mixed" / "manifest.jsonl"
    write_manifest(mixed, out)
    print(f"mixed: {len(mixed)} rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
