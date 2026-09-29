"""Cross-subsystem prioritization: risk x consequence x time, generalized from the cascade.

The inspection cascade (src/cascade/prioritize.py) ranks findings by
severity x criticality x consequence x urgency, where urgency grows with the age of an
unaddressed finding. Pavilion Cerebro generalizes the same pattern across subsystem types:

  priority = risk_score x consequence(subsystem, asset) x time_factor

  consequence  what failure of this asset costs, 0-1 (life safety > structure > comfort).
               A battery cell at risk 0.6 outranks a crack at risk 0.7 because a battery
               fire is worse than a cosmetic-to-moderate crack. Values are team
               assumptions, listed here so they can be argued with.
  time_factor  freshness x persistence
               freshness   evidence decays when an agent stops reporting (half-life), so a
                           stale reading cannot hold the top of the queue forever;
               persistence an elevated concern that stays open escalates (1.0 -> 2.0 over a
                           day), the cascade's `urgency_for` rule on a replay clock.

Disaster / incident mode drops cost and consequence weighting entirely and triages by
severity alone: severity band first, then raw risk. Same concerns, different ordering.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

BAND_RANK = {"critical": 0, "high": 1, "elevated": 2, "normal": 3}

# consequence of failure, 0-1 (assumption; see README "Prioritization weights")
SUBSYSTEM_CONSEQUENCE = {
    "battery": 1.0,  # fire, life safety, whole-building evacuation
    "structural_visual": 0.8,  # life safety, but damage usually progresses slowly
    "internal_sensor": 0.75,
    "hvac": 0.5,  # comfort, downtime, energy; rarely life safety
}
ASSET_CONSEQUENCE = {
    "upv-L2-slab": 0.85,  # load-bearing concrete
    "bms-floor2-zone2": 0.4,  # office comfort and energy
    "CH-1": 0.55,  # chiller: refrigerant loss is an environmental and downtime cost
}

FRESH_GRACE_H = 3.0  # no decay while an agent is on its normal reporting cadence
FRESH_HALF_LIFE_H = 4.0
PERSIST_FULL_H = 24.0


def consequence(subsystem: str, asset_id: str) -> float:
    return ASSET_CONSEQUENCE.get(asset_id, SUBSYSTEM_CONSEQUENCE.get(subsystem, 0.5))


def time_factor(last_report: datetime, open_since, now: datetime) -> Dict[str, float]:
    age_h = max(0.0, (now - last_report).total_seconds() / 3600.0)
    freshness = 0.5 ** (max(0.0, age_h - FRESH_GRACE_H) / FRESH_HALF_LIFE_H)
    open_h = 0.0 if open_since is None else max(0.0, (now - open_since).total_seconds() / 3600.0)
    persistence = min(2.0, 1.0 + open_h / PERSIST_FULL_H)
    return {"freshness": freshness, "persistence": persistence, "factor": freshness * persistence}


def score(risk: float, subsystem: str, asset_id: str, last_report: datetime, open_since, now: datetime) -> Dict[str, float]:
    c = consequence(subsystem, asset_id)
    t = time_factor(last_report, open_since, now)
    return {"priority": risk * c * t["factor"], "consequence": c, **t}


def rank(concerns: List[dict], mode: str = "normal") -> List[dict]:
    """Order concern dicts (each with risk, band, priority, key). Returns a new ranked list."""
    if mode == "disaster":
        key = lambda c: (BAND_RANK[c["band"]], -c["risk"], c["key"])
    else:
        key = lambda c: (-c["priority"], BAND_RANK[c["band"]], c["key"])
    out = sorted(concerns, key=key)
    for i, c in enumerate(out, start=1):
        c["rank"] = i
    return out
