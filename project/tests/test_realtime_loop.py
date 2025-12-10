from pathlib import Path

from src.decision.entry import EntryInputs
from src.decision.quantile import QuantileOutput
from src.risk.infra import InfraSnapshot
from src.risk.limits import LossState
from src.risk.news import NewsEvent
from src.risk.turbo import TurboSnapshot
from src.run import MicroTunerOutput, RealtimeEngine


def test_realtime_loop_enters_conservative_mode(tmp_path: Path):
    config_path = Path("project/configs/base.yaml")
    engine = RealtimeEngine(config_path=config_path)
    features = EntryInputs(stage1=0.3, stage2=0.4, direction_probability=0.1, regime="normal", session="EU")
    quantiles = QuantileOutput(q10=0.1, q50=0.2, q90=0.3)
    news_events = [NewsEvent(severity="medium", minutes_since=1)]
    infra_snapshot = InfraSnapshot(error_rate=0.05, ws_gap_rate=0.05, latency_p99_ms=1.0)
    turbo_snapshot = TurboSnapshot(adl_rank=1, funding_bp=5, vol_quantile=0.5, cpd_score=1.0)
    loss_state = LossState(daily_pnl_bp=-50, weekly_pnl_bp=-10, streak_losses=2)
    tuner_output = MicroTunerOutput(price_offset_bp=0.8, splits=2, dt_ms=130, nonconformal_score=0.1)
    result = engine.loop_once(
        features=features,
        coverage_error=0.06,
        news_events=news_events,
        infra_snapshot=infra_snapshot,
        turbo_snapshot=turbo_snapshot,
        loss_state=loss_state,
        quantiles=quantiles,
        tuner_output=tuner_output,
    )
    assert result["conservative"]
    assert result["halt"] or not result["entry"].accept
