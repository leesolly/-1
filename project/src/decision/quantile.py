"""Quantile post-processing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class QuantileOutput:
    """Container for monotonic quantile predictions."""

    q10: float
    q50: float
    q90: float

    def enforce_monotonic(self) -> "QuantileOutput":
        """Return a new instance with monotonicity enforced."""

        lower = min(self.q10, self.q50, self.q90)
        upper = max(self.q10, self.q50, self.q90)
        median = sorted([self.q10, self.q50, self.q90])[1]
        return QuantileOutput(q10=lower, q50=median, q90=upper)

    def apply_conformal(self, offset: float) -> "QuantileOutput":
        """Apply a symmetric conformal offset."""

        return QuantileOutput(
            q10=self.q10 - offset,
            q50=self.q50,
            q90=self.q90 + offset,
        )

    def spread(self) -> float:
        """Return the q90-q10 spread."""

        return self.q90 - self.q10


def quantile_guard(outputs: QuantileOutput, tolerance: float) -> Tuple[QuantileOutput, bool]:
    """Enforce guardrails ensuring the spread stays within tolerance."""

    adjusted = outputs.enforce_monotonic()
    spread = adjusted.spread()
    needs_conservative_mode = spread < tolerance
    if needs_conservative_mode:
        midpoint = (adjusted.q90 + adjusted.q10) / 2
        adjusted = QuantileOutput(q10=midpoint, q50=midpoint, q90=midpoint)
    return adjusted, needs_conservative_mode
