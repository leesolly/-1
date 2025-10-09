"""Transaction cost analysis utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TCAWindow:
    """Rolling window for impact modeling."""

    horizon_minutes: int
    impact_bp: float = 0.0

    def update(self, slippage_bp: float) -> None:
        """Update the impact estimate with a new observation."""

        self.impact_bp = (0.2 * slippage_bp) + (0.8 * self.impact_bp)

    def budget(self) -> float:
        """Return the execution budget in basis points."""

        return max(1.5, min(3.5, self.impact_bp))
