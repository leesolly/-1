"""Position sizing utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SizingInputs:
    """Inputs required to compute a Kelly-capped size."""

    equity: float
    edge: float
    volatility: float
    kelly_cap: float
    risk_mode_multiplier: float = 1.0


def kelly_size(inputs: SizingInputs) -> float:
    """Return a Kelly-based fraction bounded by configured caps."""

    if inputs.volatility <= 0:
        return 0.0
    raw = (inputs.edge / max(inputs.volatility, 1e-6)) * inputs.risk_mode_multiplier
    return max(0.0, min(inputs.kelly_cap, raw)) * inputs.equity
