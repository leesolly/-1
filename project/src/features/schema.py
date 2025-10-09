"""Feature schema registry and hashing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from ..utils.hash import stable_hash


@dataclass(frozen=True)
class FeatureDefinition:
    """Describe a single feature specification."""

    name: str
    description: str
    aggregation: str


class FeatureSchema:
    """Maintain a registry of feature definitions."""

    def __init__(self) -> None:
        self._definitions: Dict[str, FeatureDefinition] = {}

    def register(self, definition: FeatureDefinition) -> None:
        """Register a new feature, replacing any existing entry."""

        self._definitions[definition.name] = definition

    def hash(self) -> str:
        """Return a deterministic schema hash."""

        payload = {
            name: {
                "description": definition.description,
                "aggregation": definition.aggregation,
            }
            for name, definition in sorted(self._definitions.items())
        }
        return stable_hash(payload)

    def names(self) -> Iterable[str]:
        """Yield feature names in sorted order."""

        return sorted(self._definitions)
