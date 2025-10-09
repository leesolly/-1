"""Feature resampling logic tailored for multi-horizon inputs."""

from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import Deque, Iterable


@dataclass
class ResampledFeature:
    """Container for resampled values and meta-information."""

    values: Deque[float]
    window: int

    def push(self, value: float) -> None:
        """Insert a value respecting the configured window size."""

        self.values.append(value)
        if len(self.values) > self.window:
            self.values.popleft()

    def normalized(self) -> float:
        """Return a normalized value using min-max scaling within the window."""

        if not self.values:
            return 0.0
        minimum = min(self.values)
        maximum = max(self.values)
        if minimum == maximum:
            return 0.0
        latest = self.values[-1]
        return (latest - minimum) / (maximum - minimum)


def ewma(sequence: Iterable[float], alpha: float) -> float:
    """Compute an exponentially weighted moving average."""

    alpha = max(0.0, min(alpha, 1.0))
    iterator = iter(sequence)
    try:
        result = next(iterator)
    except StopIteration:
        return 0.0
    for value in iterator:
        result = (alpha * value) + ((1.0 - alpha) * result)
    return result


def build_resampler(window: int) -> ResampledFeature:
    """Factory helper for feature resamplers."""

    return ResampledFeature(values=collections.deque(maxlen=window), window=window)
