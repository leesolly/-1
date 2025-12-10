"""Simplified Bybit adapter stubs for REST and WebSocket interactions."""

from __future__ import annotations

import asyncio
import collections
from dataclasses import dataclass
from typing import Deque, Optional

import httpx


@dataclass
class OrderRequest:
    """A minimal order payload."""

    symbol: str
    side: str
    qty: float
    price: float
    time_in_force: str
    idempotency_key: str


@dataclass
class OrderResponse:
    """Response structure for order operations."""

    success: bool
    status: str
    error: Optional[str]


class DuplicateFilter:
    """Filter to avoid processing duplicate messages."""

    def __init__(self, maxlen: int = 1000) -> None:
        self._seen: Deque[str] = collections.deque(maxlen=maxlen)

    def check(self, identifier: str) -> bool:
        """Return True if identifier is new."""

        if identifier in self._seen:
            return False
        self._seen.append(identifier)
        return True


class Reconnector:
    """Handle exponential backoff reconnections."""

    def __init__(self, backoff: tuple[int, ...]) -> None:
        self._backoff = backoff

    async def reconnect(self, attempt: int) -> None:
        """Sleep for the backoff duration corresponding to the attempt."""

        index = min(attempt, len(self._backoff) - 1)
        await asyncio.sleep(self._backoff[index])


class BybitREST:
    """Minimal REST client with idempotency support."""

    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None) -> None:
        self._base_url = base_url
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=2.0)

    async def place_order(self, request: OrderRequest) -> OrderResponse:
        """Send an order placement request with idempotency header."""

        headers = {"X-IDEMPOTENCY-KEY": request.idempotency_key}
        try:
            response = await self._client.post(
                "/v5/order/create",
                json={
                    "symbol": request.symbol,
                    "side": request.side,
                    "qty": request.qty,
                    "price": request.price,
                    "timeInForce": request.time_in_force,
                },
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            return OrderResponse(success=False, status="error", error=str(error))
        payload = response.json()
        success = payload.get("retCode", 0) == 0
        status = payload.get("result", {}).get("orderStatus", "unknown")
        return OrderResponse(success=success, status=status, error=None)


class SequenceReconciler:
    """Reconcile websocket sequence numbers and detect gaps."""

    def __init__(self, seq_gap_max: int, duplicate_filter: DuplicateFilter) -> None:
        self._seq_gap_max = seq_gap_max
        self._duplicate_filter = duplicate_filter
        self._last_seq: Optional[int] = None

    def check(self, identifier: str, sequence: int) -> bool:
        """Return True when the message should be processed."""

        if not self._duplicate_filter.check(identifier):
            return False
        if self._last_seq is None:
            self._last_seq = sequence
            return True
        gap = sequence - self._last_seq
        if gap < 0 or gap > self._seq_gap_max:
            self._last_seq = sequence
            return False
        self._last_seq = sequence
        return True
