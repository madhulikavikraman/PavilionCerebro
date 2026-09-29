"""Agent 2 - Battery and electrical fire risk (NASA PCoE Li-ion aging data).

Per discharge cycle of each 18650 cell (B0005, B0006, B0007, B0018), the agent tracks

  capacity fade  -> State of Health (SOH = capacity / 2.0 Ah rated) and a Remaining
                    Useful Life projection to the dataset's own end-of-life criterion
                    (30% fade, 1.4 Ah), from a robust (Theil-Sen) trend over recent cycles;
  thermal        -> discharge temperature rise, scored by the generic engine
                    (agents.generic) against the cell's own inferred baseline;
  impedance      -> electrolyte + charge-transfer resistance (Re + Rct from EIS), scored
                    by the generic engine for growth and drift.

Fire-risk score: these are *precursor indicators* (capacity fade toward/after EOL,
impedance growth, abnormal self-heating), the signals battery-safety literature ties to
thermal-runaway susceptibility. The NASA cells never went into runaway; the score is a
triage signal for "pull this cell for inspection", not a runaway predictor. Weights are
a stated assumption, documented in README.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import numpy as np
import pandas as pd

from .base import AgentReport, BaseAgent
from .generic import SeriesMonitor, SeriesSpec

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"
RATED_AH = 2.0
EOL_AH = 1.4


def theil_sen(x: np.ndarray, y: np.ndarray) -> tuple:
    """Median pairwise slope: robust to the capacity-regeneration jumps after rest periods."""
    i, j = np.triu_indices(len(x), 1)
    dx = x[j] - x[i]
    ok = dx != 0
    slope = float(np.median((y[j] - y[i])[ok] / dx[ok]))
    intercept = float(np.median(y - slope * x))
    return slope, intercept


def project_rul(cycles: np.ndarray, cap: np.ndarray, window: int = 80) -> Optional[float]:
    """Cycles remaining until capacity reaches EOL_AH. 0 if already past, None if no fade trend."""
    if cap[-1] <= EOL_AH:
        return 0.0
    if len(cap) < 8:
        return None
    x, y = cycles[-window:].astype(float), cap[-window:].astype(float)
    slope, icpt = theil_sen(x, y)
    if slope >= -1e-5:
        return None
    level_now = slope * x[-1] + icpt
    return max(0.0, (EOL_AH - level_now) / slope)


def _logistic(v: float) -> float:
    return 1.0 / (1.0 + math.exp(-v))


class CellState:
    def __init__(self, cell: str) -> None:
        self.cell = cell
        self.cycles: List[int] = []
        self.cap: List[float] = []
        self.thermal = SeriesMonitor(SeriesSpec(name="discharge temperature rise", unit="degC", direction="high_bad", period=0, min_history=10), recent=3, drift_window=20)
        self.imp = SeriesMonitor(SeriesSpec(name="Re+Rct impedance", unit="ohm", direction="high_bad", period=0, min_history=10), recent=3, drift_window=20)
        self.imp0: Optional[float] = None


class BatteryAgent(BaseAgent):
    agent_id = "agent-2"
    subsystem = "battery"
    name = "Battery & Electrical Fire Risk"
    description = "SOH, remaining useful life and thermal-runaway precursor indicators for battery storage cells."
    data_source = "NASA Ames PCoE Li-ion Battery Aging Dataset (B0005, B0006, B0007, B0018)"

    CELLS = {"B0005": "BESS rack 1, string A", "B0006": "BESS rack 1, string B", "B0007": "BESS rack 2, string A", "B0018": "BESS rack 2, string B"}

    def __init__(self, clock=None, path: Path = SAMPLES / "battery_cycles.csv", start_cycle: int = 1) -> None:
        super().__init__(clock)
        self.df = pd.read_csv(path)
        self.start_cycle = start_cycle
        self.state: Dict[str, CellState] = {c: CellState(c) for c in self.CELLS}

    def observations(self) -> Iterator[pd.DataFrame]:
        # one tick = the next discharge cycle of every cell (cells that finished testing drop out)
        for cyc in range(1, int(self.df["cycle"].max()) + 1):
            rows = self.df[self.df["cycle"] == cyc]
            if cyc < self.start_cycle:
                for _, r in rows.iterrows():
                    self._ingest(r)
                continue
            yield rows

    def _ingest(self, r) -> dict:
        s = self.state[r["cell"]]
        s.cycles.append(int(r["cycle"]))
        s.cap.append(float(r["capacity_ah"]))
        th = s.thermal.push(float(r["temp_rise_c"]))
        imp_v = float(r["re_ohm"]) + float(r["rct_ohm"]) if np.isfinite(r["re_ohm"]) and np.isfinite(r["rct_ohm"]) else None
        if imp_v is not None and s.imp0 is None:
            s.imp0 = imp_v
        im = s.imp.push(imp_v)
        return {"thermal": th, "imp": im, "imp_v": imp_v}

    def assess_cell(self, r) -> AgentReport:
        cell = r["cell"]
        a = self._ingest(r)
        s = self.state[cell]
        cycles, cap = np.array(s.cycles), np.array(s.cap)
        soh = cap[-1] / RATED_AH
        fade = 1.0 - soh
        rul = project_rul(cycles, cap)
        imp_growth = (a["imp_v"] / s.imp0 - 1.0) if a["imp_v"] and s.imp0 else 0.0

        # precursor components (assumed weights, see README)
        deg = _logistic((fade - 0.27) / 0.025)  # 0.5 at 27% fade, ~0.77 at the 30% EOL line
        imp = _logistic((imp_growth - 0.25) / 0.06)  # 0.5 at +25% Re+Rct over the cell's first EIS reading
        thermal = a["thermal"].risk
        fire = 1.0 - (1.0 - 0.8 * deg) * (1.0 - 0.6 * imp) * (1.0 - 0.8 * thermal)
        # a cell trending to EOL within ~10 cycles gets a floor: it needs pulling soon regardless of heat
        if rul is not None and rul <= 10:
            fire = max(fire, 0.55 + 0.03 * (10 - rul))

        reasons = []
        if fade >= 0.30:
            reasons.append(f"capacity {cap[-1]:.3f} Ah is past the 1.4 Ah end-of-life line")
        elif rul is not None:
            reasons.append(f"projected {rul:.0f} cycles to end-of-life")
        if imp_growth >= 0.15:
            reasons.append(f"impedance up {100 * imp_growth:.0f}% since first EIS")
        reasons += a["thermal"].reasons
        head = f"{cell}: SOH {100 * soh:.0f}%, " + (reasons[0] if reasons else "healthy")
        conf = min(1.0, len(cap) / 20) * (0.85 if rul is not None or fade >= 0.3 else 0.6)
        return self.report(
            risk=fire, confidence=conf, asset_id=cell, zone=f"Basement battery room - {self.CELLS[cell]}", headline=head,
            evidence={"cycle": int(r["cycle"]), "source_time": r["start"], "capacity_ah": round(cap[-1], 4), "soh": round(soh, 4), "rul_cycles": None if rul is None else round(rul, 1),
                      "eol_ah": EOL_AH, "impedance_ohm": None if a["imp_v"] is None else round(a["imp_v"], 5), "impedance_growth": round(imp_growth, 4),
                      "temp_rise_c": round(float(r["temp_rise_c"]), 2), "temp_max_c": round(float(r["temp_max_c"]), 2),
                      "components": {"degradation": round(deg, 3), "impedance": round(imp, 3), "thermal": round(thermal, 3)},
                      "thermal_assessment": a["thermal"].as_dict(), "reasons": reasons},
            metrics={"cycle": int(r["cycle"]), "soh_pct": round(100 * soh, 1), "capacity_ah": round(cap[-1], 3), "rul_cycles": None if rul is None else round(rul),
                     "temp_max_c": round(float(r["temp_max_c"]), 1), "impedance_growth_pct": round(100 * imp_growth, 1)},
        )

    def observe(self, rows: pd.DataFrame) -> List[AgentReport]:
        return [self.assess_cell(r) for _, r in rows.iterrows()]


def evaluate_rul(path: Path = SAMPLES / "battery_cycles.csv", horizons=(40, 30, 20, 10)) -> dict:
    """RUL projection error at fixed horizons before each cell's actual EOL crossing."""
    df = pd.read_csv(path)
    out = []
    for cell, g in df.groupby("cell"):
        g = g.sort_values("cycle")
        below = g[g["capacity_ah"] <= EOL_AH]
        if below.empty:
            continue
        eol = int(below["cycle"].min())
        for h in horizons:
            at = eol - h
            sub = g[g["cycle"] <= at]
            rul = project_rul(sub["cycle"].to_numpy(), sub["capacity_ah"].to_numpy())
            out.append({"cell": cell, "eol_cycle": eol, "at_cycle": at, "true_rul": h, "pred_rul": None if rul is None else round(rul, 1)})
    errs = [abs(o["pred_rul"] - o["true_rul"]) for o in out if o["pred_rul"] is not None]
    return {"points": out, "mae_cycles": round(float(np.mean(errs)), 2) if errs else None, "n": len(errs)}
