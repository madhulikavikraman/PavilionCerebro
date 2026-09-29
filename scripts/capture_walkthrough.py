"""Capture real screenshots of the actual dashboard for the layperson walkthrough.

  python scripts/capture_walkthrough.py            # -> site/walkthrough/img/*.jpg

This is the "slow, one-idea-at-a-time" companion to the live dashboard. The live dashboard
(python -m dashboard.server) is the expert, bird's-eye view: everything at once, ticking in
real time. site/walkthrough/ is the same real product, paused, with one real screenshot and
one plain-English caption per screen, advanced by hand.

Every image here is a real screenshot of the real dashboard (headless Chromium, static
mode), fed a real recorded run of the real swarm — the same recording approach as
scripts/render_demo_video.py, whose record() and Shooter this script reuses. Nothing is
mocked up or drawn separately from the product.

For each of the four agents, the "problem" screenshot is taken at the tick where that
agent's own risk score peaks in this run, found automatically rather than hardcoded, so
this keeps working if the underlying data or agents change.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from scripts.render_demo_video import Shooter, record  # noqa: E402

OUT = ROOT / "site" / "walkthrough" / "img"
PAD = 28


def crop(img, box, pad=PAD, max_h=None):
    x, y, w, h = box
    if max_h:
        h = min(h, max_h)
    return img.crop((max(0, int(x - pad)), max(0, int(y - pad)), int(x + w + pad), int(y + h + pad)))


def peak_tick(snaps: dict, agent_id: str) -> int:
    """The tick in this recorded run where `agent_id`'s worst concern is highest."""
    best_t, best_r = min(snaps), -1.0
    for t, snap in snaps.items():
        r = max((c["risk"] for c in snap["concerns"] if c["agent_id"] == agent_id), default=-1.0)
        if r > best_r:
            best_t, best_r = t, r
    return best_t


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("recording a swarm run (same as the demo video)...")
    rec = record()
    snaps = rec["snaps"]
    early = min(t for t in snaps if t >= 5)
    picks = {
        "healthy": (early, "health", "health"),
        "map": (early, "map", "map"),
        "agent0": (peak_tick(snaps, "agent-0"), "a0", "a0"),
        "agent1": (peak_tick(snaps, "agent-1"), "a1", "a1"),
        "agent2": (peak_tick(snaps, "agent-2"), "a2", "a2"),
        "agent3": (peak_tick(snaps, "agent-3"), "a3", "a3"),
        "queue": (max(snaps), "queue", "queue"),
        "feed": (max(snaps), "feed", "feed"),
    }

    sh = Shooter()
    try:
        for name, (tick, sel_a, sel_b) in picks.items():
            img, boxes = sh.shot(snaps[tick], settle_ms=500)
            x0 = min(boxes[sel_a][0], boxes[sel_b][0])
            y0 = min(boxes[sel_a][1], boxes[sel_b][1])
            x1 = max(boxes[sel_a][0] + boxes[sel_a][2], boxes[sel_b][0] + boxes[sel_b][2])
            y1 = max(boxes[sel_a][1] + boxes[sel_a][3], boxes[sel_b][1] + boxes[sel_b][3])
            cap = 620 if name == "queue" else None
            crop(img, (x0, y0, x1 - x0, y1 - y0), max_h=cap).convert("RGB").save(OUT / f"{name}.jpg", quality=90)
            print(f"  {name}.jpg  (tick {tick})")

        img, boxes = sh.shot(rec["dis_before"], settle_ms=500)
        crop(img, boxes["queue"], max_h=620).convert("RGB").save(OUT / "disaster_before.jpg", quality=90)
        img, boxes = sh.shot(rec["dis_after"][-1], settle_ms=500)
        crop(img, boxes["queue"], max_h=620).convert("RGB").save(OUT / "disaster_after.jpg", quality=90)
        print("  disaster_before.jpg, disaster_after.jpg")
    finally:
        sh.close()

    print(f"wrote {len(list(OUT.glob('*.jpg')))} images to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
