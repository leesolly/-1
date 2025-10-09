"""Turbo mode guardrails."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TurboSnapshot:
    """Metrics required for turbo gating."""

    adl_rank: int
    funding_bp: float
    vol_quantile: float
    cpd_score: float


@dataclass
class TurboDecision:
    """Turbo guard decision result."""

    turbo_allowed: bool
    conservative: bool


class TurboGuard:
    """Decide whether turbo overrides may be applied."""

    def evaluate(self, snapshot: TurboSnapshot, limits: dict[str, float]) -> TurboDecision:
        """Evaluate metrics against thresholds."""

        adl_ok = snapshot.adl_rank <= limits.get("adl_rank_max", 3)
        funding_ok = abs(snapshot.funding_bp) <= limits.get("funding_abs_bp_max", 15)
        vol_ok = snapshot.vol_quantile <= limits.get("vol_now_q_max", 0.85)
        cpd_ok = snapshot.cpd_score <= limits.get("cpd_z_max", 3.0)
        turbo_allowed = all([adl_ok, funding_ok, vol_ok, cpd_ok])
        conservative = not turbo_allowed
        return TurboDecision(turbo_allowed=turbo_allowed, conservative=conservative)
