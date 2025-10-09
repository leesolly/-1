"""Entry cascade evaluation logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping

from ..utils.hash import stable_hash


@dataclass
class EntryInputs:
    """Container of features required for entry evaluation."""

    stage1: float
    stage2: float
    direction_probability: float
    regime: str
    session: str


@dataclass
class EntryDecision:
    """Final decision output for downstream execution."""

    accept: bool
    threshold: float
    stage_probability: float
    decision_basis: str


class EntryCascade:
    """Entry cascade implementing strategy thresholds and bandit shifts."""

    def __init__(
        self,
        thresholds: Mapping[str, float],
        session_delta: Mapping[str, float],
        bandit_actions: Mapping[str, float],
    ) -> None:
        self._thresholds = thresholds
        self._session_delta = session_delta
        self._bandit_actions = bandit_actions

    def evaluate(self, features: EntryInputs, coverage_error: float) -> EntryDecision:
        """Evaluate an entry candidate."""

        base_threshold = self._thresholds["stage2"]
        bandit_shift = self._bandit_actions.get(features.regime, 0.0)
        session_shift = self._session_delta.get(features.session, 0.0)
        conservative_shift = 0.02 if coverage_error > 0.05 else 0.0
        final_threshold = base_threshold + bandit_shift + session_shift + conservative_shift
        stage_probability = min(max(features.stage2, 0.0), 1.0)
        accept = (
            features.stage1 >= self._thresholds["stage1"]
            and features.direction_probability >= 0.15
            and stage_probability >= final_threshold
        )
        basis_payload = {
            "threshold": final_threshold,
            "stage_probability": stage_probability,
            "regime": features.regime,
            "session": features.session,
        }
        return EntryDecision(
            accept=accept,
            threshold=final_threshold,
            stage_probability=stage_probability,
            decision_basis=stable_hash(basis_payload),
        )


def conservative_session_delta() -> Dict[str, float]:
    """Return hard-coded session adjustments."""

    return {"ASIA": 0.01, "EU": 0.0, "US": -0.01}
