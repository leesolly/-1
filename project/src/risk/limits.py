"""Loss limit tracking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LossState:
    """Track drawdowns and enforce conservative modes."""

    daily_pnl_bp: float
    weekly_pnl_bp: float
    streak_losses: int


@dataclass
class LimitDecision:
    """Decision based on configured hard limits."""

    halt: bool
    conservative: bool


class LimitMonitor:
    """Monitor soft and hard loss limits."""

    def __init__(self, symbol_limit_bp: int, portfolio_limit_bp: int) -> None:
        self._symbol_limit = symbol_limit_bp
        self._portfolio_limit = portfolio_limit_bp

    def evaluate(self, state: LossState) -> LimitDecision:
        """Return limit decisions from the tracked state."""

        halt = state.daily_pnl_bp <= -self._portfolio_limit or state.weekly_pnl_bp <= -self._portfolio_limit
        conservative = halt or state.daily_pnl_bp <= -self._symbol_limit or state.streak_losses >= 3
        return LimitDecision(halt=halt, conservative=conservative)
