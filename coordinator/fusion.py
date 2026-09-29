"""The coordinator: every agent reports here, and only here.

It keeps the latest standardized report per (agent, asset), fuses them into one
whole-building picture, ranks concerns across subsystems (prioritization.py), fires
simulated mitigations (mitigation.py), and keeps an incident feed. It never imports an
agent class: anything that emits an `AgentReport` can join the swarm.
"""

from __future__ import annotations

import time
from collections import deque
from datetime import datetime
from typing import Deque, Dict, List, Optional

from agents.base import AgentReport, band

from . import prioritization as P
from .mitigation import MitigationEngine


class Concern:
    def __init__(self, report: AgentReport, now: datetime) -> None:
        self.report = report
        self.last_seen = now
        self.open_since: Optional[datetime] = None
        self.history: Deque[float] = deque(maxlen=120)
        self.logged_band = "normal"
        self.logged_risk = 0.0


class Coordinator:
    def __init__(self, feed_len: int = 200) -> None:
        self.concerns: Dict[str, Concern] = {}
        self.mitigation = MitigationEngine()
        self.feed: Deque[dict] = deque(maxlen=feed_len)
        self.mode = "normal"
        self.now: Optional[datetime] = None
        self.tick = 0
        self.rerank_ms: List[float] = []
        self.last_rerank: Optional[dict] = None
        self.reports_ingested = 0

    # -- ingestion -----------------------------------------------------------

    def ingest(self, report: AgentReport, now: datetime, tick: int) -> None:
        self.now, self.tick = now, tick
        self.reports_ingested += 1
        c = self.concerns.get(report.key)
        if c is None:
            c = self.concerns[report.key] = Concern(report, now)
        c.report, c.last_seen = report, now
        c.history.append(report.risk_score)
        # a concern is "open" while elevated or worse; persistence escalation counts from here
        if report.risk_score >= 0.35:
            c.open_since = c.open_since or now
        elif report.risk_score < 0.25:
            c.open_since = None
        b = report.band
        if b != c.logged_band or abs(report.risk_score - c.logged_risk) >= 0.2:
            if not (b == "normal" and c.logged_band == "normal"):
                self._event("report", report, f"{report.headline}", extra={"band": b, "prev_band": c.logged_band})
            c.logged_band, c.logged_risk = b, report.risk_score
        ev = self.mitigation.evaluate(report, report.timestamp, tick)
        if ev:
            self.feed.appendleft(ev)

    def _event(self, kind: str, report: AgentReport, text: str, extra: Optional[dict] = None) -> None:
        self.feed.appendleft({"type": kind, "time": report.timestamp, "tick": self.tick, "agent_id": report.agent_id, "subsystem": report.subsystem,
                              "asset_id": report.asset_id, "zone": report.zone, "risk": report.risk_score, "text": text, **(extra or {})})

    # -- fusion --------------------------------------------------------------

    def concern_rows(self) -> List[dict]:
        rows = []
        for k, c in self.concerns.items():
            r = c.report
            s = P.score(r.risk_score, r.subsystem, r.asset_id, c.last_seen, c.open_since, self.now or c.last_seen)
            rows.append({"key": k, "agent_id": r.agent_id, "subsystem": r.subsystem, "asset_id": r.asset_id, "zone": r.zone, "headline": r.headline,
                         "risk": r.risk_score, "confidence": r.confidence, "band": r.band, "priority": round(s["priority"], 4),
                         "consequence": s["consequence"], "freshness": round(s["freshness"], 3), "persistence": round(s["persistence"], 3),
                         "state": self.mitigation.state(k), "history": list(c.history)[-60:], "metrics": r.metrics, "timestamp": r.timestamp})
        return rows

    def ranked(self) -> List[dict]:
        return P.rank(self.concern_rows(), self.mode)

    def health(self, rows: Optional[List[dict]] = None) -> dict:
        """Whole-building health 0-100 and per-subsystem health (worst asset in each)."""
        rows = rows if rows is not None else self.concern_rows()
        if not rows:
            return {"building": 100.0, "subsystems": {}}
        weighted = [r["risk"] * r["consequence"] for r in rows]
        agg = 0.6 * max(weighted) + 0.4 * sum(weighted) / len(weighted)
        subs: Dict[str, float] = {}
        for r in rows:
            subs[r["subsystem"]] = min(subs.get(r["subsystem"], 100.0), round(100 * (1 - r["risk"]), 1))
        return {"building": round(100 * (1 - agg), 1), "band": band(agg / 0.85 if agg < 0.85 else 1.0), "subsystems": subs}

    def set_mode(self, mode: str) -> dict:
        """Switch ranking logic; returns how the order changed and how long re-triage took."""
        assert mode in ("normal", "disaster")
        before = [r["key"] for r in self.ranked()]
        t0 = time.perf_counter()
        self.mode = mode
        after_rows = self.ranked()
        ms = (time.perf_counter() - t0) * 1000.0
        after = [r["key"] for r in after_rows]
        self.rerank_ms.append(ms)
        moved = [{"key": k, "from": before.index(k) + 1, "to": after.index(k) + 1} for k in after if k in before and before.index(k) != after.index(k)]
        self.last_rerank = {"mode": mode, "ms": round(ms, 3), "moved": moved, "tick": self.tick}
        self.feed.appendleft({"type": "mode", "time": (self.now.isoformat(timespec="minutes") if self.now else ""), "tick": self.tick,
                              "text": ("DISASTER MODE ON: triage by severity only" if mode == "disaster" else "Normal mode: consequence-weighted ranking restored")
                              + f" ({len(moved)} concerns re-ranked in {ms:.2f} ms)"})
        return self.last_rerank

    def snapshot(self) -> dict:
        rows = self.ranked()
        return {"mode": self.mode, "tick": self.tick, "sim_time": self.now.isoformat(timespec="minutes") if self.now else None, "health": self.health(rows),
                "concerns": rows, "feed": list(self.feed)[:80], "mitigations": [e for e in self.mitigation.log if e["type"] == "mitigation"][-20:],
                "last_rerank": self.last_rerank, "reports_ingested": self.reports_ingested,
                "rerank_ms_avg": round(sum(self.rerank_ms) / len(self.rerank_ms), 3) if self.rerank_ms else None}
