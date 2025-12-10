"""Retry policy modeling."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """Configuration for retry scheduling."""

    attempts: int
    base_timeout_ms: int
    backoff_ms: int

    def schedule(self) -> list[int]:
        """Return timeout schedule for attempts."""

        return [self.base_timeout_ms + (self.backoff_ms * index) for index in range(self.attempts)]
