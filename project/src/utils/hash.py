"""Hash helpers for deterministic audit logging."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def stable_hash(payload: Any) -> str:
    """Return a stable hash for nested payloads."""

    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def file_hash(path: str | Path) -> str:
    """Return the SHA256 hash of the provided file path."""

    digest = hashlib.sha256()
    with Path(path).expanduser().open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combine_hashes(*parts: str) -> str:
    """Return a combined hash from already hashed segments."""

    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
    return digest.hexdigest()
