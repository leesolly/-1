"""Contextual bandit helpers for adaptive thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass
class BanditState:
    """State tracking for Thompson-like sampling."""

    counts: Dict[str, int]
    rewards: Dict[str, float]


class RegimeBandit:
    """Simple deterministic bandit using running averages by regime."""

    def __init__(self, actions_by_regime: Dict[str, float]) -> None:
        self._actions = actions_by_regime
        self._state = BanditState(counts={regime: 0 for regime in actions_by_regime}, rewards={regime: 0.0 for regime in actions_by_regime})

    def update(self, regime: str, reward: float) -> None:
        """Update the reward statistics for a regime."""

        self._state.counts[regime] += 1
        self._state.rewards[regime] += reward

    def action(self, regime: str) -> float:
        """Return the action delta for the provided regime."""

        return self._actions.get(regime, 0.0)

    def policy_report(self) -> Dict[str, float]:
        """Return average rewards by regime for observability."""

        report: Dict[str, float] = {}
        for regime, total in self._state.rewards.items():
            count = max(1, self._state.counts[regime])
            report[regime] = total / count
        return report
