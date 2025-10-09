from src.risk.limits import LimitMonitor, LossState


def test_limit_monitor_halts_on_portfolio_loss():
    monitor = LimitMonitor(symbol_limit_bp=120, portfolio_limit_bp=350)
    decision = monitor.evaluate(LossState(daily_pnl_bp=-360, weekly_pnl_bp=-100, streak_losses=0))
    assert decision.halt
    assert decision.conservative


def test_limit_monitor_triggers_conservative_on_streak():
    monitor = LimitMonitor(symbol_limit_bp=120, portfolio_limit_bp=350)
    decision = monitor.evaluate(LossState(daily_pnl_bp=-50, weekly_pnl_bp=-50, streak_losses=3))
    assert decision.conservative
    assert not decision.halt
