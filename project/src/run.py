"""Realtime execution loop orchestrating risk and execution logic."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import random
import yaml

from .decision.entry import EntryCascade, EntryDecision, EntryInputs, conservative_session_delta
from .decision.quantile import QuantileOutput, quantile_guard
from .exec.router import ExecParams, ExecRouter
from .exec.tca import TCAWindow
from .risk.infra import InfraDecision, InfraGuard, InfraSnapshot
from .risk.limits import LimitDecision, LimitMonitor, LossState
from .risk.news import NewsEvent, NewsGate, NewsGateDecision
from .risk.turbo import TurboDecision, TurboGuard, TurboSnapshot
from .utils.hash import combine_hashes, file_hash, stable_hash
from .utils.logger import configure_logger, log_json
from .utils.metrics import RollingMetric

LOGGER = configure_logger("realtime")


@dataclass
class MicroTunerOutput:
    """Normalized output from microtuner packs."""

    price_offset_bp: float
    splits: int
    dt_ms: int
    nonconformal_score: float


class RiskPipeline:
    """Evaluate chained risk gates."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._news = NewsGate(config["risk_mode"]["news"]["hard_window_min"])
        self._infra = InfraGuard()
        turbo_cfg = {
            "adl_rank_max": 2,
            "funding_abs_bp_max": 15,
            "vol_now_q_max": 0.85,
            "cpd_z_max": 3.0,
        }
        self._turbo = TurboGuard()
        self._turbo_cfg = turbo_cfg
        limits_cfg = config["limits"]
        self._limits = LimitMonitor(
            symbol_limit_bp=limits_cfg["symbol"]["daily_loss_bp"],
            portfolio_limit_bp=limits_cfg["portfolio"]["daily_loss_bp"],
        )
        self._latency_guard = config["entry"]["p99_guard_ms"]

    def run(
        self,
        news_events: list[NewsEvent],
        infra_snapshot: InfraSnapshot,
        turbo_snapshot: TurboSnapshot,
        loss_state: LossState,
    ) -> tuple[NewsGateDecision, InfraDecision, TurboDecision, LimitDecision]:
        news_decision = self._news.evaluate(news_events)
        infra_decision = self._infra.evaluate(infra_snapshot, latency_guard_ms=self._latency_guard)
        turbo_decision = self._turbo.evaluate(turbo_snapshot, limits=self._turbo_cfg)
        limit_decision = self._limits.evaluate(loss_state)
        return news_decision, infra_decision, turbo_decision, limit_decision


class MlOutputValidator:
    """Validate ML outputs and fallback to safe defaults."""

    def __init__(self) -> None:
        self._last_valid = MicroTunerOutput(price_offset_bp=0.5, splits=1, dt_ms=120, nonconformal_score=0.0)

    def validate(self, output: MicroTunerOutput) -> MicroTunerOutput:
        """Validate and fallback to last known good output."""

        values = [output.price_offset_bp, output.splits, output.dt_ms]
        if any(math.isnan(float(value)) or math.isinf(float(value)) for value in values):
            return self._last_valid
        delta = abs(output.price_offset_bp - self._last_valid.price_offset_bp)
        if delta > 1.0:
            output = MicroTunerOutput(
                price_offset_bp=self._last_valid.price_offset_bp,
                splits=output.splits,
                dt_ms=output.dt_ms,
                nonconformal_score=output.nonconformal_score,
            )
        self._last_valid = output
        return output


