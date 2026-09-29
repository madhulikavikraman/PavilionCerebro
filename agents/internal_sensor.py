"""Agent 1 - Internal Sensor Intelligence (UPV + BMS telemetry).

One generalized ingestion path, two unrelated real data sources. The only
source-specific code here is the two loaders (`_upv_channels`, `_bms_channels`), each
of which turns its file into labeled numeric series plus whatever metadata the source
actually has. Scoring is done by the same `agents.generic` function for both:

  UPV (UMN DRUM UHPC dataset)  metadata available: an expected pulse velocity for the
      specimen's age, fiber content and test configuration (leave-one-out median of the
      matching readings), and a per-configuration spread (IQR of reading vs expected,
      floored at 2% of expected as a measurement tolerance; the floor is a team assumption). Lower-than-expected UPV means a less dense, weaker material, the
      standard NDT relationship (ASTM C597). Strength is estimated from UPV with an
      exponential fit on the dataset's own 108 paired strength/UPV measurements.
  BMS (CU-BEMS, a real building energy management system)  no metadata at all: the
      baseline, its daily seasonality and the normal range are inferred from the data.

If a third source arrived tomorrow (vibration, moisture, strain) it would get a loader
and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import numpy as np
import pandas as pd

from .base import AgentReport, BaseAgent
from .generic import SeriesMonitor, SeriesSpec, corroborated

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"


@dataclass
class Reading:
    channel: str
    value: Optional[float]
    expected: Optional[float] = None
    source_time: str = ""
    extra: Optional[dict] = None


# ------------------------------------------------------------------ UPV loader


def upv_strength_model(path: Path = SAMPLES / "upv_strength.csv") -> dict:
    """strength_MPa = a * exp(b * UPV) fitted on the dataset's paired measurements."""
    s = pd.read_csv(path)
    b, ln_a = np.polyfit(s["direct_upv_mps"], np.log(s["strength_mpa"]), 1)
    pred = np.exp(ln_a + b * s["direct_upv_mps"])
    r2 = 1 - ((s["strength_mpa"] - pred) ** 2).sum() / ((s["strength_mpa"] - s["strength_mpa"].mean()) ** 2).sum()
    by_age = s.groupby("age_h")["strength_mpa"].mean()
    return {"a": float(np.exp(ln_a)), "b": float(b), "r2": float(r2), "n": int(len(s)), "expected_strength_by_age": by_age.to_dict()}


def _upv_channels(path: Path = SAMPLES / "upv_readings.csv") -> List[Reading]:
    u = pd.read_csv(path)
    u["channel"] = "UPV " + u["mode"] + " " + u["freq_khz"].astype(str) + "kHz"
    keys = ["mode", "freq_khz", "fiber_pct", "age_h"]
    # expected value for each reading: median of the *other* readings with the same age, mix and configuration
    exp = []
    for _, g in u.groupby(keys):
        for i in g.index:
            others = g.loc[g.index != i, "upv_mps"]
            exp.append((i, float(others.median()) if len(others) else np.nan))
    u["expected"] = pd.Series(dict(exp))
    # measurement repeatability per test configuration (robust spread of reading vs expected) is source metadata
    resid = u["upv_mps"] - u["expected"]
    # robust spread (IQR) so gross artifacts (a 12,350 m/s semi-direct reading) do not inflate it
    scale = {ch: float((np.nanpercentile(r, 75) - np.nanpercentile(r, 25)) / 1.349) for ch, r in resid.groupby(u["channel"])}
    u = u.sort_values(["age_h", "fiber_pct", "mode", "freq_khz", "row"]).reset_index(drop=True)
    out = []
    for _, r in u.iterrows():
        age = r["age_h"]
        age_s = f"{int(age)} h" if age < 24 else f"{age / 24:g} d"
        out.append(Reading(channel=r["channel"], value=float(r["upv_mps"]), expected=r["expected"], source_time=f"age {age_s}",
                           extra={"scale": max(scale[r["channel"]], 0.02 * r["expected"]) if r["expected"] == r["expected"] else scale[r["channel"]], "fiber_pct": r["fiber_pct"], "age_h": age, "path_m": r["path_m"], "mode": r["mode"], "freq_khz": int(r["freq_khz"])}))
    return out


