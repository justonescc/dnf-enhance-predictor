import pytest
from app.models.hmm_model import HMMPredictor


def test_short_sequence_returns_base_rate():
    h = HMMPredictor()
    prob, state = h.predict(["S", "F", "S"], base_rate=0.5)
    assert prob == 0.5
    assert state == "normal"


def test_sufficient_sequence_returns_probability():
    h = HMMPredictor()
    prob, state = h.predict(["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"], base_rate=0.5)
    assert 0.0 <= prob <= 1.0
    assert state in ("lucky", "normal", "unlucky")


def test_all_success_sequence():
    h = HMMPredictor()
    prob, state = h.predict(["S"] * 10, base_rate=0.5)
    assert prob > 0.5
    assert state == "lucky"


def test_all_failure_sequence():
    h = HMMPredictor()
    prob, state = h.predict(["F"] * 10, base_rate=0.5)
    assert prob < 0.5
    assert state == "unlucky"


def test_predict_with_custom_base():
    h = HMMPredictor()
    prob, _ = h.predict(["S", "F"] * 6, base_rate=0.3)
    assert 0.0 <= prob <= 1.0


def test_get_trend():
    h = HMMPredictor()
    trend = h.get_trend(["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"], base_rate=0.5)
    assert len(trend) == 10
    for t in trend:
        assert 0.0 <= t["prob"] <= 1.0