class RealtimeEngine:
    """Orchestrate the entire realtime loop."""

    def __init__(self, config_path: Path) -> None:
        with config_path.open("r", encoding="utf-8") as handle:
            self._config = yaml.safe_load(handle)
        self._risk = RiskPipeline(self._config)
        self._entry = EntryCascade(
            thresholds=self._config["entry"]["thresholds"],
            session_delta=conservative_session_delta(),
            bandit_actions={
                "low_vol": -self._config["bandit"]["actions_by_regime"]["low_vol"],
                "normal": -self._config["bandit"]["actions_by_regime"]["normal"],
                "high_vol": -self._config["bandit"]["actions_by_regime"]["high_vol"],
            },
        )
        self._router = ExecRouter(alpha=0.2)
        self._tca = TCAWindow(horizon_minutes=120)
        self._validator = MlOutputValidator()
        self._latency_metric = RollingMetric(window=100)
        self._failures = 0
        self._conservative_until: float | None = None
        self._model_hash = combine_hashes(
            file_hash(config_path),
            stable_hash(self._config["quantile"]),
        )

    def _conservative_mode(self) -> bool:
        now = time.time()
        if self._conservative_until and now < self._conservative_until:
            return True
        if self._conservative_until and now >= self._conservative_until:
            self._conservative_until = None
            self._failures = 0
        return False

    def _trigger_conservative(self) -> None:
        self._failures += 1
        if self._failures >= 3:
            self._conservative_until = time.time() + 300

    def loop_once(
        self,
        features: EntryInputs,
        coverage_error: float,
        news_events: list[NewsEvent],
        infra_snapshot: InfraSnapshot,
        turbo_snapshot: TurboSnapshot,
        loss_state: LossState,
        quantiles: QuantileOutput,
        tuner_output: MicroTunerOutput,
    ) -> Dict[str, Any]:
        """Process a single realtime cycle."""

        news_decision, infra_decision, turbo_decision, limit_decision = self._risk.run(
            news_events=news_events,
            infra_snapshot=infra_snapshot,
            turbo_snapshot=turbo_snapshot,
            loss_state=loss_state,
        )
        conservative = any(
            decision.conservative for decision in [news_decision, infra_decision, turbo_decision, limit_decision]
        )
        halt = limit_decision.halt or news_decision.block_new
        entry_decision = self._entry.evaluate(features, coverage_error=coverage_error)
        quantiles_adjusted, quantile_conservative = quantile_guard(quantiles, tolerance=0.02)
        conservative = conservative or quantile_conservative or self._conservative_mode()
        if halt:
            entry_decision = EntryDecision(
                accept=False,
                threshold=entry_decision.threshold,
                stage_probability=entry_decision.stage_probability,
                decision_basis=entry_decision.decision_basis,
            )
        validated_output = self._validator.validate(tuner_output)
        exec_params = self._router.smooth(
            ExecParams(
                price_offset_bp=validated_output.price_offset_bp,
                splits=validated_output.splits,
                dt_ms=validated_output.dt_ms,
            )
        )
        self._tca.update(validated_output.price_offset_bp)
        budget_bp = self._tca.budget()
        latency_ms = random.uniform(0.1, 0.5)
        self._latency_metric.add(latency_ms)
        if self._latency_metric.p99() > self._config["entry"]["p99_guard_ms"]:
            conservative = True
        if not entry_decision.accept or halt:
            self._trigger_conservative()
        else:
            self._failures = 0
        audit_payload = {
            "model_hash": self._model_hash,
            "config_hash": stable_hash(self._config),
            "nonconformal_score": validated_output.nonconformal_score,
            "decision_basis": entry_decision.decision_basis,
        }
        log_json(
            LOGGER,
            level=20,
            message="order_intent",
            entry_accept=entry_decision.accept and not halt,
            exec_params=exec_params.__dict__,
            budget_bp=budget_bp,
            conservative=conservative,
            audit=audit_payload,
        )
        return {
            "risk": (news_decision, infra_decision, turbo_decision, limit_decision),
            "entry": entry_decision,
            "quantiles": quantiles_adjusted,
            "exec": exec_params,
            "budget_bp": budget_bp,
            "conservative": conservative,
            "halt": halt,
        }


def load_config(path: str | Path) -> dict[str, Any]:
    """Load YAML configuration."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
