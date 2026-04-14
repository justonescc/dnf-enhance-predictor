import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint():
    response = client.post("/api/predict", json={
        "enhance_level": "+10", "badge_level": 7,
        "results": ["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "predicted_rate" in data
    assert "base_rate" in data
    assert "confidence" in data
    assert "recommendation" in data
    assert "models" in data
    assert "trend" in data
    assert data["base_rate"] == 0.40


def test_predict_short_sequence():
    response = client.post("/api/predict", json={
        "enhance_level": "+10", "badge_level": 7, "results": ["S", "F"],
    })
    assert response.status_code == 200


def test_probabilities_endpoint():
    response = client.get("/api/probabilities")
    assert response.status_code == 200
    data = response.json()
    assert "enhance" in data
    assert "badge" in data
    assert data["enhance"]["+10"] == 0.40
    assert data["badge"]["7"] == 0.50


def test_feedback_endpoint():
    response = client.post("/api/feedback", json={
        "session_id": "test123", "actual_result": "success",
        "history": [
            {"predicted_rate": 0.7, "markov_prob": 0.68, "hmm_prob": 0.75, "bayesian_prob": 0.73, "actual_result": "success"},
            {"predicted_rate": 0.4, "markov_prob": 0.45, "hmm_prob": 0.38, "bayesian_prob": 0.42, "actual_result": "failure"},
        ],
    })
    assert response.status_code == 200
    data = response.json()
    assert "new_weights" in data
    assert "accuracy" in data
    assert "learning_stage" in data
    total = data["new_weights"]["w1"] + data["new_weights"]["w2"] + data["new_weights"]["w3"]
    assert abs(total - 1.0) < 0.05


def test_learn_endpoint():
    response = client.post("/api/learn", json={
        "history": [
            {"pad_results": ["S", "F", "F"], "actual_result": "success", "enhance_level": "+10"},
            {"pad_results": ["F", "F", "F", "F"], "actual_result": "failure", "enhance_level": "+10"},
            {"pad_results": ["S", "S", "F", "F"], "actual_result": "success", "enhance_level": "+10"},
            {"pad_results": ["F", "S", "F", "F"], "actual_result": "failure", "enhance_level": "+10"},
            {"pad_results": ["S", "F", "S", "F"], "actual_result": "success", "enhance_level": "+10"},
        ],
        "current_markov_order": 2,
    })
    assert response.status_code == 200
    data = response.json()
    assert "empirical_patterns" in data
    assert "personal_rates" in data
    assert "message" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()