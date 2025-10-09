"""News severity gating."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class NewsEvent:
    """News event representation."""

    severity: str
    minutes_since: float


@dataclass
class NewsGateDecision:
    """Decision outcome after evaluating news events."""

    block_new: bool
    conservative: bool


class NewsGate:
    """Evaluate news events against configured windows."""

    def __init__(self, hard_window_min: int) -> None:
        self._hard_window = hard_window_min

    def evaluate(self, events: Iterable[NewsEvent]) -> NewsGateDecision:
        """Evaluate the news tape and return gating decisions."""

        block = False
        conservative = False
        for event in events:
            if event.severity == "high" and event.minutes_since <= self._hard_window:
                block = True
                conservative = True
            elif event.severity == "medium" and event.minutes_since <= self._hard_window:
                conservative = True
        return NewsGateDecision(block_new=block, conservative=conservative)
