from src.decision.entry import EntryCascade, EntryInputs, conservative_session_delta


def test_entry_accepts_when_threshold_met():
    cascade = EntryCascade(
        thresholds={"stage1": 0.5, "stage2": 0.6},
        session_delta=conservative_session_delta(),
        bandit_actions={"normal": 0.0},
    )
    decision = cascade.evaluate(
        features=EntryInputs(stage1=0.7, stage2=0.65, direction_probability=0.2, regime="normal", session="EU"),
        coverage_error=0.01,
    )
    assert decision.accept
    assert decision.threshold == 0.6


def test_entry_rejects_with_high_coverage_error():
    cascade = EntryCascade(
        thresholds={"stage1": 0.5, "stage2": 0.6},
        session_delta=conservative_session_delta(),
        bandit_actions={"normal": 0.0},
    )
    decision = cascade.evaluate(
        features=EntryInputs(stage1=0.7, stage2=0.61, direction_probability=0.2, regime="normal", session="EU"),
        coverage_error=0.08,
    )
    assert not decision.accept
    assert decision.threshold == 0.62
