"""Per-call cost and latency logging. Prices are USD per million tokens (input, output).

Sources: docs/research/06_vlm_tech_landscape_2026.md key numbers table (fetched 2026-09-24)
and the Claude API reference loaded in-session. Local models cost $0 in API terms.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PRICES_PER_MTOK = {
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-fable-5-1": (10.0, 50.0),
}


def usd_for(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICES_PER_MTOK:
        return 0.0
    pin, pout = PRICES_PER_MTOK[model]
    return (input_tokens * pin + output_tokens * pout) / 1_000_000


@dataclass
class CallLog:
    path: Optional[Path] = None
    rows: list = field(default_factory=list)

    def record(
        self,
        *,
        stage: str,
        model: str,
        image_id: str,
        input_tokens: int,
        output_tokens: int,
        seconds: float,
        usd: Optional[float] = None,
        note: str = "",
    ) -> dict:
        row = {
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "stage": stage,
            "model": model,
            "image_id": image_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "usd": usd if usd is not None else usd_for(model, input_tokens, output_tokens),
            "seconds": round(seconds, 3),
            "note": note,
        }
        self.rows.append(row)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n")
        return row

    def totals(self) -> dict:
        out: dict = {}
        for r in self.rows:
            s = out.setdefault(r["stage"], {"calls": 0, "usd": 0.0, "seconds": 0.0, "input_tokens": 0, "output_tokens": 0})
            s["calls"] += 1
            s["usd"] += r["usd"]
            s["seconds"] += r["seconds"]
            s["input_tokens"] += r["input_tokens"]
            s["output_tokens"] += r["output_tokens"]
        return out


class Timer:
    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self.t0
