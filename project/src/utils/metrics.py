"""Metrics and rolling statistics helpers."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterable


@dataclass
class RollingMetric:
    """Compute rolling averages and quantiles for latency tracking."""

    window: int
    values: Deque[float] = field(default_factory=deque)

    def add(self, value: float) -> None:
        """Add a value to the rolling window."""

        self.values.append(value)
        if len(self.values) > self.window:
            self.values.popleft()

    def mean(self) -> float:
        """Return the arithmetic mean of the tracked values."""

        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    def p99(self) -> float:
        """Return the approximate 99th percentile."""

        if not self.values:
            return 0.0
        sorted_values = sorted(self.values)
        index = min(len(sorted_values) - 1, int(0.99 * (len(sorted_values) - 1)))
        return sorted_values[index]


def exponential_moving_average(values: Iterable[float], alpha: float) -> float:
    """Return the exponential moving average of the sequence."""

    iterator = iter(values)
    try:
        first = next(iterator)
    except StopIteration:
        return 0.0
    ema_value = first
    for value in iterator:
        ema_value = (alpha * value) + ((1 - alpha) * ema_value)
    return ema_value
