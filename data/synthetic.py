"""Fallback synthetic generator: same schemas as data/samples/, clearly marked SYNTHETIC.

  python data/synthetic.py          # writes only the sample files that are missing

The real samples in data/samples/ are committed, so this should never be needed for the
demo. It exists so the agents and dashboard can still be exercised if a sample file is
lost and the public source is unreachable. Anything it writes is recorded in
data/samples/SYNTHETIC.txt, and nothing it produces may be quoted as a result.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "samples"
rng = np.random.default_rng(0)


def upv() -> None:
    rows = []
    for mode, base in (("direct", 4700), ("semi-direct", 4750), ("indirect", 4400)):
        for freq in (54, 250):
            for age in (24, 72, 168, 336, 672):
                for fiber in (0, 1, 2, 3):
                    for i in range(3):
                        v = base * (1 + 0.03 * np.log(age / 24) / np.log(28)) + rng.normal(0, 60)
                        rows.append({"mode": mode, "freq_khz": freq, "fiber_pct": fiber, "age_h": age, "path_m": 0.25, "upv_mps": round(v, 1), "row": i})
    pd.DataFrame(rows).to_csv(OUT / "upv_readings.csv", index=False)
    s = [{"fiber_pct": f, "age_h": a, "strength_mpa": round(0.25 * np.exp(0.00125 * u), 1), "direct_upv_mps": u, "rebound": None}
         for f in (0, 1, 2, 3) for a, u in ((12, 1700), (24, 4400), (72, 4610), (168, 4660), (672, 4840))]
    pd.DataFrame(s).to_csv(OUT / "upv_strength.csv", index=False)


def bms() -> None:
    t = pd.date_range("2018-07-01", "2018-09-12", freq="15min")
    hour = t.hour + t.minute / 60
    work = ((hour >= 8) & (hour <= 18) & (t.dayofweek < 5)).astype(float)
    df = pd.DataFrame({"time": t})
    df["ac1_kw"] = 20 * work + rng.normal(0, 0.5, len(t))
    for i in range(2, 15):
        df[f"ac{i}_kw"] = work * rng.uniform(0.5, 1.2) + rng.normal(0, 0.05, len(t))
    df["ac_total_kw"] = df[[c for c in df if c.startswith("ac") and c != "ac_total_kw"]].sum(axis=1)
    df["light_kw"], df["plug_kw"] = 0.6 * work, 0.3 * work + 0.05
    df["temp_c"] = 26 + 2 * work + rng.normal(0, 0.3, len(t))
    df["rh_pct"] = 62 - 3 * work + rng.normal(0, 1, len(t))
    df["lux"] = 100 * work
    df.round(3).to_csv(OUT / "bms_zone2.csv", index=False)


def battery() -> None:
    rows = []
    for cell, fade in (("B0005", 0.0033), ("B0006", 0.0045), ("B0007", 0.0026), ("B0018", 0.0048)):
        for c in range(1, 169):
            cap = 1.9 * (1 - fade * c) + rng.normal(0, 0.01)
            rows.append({"cell": cell, "cycle": c, "start": "2008-04-02T00:00:00", "ambient_c": 24, "capacity_ah": cap, "temp_max_c": 38 + 0.02 * c + rng.normal(0, 0.4),
                         "temp_rise_c": 14 + 0.02 * c + rng.normal(0, 0.4), "time_to_tmax_s": 3000, "duration_s": 3200, "v_mean": 3.5, "re_ohm": 0.05 + 0.0001 * c, "rct_ohm": 0.07 + 0.0001 * c})
    pd.DataFrame(rows).round(5).to_csv(OUT / "battery_cycles.csv", index=False)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    wrote = []
    for fname, fn in (("upv_readings.csv", upv), ("bms_zone2.csv", bms), ("battery_cycles.csv", battery)):
        if not (OUT / fname).exists():
            fn()
            wrote.append(fname)
    if wrote:
        with (OUT / "SYNTHETIC.txt").open("a") as fh:
            fh.write("SYNTHETIC fallback data written by data/synthetic.py (not real measurements): " + ", ".join(wrote) + "\n")
    # hvac_windows.csv and crack images have no synthetic stand-in: those agents need the real data
    print("synthetic fallback wrote: " + (", ".join(wrote) if wrote else "nothing (all real samples present)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
