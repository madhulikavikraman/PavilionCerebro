"""Generic numeric-sensor inference: one function for any labeled series.

This is the concrete proof behind "the agent infers from whatever data it gets". The
same `assess()` call scores ultrasonic pulse velocity readings on a concrete pour and
chilled-air / AC-power telemetry from a building management system. Nothing here knows
what the numbers mean. The caller supplies a `SeriesSpec` (name, unit, which direction
is bad, and optionally an expected value or normal range); anything not supplied is
inferred from the data itself:

  baseline  provided expected value            -> deviation from that expectation
            else a detected seasonal period     -> median of the same phase in past cycles
            else                                -> rolling median of recent history
  scale     provided, else robust MAD of past residuals
  range     provided, else the 0.5-99.5 percentile band of past values

Three generic signals are combined:
  level      z-score of the latest reading(s) against the baseline
  drift      total trend over a window, in units of scale (catches slow degradation)
  crossing   fraction of recent readings outside the normal range
Missing readings are scored too (a sensor that goes quiet is itself a finding).

The combined risk maps deviation significance onto 0-1: a sustained 3.5-sigma departure
scores 0.5, 5 sigma scores ~0.9. False-alarm rates on fault-free data are measured in
scripts/selfcheck.py rather than assumed.
"""

from __future__ import annotations

import math
import warnings
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Tuple

import numpy as np

MAD_TO_SIGMA = 1.4826


@dataclass
class SeriesSpec:
    name: str
    unit: str = ""
    direction: str = "both"  # "low_bad" | "high_bad" | "both"
    normal_range: Optional[Tuple[float, float]] = None
    scale: Optional[float] = None
    period: Optional[int] = None  # samples per cycle; None = try to infer; 0 = never seasonal
    min_history: int = 12
    trend: bool = True  # False for reading sets (independent specimens/paths), where ordering carries no time


