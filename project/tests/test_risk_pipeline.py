from src.risk.infra import InfraGuard, InfraSnapshot
from src.risk.news import NewsEvent, NewsGate
from src.risk.turbo import TurboGuard, TurboSnapshot


def test_news_gate_blocks_high_severity():
    gate = NewsGate(hard_window_min=15)
    decision = gate.evaluate([NewsEvent(severity="high", minutes_since=5)])
    assert decision.block_new
    assert decision.conservative


def test_infra_guard_flags_latency_exceedance():
    guard = InfraGuard()
    decision = guard.evaluate(
        snapshot=InfraSnapshot(error_rate=0.0, ws_gap_rate=0.0, latency_p99_ms=1.1),
        latency_guard_ms=0.9,
    )
    assert decision.conservative


def test_turbo_guard_enforces_limits():
    guard = TurboGuard()
    decision = guard.evaluate(
        TurboSnapshot(adl_rank=4, funding_bp=20, vol_quantile=0.9, cpd_score=3.5),
        limits={"adl_rank_max": 3, "funding_abs_bp_max": 15, "vol_now_q_max": 0.85, "cpd_z_max": 3.0},
    )
    assert not decision.turbo_allowed
