import pytest
from app.models.bayesian import BayesianPredictor


def test_no_results_returns_base_rate():
    b = BayesianPredictor()
    alpha, beta, prob = b.predict([], base_rate=0.5)
    assert abs(prob - 0.5) < 0.01
    assert alpha == 5.0
    assert beta == 5.0


def test_all_success_increases_probability():
    b = BayesianPredictor()
    _, _, prob = b.predict(["S", "S", "S", "S", "S"], base_rate=0.5)
    assert prob > 0.5


def test_all_failure_decreases_probability():
    b = BayesianPredictor()
    _, _, prob = b.predict(["F", "F", "F", "F", "F"], base_rate=0.5)
    assert prob < 0.5


def test_balanced_results_stays_near_base():
    b = BayesianPredictor()
    _, _, prob = b.predict(["S", "F", "S", "F", "S", "F"], base_rate=0.5)
    assert abs(prob - 0.5) < 0.1


def test_returns_alpha_beta():
    b = BayesianPredictor()
    alpha, beta, _ = b.predict(["S", "F", "S"], base_rate=0.5)
    assert alpha == 7.0
    assert beta == 6.0


def test_custom_prior_strength():
    b = BayesianPredictor(prior_strength=20)
    alpha, beta, _ = b.predict([], base_rate=0.5)
    assert alpha == 10.0
    assert beta == 10.0


def test_get_trend():
    b = BayesianPredictor()
    trend = b.get_trend(["S", "F", "S", "F", "S"], base_rate=0.5)
    assert len(trend) == 5
    for t in trend:
        assert 0.0 < t["prob"] < 1.0