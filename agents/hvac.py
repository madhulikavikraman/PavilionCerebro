"""Agent 3 - HVAC chiller fault detection and diagnosis (ASHRAE RP-1043).

Data: 5-minute steady-state windows from the RP-1043 90-ton centrifugal chiller, fault-free
benchmark runs and seven faults at four severity levels (data/prepare_samples.py).

Method, all fitted on real runs and scored on runs the model did not see:
  1. Fault-free reference: each of 23 sensor features is regressed (quadratic) on the
     operating point (leaving chilled-water temp, entering condenser-water temp, load)
     using 8 fault-free benchmark runs. Live readings become standardized residuals.
  2. Detection: Mahalanobis distance of the residual vector; the alarm threshold is the
     99th percentile on the fault-free training runs. False-alarm rate is measured on 4
     held-out fault-free runs.
  3. Diagnosis: each fault's signature is the mean whitened residual direction of its
     detected windows. A window is assigned the fault whose signature it points along
     (cosine). Signatures are always built without the severity level being scored
     (leave-one-severity-out), so diagnosis is never tested on its own training data.
  4. Severity SL1-SL4: residual magnitude interpolated against the other levels' magnitudes.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np
import pandas as pd

from .base import AgentReport, BaseAgent

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "samples"

REGRESSORS = ["TWEO", "TWCI", "Evap Tons"]
FEATURES = ["TEI", "TEO", "TCI", "TCO", "TRE", "PRE", "TRC", "PRC", "TRC_sub", "Tsh_suc", "Tsh_dis", "TO_feed", "PO_feed", "PO_net", "TO_sump", "kW", "FWC", "FWE", "TCA", "TEA", "COP", "TWCO", "TWEI"]
FAULT_LABELS = {
    "reduced_condenser_flow": "Reduced condenser water flow",
    "reduced_evaporator_flow": "Reduced evaporator water flow",
    "refrigerant_leak": "Refrigerant leak (undercharge)",
    "refrigerant_overcharge": "Refrigerant overcharge",
    "condenser_fouling": "Condenser fouling",
    "excess_oil": "Excess oil",
    "non_condensables": "Non-condensables in refrigerant",
}


def _design(d: pd.DataFrame) -> np.ndarray:
    a, b, c = (d[k].to_numpy(float) for k in REGRESSORS)
    return np.column_stack([np.ones(len(d)), a, b, c, a * a, b * b, c * c, a * b, a * c, b * c])


@dataclass
class HvacModel:
    B: np.ndarray = None
    mu: np.ndarray = None
    sd: np.ndarray = None
    L: np.ndarray = None  # whitening: ||z @ L||^2 = Mahalanobis d2
    thr: float = 0.0
    signatures: Dict[str, np.ndarray] = field(default_factory=dict)
    level_mag: Dict[str, Dict[int, float]] = field(default_factory=dict)
    holdout: Optional[Tuple[str, int]] = None

    @classmethod
    def fit(cls, h: pd.DataFrame, holdout: Optional[Tuple[str, int]] = None) -> "HvacModel":
        m = cls(holdout=holdout)
        tr = h[h["split"] == "train"]
        m.B, *_ = np.linalg.lstsq(_design(tr), tr[FEATURES].to_numpy(float), rcond=None)
        r = tr[FEATURES].to_numpy(float) - _design(tr) @ m.B
        m.mu, m.sd = r.mean(0), r.std(0) + 1e-9
        z = (r - m.mu) / m.sd
        ci = np.linalg.inv(np.cov(z.T) + 0.05 * np.eye(len(FEATURES)))
        m.L = np.linalg.cholesky(ci)
        m.thr = float(np.percentile(((z @ m.L) ** 2).sum(1), 99))
        f = h[h["split"] == "fault"]
        if holdout is not None:
            f = f[~((f["fault"] == holdout[0]) & (f["level"] == holdout[1]))]
        w = m.whiten(f)
        d2 = (w ** 2).sum(1)
        det = d2 > m.thr
        for fault, g in f.groupby("fault"):
            dirs, mags = [], {}
            for lvl, gl in g.groupby("level"):
                sel = np.isin(f.index, gl.index) & det
                if sel.sum() >= 5:
                    v = w[sel].mean(0)
                    dirs.append(v / np.linalg.norm(v))
                    mags[int(lvl)] = float(np.median(np.sqrt(d2[sel])))
            if dirs:
                v = np.mean(dirs, 0)
                m.signatures[fault] = v / np.linalg.norm(v)
                m.level_mag[fault] = mags
        return m

    def whiten(self, d: pd.DataFrame) -> np.ndarray:
        r = d[FEATURES].to_numpy(float) - _design(d) @ self.B
        return ((r - self.mu) / self.sd) @ self.L

    def classify(self, w: np.ndarray) -> Dict[str, float]:
        n = np.linalg.norm(w) + 1e-9
        return {f: float(w @ s / n) for f, s in self.signatures.items()}

    def severity(self, fault: str, mag: float) -> float:
        pts = sorted(self.level_mag.get(fault, {}).items())
        if not pts:
            return 1.0
        lv = np.array([p[0] for p in pts], float)
        lm = np.log(np.array([p[1] for p in pts]))
        x = np.log(max(mag, 1e-6))
        if len(pts) == 1:
            return float(lv[0])
        if x <= lm[0]:
            slope = (lv[1] - lv[0]) / max(1e-6, lm[1] - lm[0])
            s = lv[0] + slope * (x - lm[0])
        elif x >= lm[-1]:
            slope = (lv[-1] - lv[-2]) / max(1e-6, lm[-1] - lm[-2])
            s = lv[-1] + slope * (x - lm[-1])
        else:
            order = np.argsort(lm)
            s = float(np.interp(x, lm[order], lv[order]))
        return float(np.clip(s, 1.0, 4.0))


# live replay: held-out fault-free run, then a refrigerant leak progressing through SL1-SL4
SCENARIO = [("normal2", None, 30), ("rl10", ("refrigerant_leak", 1), 22), ("rl20", ("refrigerant_leak", 2), 22), ("rl30", ("refrigerant_leak", 3), 28), ("rl40", ("refrigerant_leak", 4), 40)]


class HvacAgent(BaseAgent):
    agent_id = "agent-3"
    subsystem = "hvac"
    name = "HVAC Fault Detection & Diagnosis"
    description = "Chiller fault detection against a fault-free baseline, fault-type diagnosis and SL1-SL4 severity."
    data_source = "ASHRAE RP-1043 90-ton centrifugal chiller (CC0, figshare 28435232)"
    ASSET = "CH-1"

    def __init__(self, clock=None, path: Path = SAMPLES / "hvac_windows.csv", scenario=SCENARIO, smooth: int = 3) -> None:
        super().__init__(clock)
        self.h = pd.read_csv(path)
        self.scenario = scenario
        self._models: Dict[Optional[tuple], HvacModel] = {}
        self.recent = deque(maxlen=smooth)

    def model(self, holdout) -> HvacModel:
        if holdout not in self._models:
            self._models[holdout] = HvacModel.fit(self.h, holdout)
        return self._models[holdout]

    def observations(self) -> Iterator[tuple]:
        for run, holdout, n in self.scenario:
            rows = self.h[self.h["run"] == run].sort_values("t_min")
            idx = np.linspace(0, len(rows) - 1, min(n, len(rows))).astype(int)
            for _, r in rows.iloc[idx].iterrows():
                yield run, holdout, r

    def observe(self, obs) -> List[AgentReport]:
        run, holdout, r = obs
        m = self.model(holdout)
        row = r[FEATURES + REGRESSORS].astype(float).to_frame().T
        w = m.whiten(row)[0]
        self.recent.append(w)
        wm = np.median(np.array(self.recent), axis=0)  # short median filter over 5-minute windows
        d2 = float((wm ** 2).sum())
        ratio = np.sqrt(d2 / m.thr)
        scores = m.classify(wm)
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        fault, cos = ranked[0]
        detected = d2 > m.thr and len(self.recent) >= 2  # never alarm on a single unfiltered window
        if detected:
            sev = m.severity(fault, np.sqrt(d2))
            risk = 0.45 + 0.14 * (sev - 1.0)
            conf = float(np.clip(0.5 + 0.5 * (cos - ranked[1][1]) / max(1e-6, cos), 0.3, 0.95))
            head = f"{FAULT_LABELS[fault]} - SL{int(round(sev))} (match {cos:.2f})"
        else:
            sev = 0.0
            risk = 0.3 * min(1.0, ratio) ** 2
            conf = 0.8
            head = "Operating within fault-free envelope"
        raw = row[FEATURES].to_numpy(float) - _design(row) @ m.B
        zf = ((raw - m.mu) / m.sd)[0]
        top_feats = sorted(zip(FEATURES, zf), key=lambda kv: -abs(kv[1]))[:5]
        truth = "fault-free" if holdout is None else f"{FAULT_LABELS[holdout[0]]} SL{holdout[1]}"
        return [self.report(
            risk=min(risk, 0.97), confidence=conf, asset_id=self.ASSET, zone="Roof mechanical plant - chiller CH-1 (90-ton centrifugal)", headline=head,
            evidence={"run": run, "ground_truth": truth, "model_holdout": None if holdout is None else list(holdout), "source_time": f"{run} t={int(r['t_min'])} min",
                      "mahalanobis_d2": round(d2, 1), "threshold_d2": round(m.thr, 1), "detected": bool(detected),
                      "diagnosis": [{"fault": FAULT_LABELS[f], "match": round(s, 3)} for f, s in ranked[:3]], "severity_level": round(sev, 2),
                      "top_residuals": [{"feature": f, "z": round(float(z), 2)} for f, z in top_feats],
                      "operating_point": {k: round(float(r[k]), 2) for k in REGRESSORS}},
            metrics={"d2_ratio": round(float(ratio), 2), "fault": FAULT_LABELS[fault] if detected else "none", "severity": f"SL{int(round(sev))}" if detected else "-",
                     "kW": round(float(r["kW"]), 1), "COP": round(float(r["COP"]), 2), "run": run},
        )]


def evaluate(path: Path = SAMPLES / "hvac_windows.csv") -> dict:
    """Detection, false alarms, leave-one-severity-out diagnosis and severity accuracy on RP-1043."""
    h = pd.read_csv(path)
    base = HvacModel.fit(h)
    ho = h[h["split"] == "holdout"]
    fa = float(((base.whiten(ho) ** 2).sum(1) > base.thr).mean())
    per, correct, total, sev_exact, sev_close, n_sev = [], 0, 0, 0, 0, 0
    runs_flagged = 0
    for (fault, lvl), g in h[h["split"] == "fault"].groupby(["fault", "level"]):
        m = HvacModel.fit(h, (fault, int(lvl)))
        w = m.whiten(g)
        d2 = (w ** 2).sum(1)
        det = d2 > m.thr
        preds = [max(m.classify(x).items(), key=lambda kv: kv[1])[0] for x in w[det]]
        ok = sum(p == fault for p in preds)
        correct += ok
        total += len(preds)
        sevs = [m.severity(fault, float(np.sqrt(x))) for x in d2[det]]
        sev_exact += sum(int(round(s)) == int(lvl) for s in sevs)
        sev_close += sum(abs(int(round(s)) - int(lvl)) <= 1 for s in sevs)
        n_sev += len(sevs)
        runs_flagged += int(det.mean() >= 0.5 and preds and max(set(preds), key=preds.count) == fault)
        per.append({"fault": fault, "level": int(lvl), "windows": int(len(g)), "detection_rate": round(float(det.mean()), 3),
                    "diagnosis_accuracy": round(ok / len(preds), 3) if preds else None})
    return {
        "false_alarm_rate_holdout_normal": round(fa, 4),
        "n_holdout_normal_windows": int(len(ho)),
        "detection_rate_all_fault_windows": round(float(np.mean([p["detection_rate"] for p in per])), 3),
        "diagnosis_accuracy_detected": round(correct / max(1, total), 4),
        "n_detected_windows": int(total),
        "severity_exact": round(sev_exact / max(1, n_sev), 3),
        "severity_within_one": round(sev_close / max(1, n_sev), 3),
        "fault_runs": len(per),
        "fault_runs_detected_and_diagnosed": runs_flagged,
        "per_run": per,
    }
