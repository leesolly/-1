"""Ranking logic applying cost penalties."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class Candidate:
    """Candidate instrument with score and cost estimate."""

    symbol: str
    score: float
    cost_bp: float


class Ranker:
    """Cost-aware ranker."""

    def __init__(self, cost_penalties: Dict[str, float]) -> None:
        self._cost_weight = cost_penalties.get("slippage_bp", 0.0) + cost_penalties.get("fee_bp", 0.0)

    def rank(self, candidates: Iterable[Candidate]) -> List[Candidate]:
        """Sort candidates penalizing by estimated cost."""

        ranked = sorted(
            candidates,
            key=lambda item: item.score - (self._cost_weight * item.cost_bp),
            reverse=True,
        )
        return list(ranked)
