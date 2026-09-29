"""CLI: run the cascade over a manifest.

Examples:
  python -m cascade.run --manifest data/dev/manifest.jsonl --out runs/dev01 --gate local --grader claude --limit 10
  python -m cascade.run --manifest data/eval_v1/manifest.jsonl --out runs/eval_v1_run1 --exemplars data/dev/manifest.jsonl
  python -m cascade.run --manifest data/dev/manifest.jsonl --out runs/gate_only --grader none
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from .exemplars import exemplar_provider
from .ingest import read_manifest
from .pipeline import Progress, RunConfig, run_cascade

ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m cascade.run", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--gate", choices=["local", "claude", "none"], default="local")
    ap.add_argument("--grader", choices=["claude", "local", "none"], default="claude", help="none = gate only, no grading calls")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--tiles", action="store_true", help="grade overlapping 1568 px tiles instead of the whole downscaled image (more calls, more cost)")
    ap.add_argument("--gate-min-conf", type=float, default=0.7, help="a no-damage verdict below this confidence is still routed to the grader")
    ap.add_argument("--force-route", default="pv_module", help="comma-separated asset classes always sent to the grader regardless of the gate verdict; '' to disable")
    ap.add_argument("--rubric", default=None, help="bridge rubric override, e.g. bridge_nbi.json (default bridge_mbei.json)")
    ap.add_argument("--exemplars", default=None, metavar="DEV_MANIFEST", help="FR-13: include labelled dev-set exemplars per asset class in the grader prompt")
    ap.add_argument("--exemplars-k", type=int, default=3, help="exemplars per asset class, 2 to 5")
    return ap


def main(argv=None) -> int:
    load_dotenv(ROOT / ".env")
    args = build_parser().parse_args(argv)
    records = read_manifest(Path(args.manifest))
    cfg = RunConfig(gate=args.gate, grader=args.grader, tiles=args.tiles, gate_min_conf=args.gate_min_conf, rubric_file=args.rubric, limit=args.limit, force_route_classes=tuple(c.strip() for c in args.force_route.split(',') if c.strip()))
    provider = exemplar_provider(Path(args.exemplars), k=args.exemplars_k) if args.exemplars else None

    total = min(len(records), args.limit) if args.limit else len(records)
    bar = tqdm(total=total, desc="cascade")
    seen: set = set()

    def on_progress(p: Progress) -> None:
        if p.current_image and p.current_image not in seen and p.stage in ("gate", "grade"):
            seen.add(p.current_image)
            bar.update(1)
        bar.set_postfix(routed=p.routed, graded=p.graded, usd=f"{p.usd:.3f}")

    summary = run_cascade(records, Path(args.out), cfg, exemplars=provider, progress=on_progress)
    bar.close()
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
