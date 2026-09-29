"""Self-healing layer: threshold-triggered mitigation actions. SIMULATED.

When an asset's risk stays critical, the coordinator fires the action mapped to its
subsystem and records it. Nothing here talks to real building controls: an action is a
log entry plus a state change the dashboard renders (e.g. chiller CH-1 "ISOLATED",
backup CH-2 "ONLINE"). Integrating a BACnet/Modbus or BMS vendor API would replace
`_apply` and nothing else.

Rules
  critical  risk >= 0.8 for 2 consecutive reports -> automated action, fires once per episode
  high      risk >= 0.6 for 3 consecutive reports -> advisory work order (no automation)
  re-arm    after risk < 0.5 for 8 consecutive reports (hysteresis: a daily comfort cycle must not re-fire it)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

CRITICAL, HIGH, REARM = 0.8, 0.6, 0.5

ACTIONS = {
    "battery": {
        "action": "Throttled charge rate on {asset} to 50% and paged facilities team",
        "state": "CHARGE 50% / PAGED",
        "advisory": "Work order: schedule capacity test and IR scan for {asset}",
    },
    "hvac": {
        "action": "Shut down affected chiller loop {asset} and switched cooling to backup chiller CH-2",
        "state": "ISOLATED / CH-2 ONLINE",
        "advisory": "Work order: refrigerant leak check and charge verification on {asset}",
    },
    "internal_sensor": {
        "action": "Flagged {zone} for structural inspection and restricted access",
        "state": "ACCESS RESTRICTED",
        "advisory": "Work order: confirm readings with a second NDT method at {zone}",
    },
    "internal_sensor:bms": {
        "action": "Opened priority HVAC work order for {zone} and raised zone to comfort-alarm mode",
        "state": "COMFORT ALARM",
        "advisory": "Work order: check AC unit output and setpoints in {zone}",
    },
    "structural_visual": {
        "action": "Flagged {zone} for structural inspection and restricted access",
        "state": "ACCESS RESTRICTED",
        "advisory": "Work order: inspector to measure crack width and map extent at {zone}",
    },
}


def _rule(subsystem: str, asset_id: str) -> dict:
    if subsystem == "internal_sensor" and asset_id.startswith("bms"):
        return ACTIONS["internal_sensor:bms"]
    return ACTIONS[subsystem]


@dataclass
class AssetLatch:
    crit_run: int = 0
    high_run: int = 0
    low_run: int = 0
    fired: bool = False
    advised: bool = False
    state: str = "MONITORING"


@dataclass
class MitigationEngine:
    latches: Dict[str, AssetLatch] = field(default_factory=dict)
    log: List[dict] = field(default_factory=list)

    def evaluate(self, report, when: str, tick: int) -> Optional[dict]:
        """Update latches for one report; return an event dict if an action fired."""
        k = report.key
        lt = self.latches.setdefault(k, AssetLatch())
        r = report.risk_score
        lt.crit_run = lt.crit_run + 1 if r >= CRITICAL else 0
        lt.high_run = lt.high_run + 1 if r >= HIGH else 0
        lt.low_run = lt.low_run + 1 if r < REARM else 0
        rule = _rule(report.subsystem, report.asset_id)
        fmt = {"asset": report.asset_id, "zone": report.zone}
        ev = None
        if lt.crit_run >= 2 and not lt.fired:
            lt.fired = True
            lt.state = rule["state"]
            ev = self._apply("mitigation", report, rule["action"].format(**fmt), when, tick)
        elif lt.high_run >= 3 and not lt.advised and not lt.fired:
            lt.advised = True
            lt.state = "WORK ORDER OPEN"
            ev = self._apply("advisory", report, rule["advisory"].format(**fmt), when, tick)
        elif lt.low_run >= 8 and (lt.fired or lt.advised):
            lt.fired = lt.advised = False
            lt.state = "MONITORING"
            ev = self._apply("rearm", report, f"{report.asset_id} back below threshold; automation re-armed", when, tick)
        return ev

    def _apply(self, kind: str, report, text: str, when: str, tick: int) -> dict:
        ev = {"type": kind, "time": when, "tick": tick, "agent_id": report.agent_id, "subsystem": report.subsystem, "asset_id": report.asset_id,
              "zone": report.zone, "risk": report.risk_score, "text": text, "simulated": True}
        self.log.append(ev)
        return ev

    def state(self, key: str) -> str:
        return self.latches[key].state if key in self.latches else "MONITORING"