@dataclass
class Assessment:
    name: str
    value: Optional[float]
    baseline: Optional[float]
    scale: Optional[float]
    z: float
    drift_z: float
    frac_out: float
    missing_run: int
    risk: float
    confidence: float
    method: str
    reasons: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        r = lambda v, n=3: None if v is None or (isinstance(v, float) and not math.isfinite(v)) else round(float(v), n)
        return {
            "series": self.name,
            "value": r(self.value),
            "baseline": r(self.baseline),
            "scale": r(self.scale),
            "z": r(self.z, 2),
            "drift_z": r(self.drift_z, 2),
            "frac_out": r(self.frac_out, 2),
            "missing_run": self.missing_run,
            "risk": r(self.risk),
            "confidence": r(self.confidence),
            "baseline_method": self.method,
            "reasons": self.reasons,
        }


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _robust_scale(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    if x.size < 3:
        return float("nan")
    mad = np.median(np.abs(x - np.median(x))) * MAD_TO_SIGMA
    # zero-inflated signals (equipment off overnight) collapse the MAD; floor it at half the SD
    return float(max(mad, 0.5 * float(np.std(x))))


def infer_period(values: np.ndarray, min_lag: int = 4, min_acf: float = 0.45) -> int:
    """Seasonal period from the data itself. 0 if none.

    Finds the first strong autocorrelation peak, then prefers a multiple of it when that
    multiple correlates clearly better (a daily cycle inside a weekly one: weekends differ).
    """
    v = np.asarray(values, dtype=float)
    ok = np.isfinite(v)
    n = v.size
    if ok.sum() < 3 * min_lag + 8:
        return 0
    # keep gaps in place (filled with the mean) so lags stay aligned with sample spacing
    x = np.where(ok, v - v[ok].mean(), 0.0)
    f = np.fft.rfft(x, n=2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n]
    if acf[0] <= 0:
        return 0
    acf = acf / acf[0]
    acf = acf * n / np.maximum(1, n - np.arange(n))  # unbiased: long lags are not penalized for fewer overlapping samples
    first = 0
    for lag in range(min_lag, n // 3):
        if acf[lag] >= min_acf and acf[lag] >= acf[lag - 1] and acf[lag] >= acf[lag + 1]:
            first = lag
            break
    if not first:
        return 0
    best = first
    for k in range(2, 9):
        lag = k * first
        if lag >= n // 3:
            break
        near = acf[max(1, lag - 2): lag + 3]
        if near.max() > acf[best] + 0.05:
            best = lag - 2 + int(near.argmax()) if lag - 2 >= 1 else lag
    return best


def _directional(z: float, direction: str) -> float:
    if direction == "low_bad":
        return max(0.0, -z)
    if direction == "high_bad":
        return max(0.0, z)
    return abs(z)


def assess(
    history: np.ndarray,
    spec: SeriesSpec,
    *,
    expected: Optional[np.ndarray] = None,
    recent: int = 4,
    drift_window: int = 24,
) -> Assessment:
    """Score the latest point(s) of `history` (oldest first, NaN = missing reading).

    `expected`, when given, is the per-point expected value from source metadata
    (same length as history); deviations are measured against it directly.
    """
    h = np.asarray(history, dtype=float)
    reasons: List[str] = []
    missing_run = 0
    for v in h[::-1]:
        if np.isfinite(v):
            break
        missing_run += 1
    valid_n = int(np.isfinite(h).sum())
    last = float(h[-1]) if h.size and np.isfinite(h[-1]) else None

    if expected is not None:
        e = np.asarray(expected, dtype=float)
        resid = h - e
        past = resid[:-recent] if resid.size > recent else resid[:0]
        scale = spec.scale or _robust_scale(past)
        base_now = float(e[-1]) if np.isfinite(e[-1]) else None
        method = "provided (source metadata)"
    else:
        period = spec.period
        if period is None:
            period = infer_period(h[:-recent] if h.size > recent else h)
        if period and h.size > 2 * period + recent:
            # seasonal baseline: median of the same phase in up to 7 previous cycles
            base = np.full(h.size, np.nan)
            idx = np.arange(max(0, h.size - 400), h.size)
            lagged = np.stack([np.where(idx - k * period >= 0, h[np.clip(idx - k * period, 0, None)], np.nan) for k in range(1, 8)])
            ok = np.isfinite(lagged).sum(0) >= 2
            with np.errstate(all="ignore"), warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                base[idx[ok]] = np.nanmedian(lagged[:, ok], axis=0)
            method = f"inferred seasonal (period={period} samples)"
        else:
            base = np.full(h.size, np.nan)
            w = max(spec.min_history, 3 * recent)
            padded = np.concatenate([np.full(w + recent, np.nan), h])
            win = np.lib.stride_tricks.sliding_window_view(padded, w)[: h.size]
            start = max(0, h.size - 400)
            seg = win[start:]
            ok = np.isfinite(seg).sum(1) >= 3
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                base[start:][ok] = np.nanmedian(seg[ok], axis=1)
            method = "inferred rolling median"
        resid = h - base
        past = resid[:-recent] if resid.size > recent else resid[:0]
        scale = spec.scale or _robust_scale(past)
        base_now = float(base[-1]) if np.isfinite(base[-1]) else None

    if not np.isfinite(scale) or scale <= 0:
        scale = float("nan")

    rec = resid[-recent:]
    rec = rec[np.isfinite(rec)]
    z_now = z_rec = drift_z = frac_out = 0.0
    if np.isfinite(scale) and rec.size:
        if np.isfinite(resid[-1]):
            z_now = float(resid[-1] / scale)
        z_rec = float(np.mean(rec) / scale)
        dw = resid[-drift_window:]
        idx = np.where(np.isfinite(dw))[0]
        if spec.trend and idx.size >= 6:
            slope = np.polyfit(idx, dw[idx], 1)[0]
            drift_z = float(slope * drift_window / scale)

    # normal range: provided, or the 0.5-99.5 percentile band of past raw values
    lo_hi = spec.normal_range
    if lo_hi is None:
        past_vals = h[:-recent][np.isfinite(h[:-recent])] if h.size > recent else np.array([])
        if past_vals.size >= spec.min_history:
            lo_hi = (float(np.percentile(past_vals, 0.5)), float(np.percentile(past_vals, 99.5)))
    tail = h[-recent:]
    tail = tail[np.isfinite(tail)]
    if lo_hi is not None and tail.size:
        lo, hi = lo_hi
        if spec.direction == "low_bad":
            out = tail < lo
        elif spec.direction == "high_bad":
            out = tail > hi
        else:
            out = (tail < lo) | (tail > hi)
        frac_out = float(out.mean())

    d_now = _directional(z_now, spec.direction)
    d_rec = _directional(z_rec, spec.direction)
    d_drift = _directional(drift_z, spec.direction)
    level = max(d_rec, 0.6 * d_now)  # sustained deviation counts more than a single spike
    s_level = _logistic((level - 3.5) / 0.7)
    s_drift = _logistic((d_drift - 3.0) / 1.0)
    s_cross = frac_out
    s_missing = min(1.0, missing_run / 12.0) * 0.6
    risk = 1.0 - (1.0 - s_level) * (1.0 - 0.7 * s_drift) * (1.0 - 0.6 * s_cross) * (1.0 - s_missing)

    if level >= 2.0:
        reasons.append(f"{spec.name} {'below' if (z_rec if d_rec else z_now) < 0 else 'above'} baseline by {level:.1f} sigma")
    if d_drift >= 2.0:
        reasons.append(f"{spec.name} trending {'down' if drift_z < 0 else 'up'} ({d_drift:.1f} sigma over {drift_window} readings)")
    if frac_out > 0:
        reasons.append(f"{int(round(frac_out * 100))}% of recent {spec.name} readings outside normal range")
    if missing_run:
        reasons.append(f"{spec.name}: {missing_run} consecutive missing readings")

    enough = min(1.0, valid_n / max(1, 3 * spec.min_history))
    confidence = enough * (0.9 if expected is not None else 0.75) * (1.0 - min(0.5, missing_run / 24.0))
    return Assessment(
        name=spec.name,
        value=last,
        baseline=base_now,
        scale=scale if np.isfinite(scale) else None,
        z=z_now,
        drift_z=drift_z,
        frac_out=frac_out,
        missing_run=missing_run,
        risk=float(risk),
        confidence=float(confidence),
        method=method,
        reasons=reasons,
    )


class SeriesMonitor:
    """Streaming wrapper around `assess`: push readings one at a time."""

    def __init__(self, spec: SeriesSpec, maxlen: int = 2000, recent: int = 4, drift_window: int = 24) -> None:
        self.spec = spec
        self.values: Deque[float] = deque(maxlen=maxlen)
        self.expected: Deque[float] = deque(maxlen=maxlen)
        self.recent = recent
        self.drift_window = drift_window
        self._period: Optional[int] = spec.period
        self.last: Optional[Assessment] = None

    def warm(self, values, expected=None) -> None:
        """Load history without scoring it (baseline warm-up before live replay starts)."""
        exp = [None] * len(values) if expected is None else list(expected)
        for v, e in zip(values, exp):
            self.values.append(np.nan if v is None or not np.isfinite(v) else float(v))
            self.expected.append(np.nan if e is None else float(e))

    def push_many(self, values, expected=None) -> Assessment:
        """Append a block of readings and score once at the end of the block."""
        values = list(values)
        exp = [None] * len(values) if expected is None else list(expected)
        self.warm(values[:-1], exp[:-1])
        return self.push(values[-1], exp[-1])

    def push(self, value: Optional[float], expected: Optional[float] = None) -> Assessment:
        self.values.append(np.nan if value is None else float(value))
        self.expected.append(np.nan if expected is None else float(expected))
        # infer the seasonal period once enough history exists, then keep it fixed
        if self._period is None and len(self.values) >= 400:
            self._period = infer_period(np.array(self.values)) or 0
        spec = self.spec if self._period is None else SeriesSpec(**{**self.spec.__dict__, "period": self._period})
        if spec.period is None:
            spec = SeriesSpec(**{**spec.__dict__, "period": 0})
        exp = np.array(self.expected) if np.isfinite(self.expected[-1]) else None
        self.last = assess(np.array(self.values), spec, expected=exp, recent=self.recent, drift_window=self.drift_window)
        return self.last


def corroborated(risks) -> float:
    """Asset risk from several channels: the worst channel, raised by a second channel agreeing.

    One channel alone tops out around 0.7 ("high"); reaching "critical" needs a second
    channel to corroborate. Used by every multi-channel agent.
    """
    r = sorted((float(x) for x in risks), reverse=True)
    if not r:
        return 0.0
    second = r[1] if len(r) > 1 else r[0]
    return 0.7 * r[0] + 0.3 * second
