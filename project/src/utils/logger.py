"""Structured logging utilities."""

from __future__ import annotations

import json
import logging
from logging import Logger
from typing import Any


def configure_logger(name: str) -> Logger:
    """Configure and return a structured logger."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt="%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_json(logger: Logger, level: int, message: str, **extra: Any) -> None:
    """Emit a JSON log line with the provided payload."""

    payload = {"message": message, **extra}
    logger.log(level, json.dumps(payload, sort_keys=True))
