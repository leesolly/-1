"""Infrastructure risk checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InfraSnapshot:
    """Current infrastructure state metrics."""

    error_rate: float
    ws_gap_rate: float
    latency_p99_ms: float


@dataclass
class InfraDecision:
    """Infrastructure gating decision."""

    healthy: bool
    conservative: bool


class InfraGuard:
    """Guard that monitors infrastructure health thresholds."""

    def evaluate(self, snapshot: InfraSnapshot, latency_guard_ms: float) -> InfraDecision:
        """Return gating decision based on latency and error statistics."""

        healthy = snapshot.error_rate < 0.02 and snapshot.ws_gap_rate < 0.02
        conservative = snapshot.latency_p99_ms > latency_guard_ms or not healthy
        return InfraDecision(healthy=healthy, conservative=conservative)
