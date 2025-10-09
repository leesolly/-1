"""Switching threshold adaptation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SwitchStats:
    """Rolling statistics used for adaptation."""

    win_rate: float
    avg_gain_bp: float


class SwitchThreshold:
    """Adapt switching thresholds based on performance."""

    def __init__(self, base: float, clip: tuple[float, float]) -> None:
        self._base = base
        self._clip = clip

    def adapt(self, stats: SwitchStats) -> float:
        """Return the adapted threshold."""

        delta = 0.0
        if stats.win_rate >= 0.55 and stats.avg_gain_bp >= 3.0:
            delta = -0.03
        elif stats.win_rate <= 0.45 and stats.avg_gain_bp <= 0.0:
            delta = 0.05
        threshold = self._base + delta
        return max(self._clip[0], min(self._clip[1], threshold))