# ------------------------------------------------------------------ BMS loader

BMS_CHANNELS = {
    "temp_c": ("Zone temperature", "degC"),
    "rh_pct": ("Zone humidity", "%RH"),
    "ac1_kw": ("AC unit 1 power", "kW"),
    "ac_total_kw": ("Zone AC power", "kW"),
    "plug_kw": ("Plug load", "kW"),
}


def _bms_frame(path: Path = SAMPLES / "bms_zone2.csv") -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["time"]).set_index("time")


# ------------------------------------------------------------------ agent


class InternalSensorAgent(BaseAgent):
    agent_id = "agent-1"
    subsystem = "internal_sensor"
    name = "Internal Sensor Intelligence"
    description = "Generic numeric-sensor inference: UPV material health and BMS telemetry through one scoring function."
    data_source = "UMN DRUM UHPC UPV dataset (CC0) + CU-BEMS building management telemetry (CC BY 4.0)"

    UPV_ASSET = "upv-L2-slab"
    BMS_ASSET = "bms-floor2-zone2"

    def __init__(self, clock=None, bms_live_start: str = "2018-08-27", bms_step: int = 12, upv_step: int = 6) -> None:
        super().__init__(clock)
        self.strength = upv_strength_model()
        self.upv = _upv_channels()
        self.bms = _bms_frame()
        self.bms_live_start = pd.Timestamp(bms_live_start)
        self.bms_step = bms_step  # 15-min samples per replay tick (12 = 3 hours)
        self.upv_step = upv_step  # UPV readings per replay tick
        self.upv_mon: Dict[str, SeriesMonitor] = {}
        self.bms_mon: Dict[str, SeriesMonitor] = {}
        for col, (label, unit) in BMS_CHANNELS.items():
            # no metadata: direction "both", baseline, period and range all inferred
            self.bms_mon[col] = SeriesMonitor(SeriesSpec(name=label, unit=unit, direction="both", period=None, min_history=48), maxlen=8000, recent=8, drift_window=96)
        warm = self.bms.loc[: self.bms_live_start - pd.Timedelta(minutes=15)]
        for col, mon in self.bms_mon.items():
            mon.warm(warm[col].to_numpy(dtype=float))
        self.upv_history: List[dict] = []

    # -- helpers -----------------------------------------------------------

    def _upv_monitor(self, channel: str, scale: float) -> SeriesMonitor:
        if channel not in self.upv_mon:
            # metadata: expected UPV per reading and the configuration's repeatability; low UPV = weaker material
            self.upv_mon[channel] = SeriesMonitor(SeriesSpec(name=channel, unit="m/s", direction="low_bad", period=0, scale=scale, min_history=6, trend=False), maxlen=400, recent=1, drift_window=12)
        return self.upv_mon[channel]

    def est_strength(self, upv: float) -> float:
        return self.strength["a"] * np.exp(self.strength["b"] * upv)

    def expected_strength(self, age_h: float) -> float:
        ages = sorted(self.strength["expected_strength_by_age"])
        vals = [self.strength["expected_strength_by_age"][a] for a in ages]
        return float(np.interp(np.log(age_h), np.log(ages), vals))

    # -- BaseAgent ---------------------------------------------------------

    def observations(self) -> Iterator[dict]:
        live = self.bms.loc[self.bms_live_start:]
        n_bms = len(live) // self.bms_step
        n_upv = int(np.ceil(len(self.upv) / self.upv_step))
        for t in range(max(n_bms, n_upv)):
            yield {
                "upv": self.upv[t * self.upv_step:(t + 1) * self.upv_step] if t < n_upv else [],
                "bms": live.iloc[t * self.bms_step:(t + 1) * self.bms_step] if t < n_bms else None,
            }

    def observe(self, obs: dict) -> List[AgentReport]:
        reports = []
        if obs.get("upv"):
            reports.append(self._observe_upv(obs["upv"]))
        if obs.get("bms") is not None and len(obs["bms"]):
            reports.append(self._observe_bms(obs["bms"]))
        return reports

    def _observe_upv(self, readings: List[Reading]) -> AgentReport:
        worst = None
        for rd in readings:
            a = self._upv_monitor(rd.channel, rd.extra["scale"]).push(rd.value, rd.expected)
            self.upv_history.append({"channel": rd.channel, "value": rd.value, "expected": rd.expected, "risk": a.risk, **(rd.extra or {})})
            if worst is None or a.risk > worst[1].risk:
                worst = (rd, a)
        # asset risk: corroboration over the most recent readings (two ticks), not each channel's latched last value
        recent = [x["risk"] for x in self.upv_history[-2 * self.upv_step:]]
        risk = corroborated(recent)
        rd, a = worst
        # the strength curve was fitted on direct-transmission UPV; other path geometries do not map onto it
        direct = rd.extra["mode"] == "direct"
        est = self.est_strength(rd.value) if direct else None
        exp_s = self.expected_strength(rd.extra["age_h"])
        deficit = (est - exp_s) / exp_s if direct else None
        head = f"{rd.channel}: {rd.value:.0f} m/s vs {rd.expected:.0f} expected at {rd.source_time}" if rd.expected == rd.expected else f"{rd.channel}: {rd.value:.0f} m/s"
        return self.report(
            risk=risk, confidence=a.confidence, asset_id=self.UPV_ASSET, zone="Level 2 transfer slab - UHPC repair pour", headline=head,
            evidence={"worst_channel": a.as_dict(), "channels": {k: m.last.as_dict() for k, m in self.upv_mon.items() if m.last},
                      "strength_model": {"form": "MPa = a*exp(b*UPV)", "a": round(self.strength["a"], 4), "b": round(self.strength["b"], 6), "r2": round(self.strength["r2"], 3), "n_pairs": self.strength["n"]},
                      "est_strength_mpa": None if est is None else round(est, 1), "expected_strength_mpa": round(exp_s, 1),
                      "strength_deficit_pct": None if deficit is None else round(100 * deficit, 1), "source_time": rd.source_time,
                      "specimen": rd.extra},
            metrics={"upv_mps": round(rd.value, 0), "expected_mps": round(rd.expected, 0) if rd.expected == rd.expected else None, "est_strength_mpa": None if est is None else round(est, 1),
                     "strength_deficit_pct": None if deficit is None else round(100 * deficit, 1), "age": rd.source_time, "config": rd.channel.replace("UPV ", "")},
        )

    def _observe_bms(self, block: pd.DataFrame) -> AgentReport:
        last = {}
        for col, mon in self.bms_mon.items():
            last[col] = mon.push_many([None if not np.isfinite(v) else v for v in block[col].to_numpy(dtype=float)])
        risks = {c: a.risk for c, a in last.items()}
        top = max(risks, key=risks.get)
        risk = corroborated(risks.values())
        t = block.index[-1]
        a = last[top]
        reasons = [r for c in last for r in last[c].reasons if last[c].risk >= 0.3]
        head = reasons[0] if reasons else "All zone telemetry within inferred normal pattern"
        return self.report(
            risk=risk, confidence=float(np.mean([x.confidence for x in last.values()])), asset_id=self.BMS_ASSET, zone="Floor 2, zone 2 (office) - BMS points", headline=head,
            evidence={"source_time": str(t), "top_channel": a.as_dict(), "channels": {c: x.as_dict() for c, x in last.items()}},
            metrics={"source_time": t.strftime("%m-%d %H:%M"), **{c: (round(x.value, 2) if x.value is not None else None) for c, x in last.items()},
                     "top_channel": BMS_CHANNELS[top][0]},
        )
