import pytest
from app.models.markov import MarkovPredictor


def test_empty_results_returns_base_rate():
    m = MarkovPredictor(order=2)
    assert m.predict([], base_rate=0.5) == 0.5


def test_single_result_returns_base_rate():
    m = MarkovPredictor(order=2)
    assert m.predict(["S"], base_rate=0.5) == 0.5


def test_two_results_returns_base_rate():
    m = MarkovPredictor(order=2)
    assert m.predict(["S", "F"], base_rate=0.5) == 0.5


def test_all_success_pattern():
    m = MarkovPredictor(order=2)
    prob = m.predict(["S", "S", "S", "S", "S", "S"], base_rate=0.5)
    assert prob > 0.5


def test_all_failure_pattern():
    m = MarkovPredictor(order=2)
    prob = m.predict(["F", "F", "F", "F", "F", "F"], base_rate=0.5)
    assert prob < 0.5


def test_alternating_pattern():
    m = MarkovPredictor(order=2)
    prob = m.predict(["S", "F", "S", "F", "S", "F"], base_rate=0.5)
    assert 0.0 <= prob <= 1.0


def test_predict_with_order_3():
    m = MarkovPredictor(order=3)
    prob = m.predict(["S", "S", "S", "F", "F", "F", "S", "S", "S"], base_rate=0.5)
    assert 0.0 <= prob <= 1.0


def test_get_trend():
    m = MarkovPredictor(order=2)
    trend = m.get_trend(["S", "F", "S", "F", "S"], base_rate=0.5)
    assert len(trend) == 5
    assert trend[0]["step"] == 1
    assert trend[4]["step"] == 5
    for t in trend:
        assert 0.0 <= t["prob"] <= 1.0


def test_get_trend_empty():
    m = MarkovPredictor(order=2)
    assert m.get_trend([], base_rate=0.5) == []
