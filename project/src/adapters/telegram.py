"""Telegram adapter for notifications."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict

import httpx


@dataclass
class TelegramConfig:
    """Telegram configuration values."""

    token: str
    chat_id: str


class TelegramClient:
    """Send structured notifications to Telegram."""

    def __init__(self, config: TelegramConfig) -> None:
        self._config = config
        self._logger = logging.getLogger(__name__)

    async def send(self, message: str, payload: Dict[str, Any] | None = None) -> None:
        """Send a message asynchronously."""

        text = message
        if payload:
            text = f"{message}\n```{payload}```"
        url = f"https://api.telegram.org/bot{self._config.token}/sendMessage"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                url,
                json={"chat_id": self._config.chat_id, "text": text, "parse_mode": "Markdown"},
            )
            if response.status_code != 200:
                self._logger.error("telegram_error", extra={"status": response.status_code})
