from src.decision.quantile import QuantileOutput, quantile_guard


def test_quantile_guard_enforces_monotonicity():
    outputs = QuantileOutput(q10=0.7, q50=0.5, q90=0.6)
    adjusted, conservative = quantile_guard(outputs, tolerance=0.05)
    assert adjusted.q10 <= adjusted.q50 <= adjusted.q90
    assert not conservative


def test_quantile_guard_triggers_conservative_when_spread_small():
    outputs = QuantileOutput(q10=0.51, q50=0.52, q90=0.53)
    adjusted, conservative = quantile_guard(outputs, tolerance=0.05)
    assert adjusted.q10 == adjusted.q50 == adjusted.q90
    assert conservative
