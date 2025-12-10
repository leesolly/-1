"""Time utilities for scheduling and throttling."""

from __future__ import annotations

import asyncio
import datetime as dt
import threading
import time
from contextlib import contextmanager
from typing import Any, Awaitable, Generator, Iterable

import importlib
import importlib.util

_UVLOOP_SPEC = importlib.util.find_spec("uvloop")
if _UVLOOP_SPEC is not None:
    uvloop = importlib.import_module("uvloop")
else:
    class _UvloopStub:
        @staticmethod
        def new_event_loop() -> asyncio.AbstractEventLoop:
            return asyncio.new_event_loop()

    uvloop = _UvloopStub()


class AsyncLoopController:
    """Manage uvloop event loops with explicit lifecycle control."""

    def __init__(self) -> None:
        self._loop = uvloop.new_event_loop()
        self._lock = threading.Lock()

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Return the underlying uvloop instance."""

        return self._loop

    def run_until_complete(self, coro: Awaitable[Any]) -> Any:
        """Run the loop until the coroutine finishes."""

        with self._lock:
            return self._loop.run_until_complete(coro)

    def close(self) -> None:
        """Close the managed loop."""

        with self._lock:
            self._loop.close()


def utc_now() -> dt.datetime:
    """Return an aware UTC timestamp."""

    return dt.datetime.now(tz=dt.timezone.utc)


def to_timestamp(value: dt.datetime | float | int) -> float:
    """Convert a datetime or seconds value to epoch seconds."""

    if isinstance(value, dt.datetime):
        return value.timestamp()
    return float(value)


def ema(previous: float, new: float, alpha: float) -> float:
    """Compute an exponential moving average with numeric guardrails."""

    bounded_alpha = max(0.0, min(alpha, 1.0))
    return (bounded_alpha * new) + ((1.0 - bounded_alpha) * previous)


@contextmanager
def throttle(min_interval: float) -> Generator[None, None, None]:
    """Context manager that enforces a minimum interval between operations."""

    start = dt.datetime.now(tz=dt.timezone.utc)
    try:
        yield
    finally:
        elapsed = (dt.datetime.now(tz=dt.timezone.utc) - start).total_seconds()
        remaining = max(0.0, min_interval - elapsed)
        if remaining:
            time.sleep(remaining)


def sliding_window(values: Iterable[float], window: int) -> list[float]:
    """Compute a simple sliding mean for a sequence."""

    window = max(1, window)
    acc: list[float] = []
    result: list[float] = []
    for value in values:
        acc.append(value)
        if len(acc) > window:
            acc.pop(0)
        result.append(sum(acc) / len(acc))
    return result
