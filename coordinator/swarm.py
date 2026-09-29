"""Swarm runtime: owns the agents, a replay clock and the coordinator.

Each tick advances the replay clock by one simulated hour and asks every agent that is
due for its next real observation. Agents that reach the end of their dataset keep their
last report (the coordinator's freshness decay then ages it). The same runtime drives the
live dashboard, the rendered video and the self-check, so all three show identical logic.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from agents.base import BaseAgent
from agents.battery import BatteryAgent
from agents.hvac import HvacAgent
from agents.internal_sensor import InternalSensorAgent
from agents.structural_visual import StructuralVisualAgent

from .fusion import Coordinator

START = datetime(2026, 9, 28, 6, 0)
TICK = timedelta(hours=1)
SCENARIO_TICKS = 150

ROADMAP = [
    {"agent_id": "agent-4", "subsystem": "plumbing", "name": "Plumbing & Water Damage", "status": "Coming soon",
     "note": "No public dataset currently exists for this; requires field data partnership."},
    {"agent_id": "agent-5", "subsystem": "fire_visual", "name": "Fire & Smoke Visual", "status": "Next sprint",
     "note": "Public fire/smoke image datasets exist, not yet integrated."},
    {"agent_id": "agent-6", "subsystem": "lidar_twin", "name": "Laser Scan Digital Twin", "status": "Hardware-dependent",
     "note": "Needs a LiDAR/laser scanner (fixed, drone- or robot-mounted); not simulated with fabricated scan data. "
             "Design: point-cloud diff against a baseline reduces to the same drift/threshold signal every agent already "
             "uses, and scans are triggered reactively when another agent's risk crosses a threshold, not on a blind timer."},
]


class SimClock:
    def __init__(self, start: datetime = START) -> None:
        self.now = start

    def __call__(self) -> str:
        return self.now.isoformat(timespec="minutes")

    def advance(self) -> None:
        self.now += TICK


class Swarm:
    def __init__(self, visual_backend: Optional[str] = None, cadence: Optional[Dict[str, int]] = None) -> None:
        self.clock = SimClock()
        self.agents: List[BaseAgent] = [
            StructuralVisualAgent(self.clock, backend=visual_backend),
            InternalSensorAgent(self.clock),
            BatteryAgent(self.clock, start_cycle=30),
            HvacAgent(self.clock),
        ]
        # ticks between observations: the visual sweep takes a frame every other hour
        self.cadence = cadence or {"agent-0": 2, "agent-1": 1, "agent-2": 1, "agent-3": 1}
        self.streams = {a.agent_id: a.stream() for a in self.agents}
        self.done = set()
        self.coord = Coordinator()
        self.tick = 0
        self.latest: Dict[str, list] = {}

    @property
    def finished(self) -> bool:
        return self.tick >= SCENARIO_TICKS

    def step(self) -> List:
        new = []
        for a in self.agents:
            if a.agent_id in self.done or self.tick % self.cadence[a.agent_id]:
                continue
            try:
                reports = next(self.streams[a.agent_id])
            except StopIteration:
                self.done.add(a.agent_id)
                continue
            for r in reports:
                self.coord.ingest(r, self.clock.now, self.tick)
            self.latest[a.agent_id] = [r.as_dict() for r in reports]
            new += reports
        self.tick += 1
        self.clock.advance()
        self.coord.now = self.clock.now
        return new

    def agent_cards(self) -> List[dict]:
        cards = []
        for a in self.agents:
            d = a.describe()
            d["status"] = "finished replay" if a.agent_id in self.done else "live"
            d["latest"] = self.latest.get(a.agent_id, [])
            if a.agent_id == "agent-0":
                d["backend"] = a.backend
            if a.agent_id == "agent-2":
                # capacity-fade history per cell, for the SOH chart (every 2nd cycle keeps the payload small)
                d["soh_series"] = {c: [[cy, round(100 * cap / 2.0, 2)] for cy, cap in list(zip(st.cycles, st.cap))[::2] + list(zip(st.cycles, st.cap))[-1:]]
                                   for c, st in a.state.items() if st.cycles}
            cards.append(d)
        return cards

    def snapshot(self) -> dict:
        s = self.coord.snapshot()
        s["tick"] = self.tick
        s.update({"agents": self.agent_cards(), "roadmap": ROADMAP, "scenario_ticks": SCENARIO_TICKS, "finished": self.finished,
                  "caption": "Simulated monitoring feed - detection logic and readings are from real public datasets, replayed live."})
        return s
