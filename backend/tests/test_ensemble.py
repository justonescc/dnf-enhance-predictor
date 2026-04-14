import pytest
from app.models.ensemble import EnsemblePredictor


def test_basic_prediction_structure():
    e = EnsemblePredictor()
    result = e.predict(
        enhance_level="+10", badge_level=7,
        results=["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"],
        weights={"w1": 0.3, "w2": 0.4, "w3": 0.3},
    )
    for key in ["predicted_rate", "base_rate", "confidence", "recommendation",
                "recommendation_text", "recommendation_level", "models", "trend"]:
        assert key in result


def test_base_rate_correct():
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert result["base_rate"] == 0.40


def test_predicted_rate_in_range():
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert 0.0 <= result["predicted_rate"] <= 1.0


def test_confidence_increases_with_length():
    e = EnsemblePredictor()
    short = e.predict("+10", 7, ["S", "F", "S"], {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    long = e.predict("+10", 7, ["S", "F"] * 8, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert long["confidence"] > short["confidence"]


def test_recommendation_levels():
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert result["recommendation_level"] in ("green", "yellow", "orange", "red")


def test_trend_length_matches_results():
    results = ["S", "F", "S", "F", "S"]
    e = EnsemblePredictor()
    r = e.predict("+10", 7, results, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert len(r["trend"]) == len(results)


def test_calibrate_weights():
    e = EnsemblePredictor()
    history = [
        {"markov_prob": 0.7, "hmm_prob": 0.6, "bayesian_prob": 0.65, "actual_result": "success"},
        {"markov_prob": 0.5, "hmm_prob": 0.4, "bayesian_prob": 0.55, "actual_result": "failure"},
        {"markov_prob": 0.6, "hmm_prob": 0.7, "bayesian_prob": 0.65, "actual_result": "success"},
    ]
    new_weights = e.calibrate_weights(history)
    total = new_weights["w1"] + new_weights["w2"] + new_weights["w3"]
    assert abs(total - 1.0) < 0.05
    assert new_weights["w1"] >= 0.1
    assert new_weights["w2"] >= 0.1
    assert new_weights["w3"] >= 0.1


def test_calibrate_with_empty_history():
    e = EnsemblePredictor()
    weights = e.calibrate_weights([])
    assert weights == {"w1": 0.3, "w2": 0.4, "w3": 0.3}


def test_calculate_accuracy():
    e = EnsemblePredictor()
    history = [
        {"predicted_rate": 0.7, "actual_result": "success"},
        {"predicted_rate": 0.3, "actual_result": "failure"},
        {"predicted_rate": 0.6, "actual_result": "failure"},
    ]
    acc = e.calculate_accuracy(history)
    assert acc["total"] == pytest.approx(2.0 / 3.0, abs=0.01)
    assert acc["total_count"] == 3