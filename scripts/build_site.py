"""Copy the measured metrics into the marketing site (site/ is what deploys to Replit).

  python scripts/build_site.py

Writes site/assets/metrics.json and site/assets/metrics.js (the same numbers as a script
global, so the page also works when opened straight from disk). Run after
scripts/selfcheck.py and scripts/render_demo_video.py.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
m = json.loads((ROOT / "data" / "samples" / "metrics.json").read_text())
public = {k: m[k] for k in ("headline", "agent0", "agent1", "agent2", "agent3", "swarm", "generated_at")}
out = ROOT / "site" / "assets"
out.mkdir(parents=True, exist_ok=True)
(out / "metrics.json").write_text(json.dumps(public, indent=1))
(out / "metrics.js").write_text("window.CEREBRO_METRICS = " + json.dumps(public) + ";\n")
missing = [f for f in ("pavilion_cerebro_demo.mp4", "poster.jpg", "still_battery.jpg", "still_hvac.jpg", "still_disaster.jpg") if not (out / f).exists()]
print("site/assets updated" + (f"; missing (run scripts/render_demo_video.py): {missing}" if missing else ""))
