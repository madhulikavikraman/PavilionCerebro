"""Turn the raw public datasets in data/raw/ into small replayable samples in data/samples/.

Run once after `python data/download_datasets.py`. Every sample file is a straight
extraction or aggregation of real measurements; nothing here is synthesized.

  upv_readings.csv     UMN DRUM UHPC dataset: every UPV reading (direct / semi-direct / indirect, 54 and 250 kHz)
  upv_strength.csv     UMN DRUM UHPC dataset: paired compressive strength and direct UPV
  bms_zone2.csv        CU-BEMS floor 2 zone 2, 15-minute means (AC power per unit, temperature, humidity, light)
  battery_cycles.csv   NASA PCoE B0005/B0006/B0007/B0018: one row per discharge cycle + latest impedance
  hvac_windows.csv     ASHRAE RP-1043: steady-state 5-minute windows from fault-free and faulted runs
  crack/               a 60-image replay sample (30 cracked, 30 intact) not used for calibration
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "samples"


def _age_hours(s: str) -> float:
    s = str(s).strip().lower()
    m = re.match(r"([\d.]+)\s*(hr|hrs|hour|hours|day|days)", s)
    if not m:
        raise ValueError(f"unparsed age {s!r}")
    v = float(m.group(1))
    return v if m.group(2).startswith("h") else v * 24.0


def prepare_upv() -> None:
    x = RAW / "umn_upv" / "UHPC_NDE_Dataset.xlsx"
    rows = []
    for sheet, mode in (("Direct UPV", "direct"), ("Semi-Direct UPV", "semi-direct"), ("Indirect UPV", "indirect")):
        df = pd.read_excel(x, sheet_name=sheet)
        cols = list(df.columns)
        fiber, age, path_m = cols[0], cols[1], cols[3]
        v54 = [c for c in cols if "UPV" in c and "54" in c][0]
        v250 = [c for c in cols if "UPV" in c and "250" in c][0]
        for i, r in df.iterrows():
            if pd.isna(r[age]):
                continue
            for freq, col in ((54, v54), (250, v250)):
                if pd.notna(r[col]):
                    rows.append({"mode": mode, "freq_khz": freq, "fiber_pct": float(r[fiber]), "age_h": _age_hours(r[age]), "path_m": float(r[path_m]), "upv_mps": float(r[col]), "row": i})
    upv = pd.DataFrame(rows)
    upv.to_csv(OUT / "upv_readings.csv", index=False)

    s = pd.read_excel(x, sheet_name="Strength and NDE values")
    cols = list(s.columns)
    s = s.rename(columns={cols[0]: "fiber_pct", cols[1]: "age", cols[3]: "strength_mpa", cols[7]: "direct_upv_mps", cols[8]: "rebound"})
    s["fiber_pct"] = s["fiber_pct"].ffill()
    s["age"] = s["age"].ffill()
    s = s.dropna(subset=["strength_mpa", "direct_upv_mps"])
    s["age_h"] = s["age"].map(_age_hours)
    s[["fiber_pct", "age_h", "strength_mpa", "direct_upv_mps", "rebound"]].to_csv(OUT / "upv_strength.csv", index=False)
    print(f"upv: {len(upv)} readings, {len(s)} strength pairs")


def prepare_bms() -> None:
    df = pd.read_csv(RAW / "cu_bems" / "2018Floor2.csv", parse_dates=["Date"]).set_index("Date")
    z = pd.DataFrame(index=df.index)
    ac_cols = [c for c in df if c.startswith("z2_AC")]
    for c in ac_cols:
        z[c.split("_")[1].split("(")[0].lower() + "_kw"] = df[c]
    z["ac_total_kw"] = df[ac_cols].sum(axis=1, min_count=1)
    z["light_kw"] = df["z2_Light(kW)"]
    z["plug_kw"] = df["z2_Plug(kW)"]
    z["temp_c"] = df["z2_S1(degC)"]
    z["rh_pct"] = df["z2_S1(RH%)"]
    z["lux"] = df["z2_S1(lux)"]
    q = z.resample("15min").mean()
    q = q.loc["2018-07-01":"2018-09-12"].round(3)
    q.index.name = "time"
    q.to_csv(OUT / "bms_zone2.csv")
    print(f"bms: {len(q)} rows of 15-min zone-2 telemetry")


def prepare_battery() -> None:
    import scipy.io as sio

    base = RAW / "nasa_battery" / "5. Battery Data Set" / "fy08q4"
    rows = []
    for cell in ("B0005", "B0006", "B0007", "B0018"):
        m = sio.loadmat(base / f"{cell}.mat", simplify_cells=True)
        re_, rct = np.nan, np.nan
        n = 0
        for c in m[cell]["cycle"]:
            d = c["data"]
            if c["type"] == "impedance":
                re_v, rct_v = float(np.real(d["Re"])), float(np.real(d["Rct"]))
                # a handful of EIS fits in this set are non-physical (negative or > 1 ohm); keep the last good one
                if 0 < re_v < 1:
                    re_ = re_v
                if 0 < rct_v < 1:
                    rct = rct_v
            elif c["type"] == "discharge":
                n += 1
                t = np.asarray(d["Time"], dtype=float)
                temp = np.asarray(d["Temperature_measured"], dtype=float)
                v = np.asarray(d["Voltage_measured"], dtype=float)
                tv = [int(x) for x in np.asarray(c["time"]).ravel()[:6]]
                rows.append({
                    "cell": cell,
                    "cycle": n,
                    "start": f"{tv[0]:04d}-{tv[1]:02d}-{tv[2]:02d}T{tv[3]:02d}:{tv[4]:02d}:{tv[5]:02d}",
                    "ambient_c": float(c["ambient_temperature"]),
                    "capacity_ah": float(d["Capacity"]),
                    "temp_max_c": float(temp.max()),
                    "temp_rise_c": float(temp.max() - temp[0]),
                    "time_to_tmax_s": float(t[int(np.argmax(temp))]),
                    "duration_s": float(t[-1]),
                    "v_mean": float(v.mean()),
                    "re_ohm": re_,
                    "rct_ohm": rct,
                })
    b = pd.DataFrame(rows)
    b.round(5).to_csv(OUT / "battery_cycles.csv", index=False)
    print(f"battery: {len(b)} discharge cycles over {b.cell.nunique()} cells")


# ASHRAE RP-1043 runs used. Severity levels follow the project's own four steps per fault.
HVAC_RUNS = {
    "Benchmark Tests/normal.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal1.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal r.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal eo.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal cf.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal cf2.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal cf4.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal nc.xls": ("normal", 0, "train"),
    "Benchmark Tests/normal2.xls": ("normal", 0, "holdout"),
    "Benchmark Tests/normal r1.xls": ("normal", 0, "holdout"),
    "Benchmark Tests/normal cf5.xls": ("normal", 0, "holdout"),
    "Benchmark Tests/normal cf6.xls": ("normal", 0, "holdout"),
}
for fault, folder, stems in (
    ("reduced_condenser_flow", "Reduced condenser water flow", ["fwc10", "fwc20", "fwc30", "fwc40"]),
    ("reduced_evaporator_flow", "Reduced evaporator water flow", ["fwe10", "fwe20", "fwe30", "fwe40"]),
    ("refrigerant_leak", "Refrigerant leak", ["rl10", "rl20", "rl30", "rl40"]),
    ("refrigerant_overcharge", "Refrigerant overcharge", ["ro10", "ro20", "ro30", "ro40"]),
    ("condenser_fouling", "Condenser fouling", ["cf12", "cf20", "cf30", "cf45"]),
    ("excess_oil", "Excess oil", ["eo14", "eo32", "eo50", "eo68--unsteady test1"]),
    ("non_condensables", "Non-condensables in refrigerant", ["nc1", "nc2", "nc3", "nc5"]),
):
    for lvl, stem in enumerate(stems, start=1):
        HVAC_RUNS[f"{folder}/{stem}.xls"] = (fault, lvl, "fault")

HVAC_FEATURES = ["TEI", "TEO", "TCI", "TCO", "TRE", "PRE", "TRC", "PRC", "TRC_sub", "Tsh_suc", "Tsh_dis", "TO_feed", "PO_feed", "PO_net", "TO_sump", "kW", "FWC", "FWE", "TCA", "TEA", "COP", "TWCO", "TWCI", "TWEO", "TWEI", "Evap Tons"]


def prepare_hvac() -> None:
    base = RAW / "ashrae_rp1043" / "Chiller Data"
    out = []
    for rel, (fault, lvl, split) in HVAC_RUNS.items():
        df = pd.read_excel(base / rel)
        df = df[HVAC_FEATURES + ["Time"]].apply(pd.to_numeric, errors="coerce")
        df = df[df["kW"] > 20]  # compressor running
        g = df.groupby((df["Time"] // 300).astype(int))  # 5-minute windows (Time is seconds)
        agg = g[HVAC_FEATURES].mean()
        sd = g[["TWEO", "TWCI", "Evap Tons"]].std()
        cnt = g.size()
        steady = (cnt >= 20) & (sd["TWEO"] < 0.3) & (sd["TWCI"] < 0.5) & (sd["Evap Tons"] < 4.0)
        agg = agg[steady].copy()
        agg["run"] = Path(rel).stem
        agg["fault"] = fault
        agg["level"] = lvl
        agg["split"] = split
        agg["t_min"] = agg.index * 5
        out.append(agg)
        print(f"  {rel}: {len(agg)} steady windows")
    h = pd.concat(out, ignore_index=True).round(4)
    h.to_csv(OUT / "hvac_windows.csv", index=False)
    print(f"hvac: {len(h)} windows from {h.run.nunique()} runs")


def prepare_crack(n_each: int = 30, seed: int = 7) -> None:
    src = RAW / "crack_images" / "test"
    dst = OUT / "crack"
    dst.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    # the replay sample is drawn from the second half of the sorted file list; the first half is the calibration split
    for label in ("Positive", "Negative"):
        files = sorted((src / label).glob("*.jpg"))
        pool = files[len(files) // 2:]
        for f in rng.choice(pool, size=n_each, replace=False):
            shutil.copy(f, dst / f"{label.lower()}_{f.name}")
    print(f"crack: {2 * n_each} replay images")


def main(argv: list) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    steps = {"upv": prepare_upv, "bms": prepare_bms, "battery": prepare_battery, "hvac": prepare_hvac, "crack": prepare_crack}
    for name in argv or list(steps):
        steps[name]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
