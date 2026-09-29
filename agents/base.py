"""The one interface every Pavilion Cerebro agent implements.

Pavilion Cerebro is one platform, not a bag of point tools: every agent, whether it watches
cracks, internal sensor telemetry, batteries or a chiller, does the same three things.

  1. ingest its own data source (the only source-specific code an agent owns),
  2. turn one new observation into a calibrated 0-1 risk score plus evidence,
  3. hand the coordinator a standard `AgentReport`.

The coordinator never looks inside an agent. Adding a subsystem later means writing
one more `BaseAgent` subclass, not touching fusion, prioritization or mitigation.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterator, List, Optional


def band(risk: float) -> str:
    """Severity band shared by every agent, the coordinator and the UI."""
    if risk >= 0.8:
        return "critical"
    if risk >= 0.6:
        return "high"
    if risk >= 0.35:
        return "elevated"
    return "normal"


@dataclass
class AgentReport:
    """The standardized report: {agent_id, subsystem, risk_score, confidence, evidence, timestamp}.

    `asset_id`, `zone`, `headline` and `metrics` are optional display fields; the coordinator
    keys concerns by (agent_id, asset_id) so one agent can watch several assets.
    """

    agent_id: str
    subsystem: str
    risk_score: float
    confidence: float
    evidence: Dict[str, Any]
    timestamp: str
    asset_id: str = ""
    zone: str = ""
    headline: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.risk_score = round(float(min(1.0, max(0.0, self.risk_score))), 4)
        self.confidence = round(float(min(1.0, max(0.0, self.confidence))), 4)

    @property
    def band(self) -> str:
        return band(self.risk_score)

    @property
    def key(self) -> str:
        return f"{self.agent_id}:{self.asset_id or self.subsystem}"

    def as_dict(self) -> dict:
        d = asdict(self)
        d["band"] = self.band
        d["key"] = self.key
        return d


class BaseAgent(ABC):
    """Shared agent contract.

    `observations()` is the source-specific loader: it yields real readings from the
    agent's dataset in the order they would arrive live. `observe()` is the inference
    step: one observation in, a list of `AgentReport`s out (one per watched asset).
    `stream()` glues them together for replay.
    """

    agent_id: str = ""
    subsystem: str = ""
    name: str = ""
    description: str = ""
    data_source: str = ""

    def __init__(self, clock=None) -> None:
        # the dashboard injects a simulated clock so every report carries replay time
        self.clock = clock or (lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

    @abstractmethod
    def observations(self) -> Iterator[Any]:
        """Yield real readings from this agent's data source, in arrival order."""

    @abstractmethod
    def observe(self, obs: Any) -> List[AgentReport]:
        """Ingest one reading, return the current report(s)."""

    def stream(self) -> Iterator[List[AgentReport]]:
        for obs in self.observations():
            yield self.observe(obs)

    def describe(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "subsystem": self.subsystem,
            "name": self.name,
            "description": self.description,
            "data_source": self.data_source,
        }

    def report(self, *, risk: float, confidence: float, evidence: dict, asset_id: str = "", zone: str = "", headline: str = "", metrics: Optional[dict] = None) -> AgentReport:
        return AgentReport(
            agent_id=self.agent_id,
            subsystem=self.subsystem,
            risk_score=risk,
            confidence=confidence,
            evidence=evidence,
            timestamp=self.clock(),
            asset_id=asset_id,
            zone=zone,
            headline=headline,
            metrics=metrics or {},
        )
