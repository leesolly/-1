"""Execution router applying EMA smoothing to parameters."""

from __future__ import annotations

from dataclasses import dataclass

from ..utils.time import ema


@dataclass
class ExecParams:
    """Execution parameters derived from microtuner outputs."""

    price_offset_bp: float
    splits: int
    dt_ms: int


class ExecRouter:
    """Apply EMA smoothing and guardrails to execution parameters."""

    def __init__(self, alpha: float) -> None:
        self._alpha = alpha
        self._previous = ExecParams(price_offset_bp=0.0, splits=1, dt_ms=100)

    def smooth(self, params: ExecParams) -> ExecParams:
        """Apply smoothing to execution parameters."""

        smoothed_offset = ema(self._previous.price_offset_bp, params.price_offset_bp, self._alpha)
        smoothed_splits = int(round(ema(float(self._previous.splits), float(params.splits), self._alpha)))
        smoothed_dt = int(round(ema(float(self._previous.dt_ms), float(params.dt_ms), self._alpha)))
        self._previous = ExecParams(
            price_offset_bp=smoothed_offset,
            splits=max(1, smoothed_splits),
            dt_ms=max(50, smoothed_dt),
        )
        return self._previous
