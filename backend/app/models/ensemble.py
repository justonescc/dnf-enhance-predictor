"""模型融合模块"""
import numpy as np
from typing import List, Dict, Tuple
from app.models.markov import MarkovPredictor
from app.models.hmm_model import HMMPredictor
from app.models.bayesian import BayesianPredictor
from app.data.probabilities import get_enhance_rate, get_badge_rate


class EnsemblePredictor:
    def __init__(self):
        self.markov = MarkovPredictor(order=2)
        self.hmm = HMMPredictor()
        self.bayesian = BayesianPredictor()

    def predict(self, enhance_level: str, badge_level: int, results: List[str], weights: Dict[str, float]) -> Dict:
        base_rate = get_enhance_rate(enhance_level)
        badge_rate = get_badge_rate(badge_level)
        markov_prob = self.markov.predict(results, badge_rate)
        hmm_prob, hmm_state = self.hmm.predict(results, badge_rate)
        bayesian_alpha, bayesian_beta, bayesian_prob = self.bayesian.predict(results, badge_rate)
        w1 = weights.get("w1", 0.3)
        w2 = weights.get("w2", 0.4)
        w3 = weights.get("w3", 0.3)
        predicted_rate = w1 * markov_prob + w2 * hmm_prob + w3 * bayesian_prob
        predicted_rate = round(max(0.01, min(0.99, predicted_rate)), 4)
        confidence = self._calculate_confidence(len(results), markov_prob, hmm_prob, bayesian_prob)
        rec, rec_text, rec_level = self._get_recommendation(predicted_rate, base_rate, confidence)
        trend = self.bayesian.get_trend(results, badge_rate)
        return {
            "predicted_rate": predicted_rate, "base_rate": base_rate,
            "confidence": round(confidence, 4), "recommendation": rec,
            "recommendation_text": rec_text, "recommendation_level": rec_level,
            "models": {
                "markov_prob": round(markov_prob, 4), "hmm_prob": round(hmm_prob, 4),
                "hmm_state": hmm_state, "bayesian_prob": round(bayesian_prob, 4),
                "bayesian_alpha": bayesian_alpha, "bayesian_beta": bayesian_beta,
            },
            "trend": trend,
        }

    def _calculate_confidence(self, n: int, p1: float, p2: float, p3: float) -> float:
        if n < 5: size_factor = 0.2
        elif n < 10: size_factor = 0.4
        elif n < 15: size_factor = 0.6
        else: size_factor = 0.8
        std = float(np.std([p1, p2, p3]))
        agreement = max(0, 1.0 - std * 4)
        return min(0.85, size_factor * 0.7 + agreement * 0.3)

    def _get_recommendation(self, predicted: float, base: float, confidence: float) -> Tuple[str, str, str]:
        pct = predicted * 100
        base_pct = base * 100
        if predicted > base * 1.3 and confidence > 0.5:
            return "enhance", f"预测成功率 {pct:.1f}%，高于基础 {base_pct:.0f}%，建议直接增幅", "green"
        if predicted >= base * 1.1:
            return "consider", f"预测成功率 {pct:.1f}%，略高于基础 {base_pct:.0f}%，可以再垫几手", "yellow"
        if predicted >= base * 0.8:
            return "pad", f"预测成功率 {pct:.1f}%，接近基础 {base_pct:.0f}%，建议继续垫手", "orange"
        return "avoid", f"预测成功率 {pct:.1f}%，低于基础 {base_pct:.0f}%，不建议此时增幅", "red"

    def calibrate_weights(self, history: List[Dict]) -> Dict[str, float]:
        if not history:
            return {"w1": 0.3, "w2": 0.4, "w3": 0.3}
        recent = history[-20:]
        scores = {"markov": 0.0, "hmm": 0.0, "bayesian": 0.0}
        for record in recent:
            actual_success = record.get("actual_result") == "success"
            for model_key, prob_key in [("markov", "markov_prob"), ("hmm", "hmm_prob"), ("bayesian", "bayesian_prob")]:
                prob = record.get(prob_key)
                if prob is None: continue
                if (prob >= 0.5) == actual_success:
                    scores[model_key] += 1.0
                else:
                    scores[model_key] -= 0.5
        min_score = 0.1
        total_score = sum(max(min_score, s + 1) for s in scores.values())
        w1 = max(min_score, (scores["markov"] + 1) / total_score)
        w2 = max(min_score, (scores["hmm"] + 1) / total_score)
        w3 = max(min_score, (scores["bayesian"] + 1) / total_score)
        total = w1 + w2 + w3
        return {"w1": round(w1 / total, 2), "w2": round(w2 / total, 2), "w3": round(w3 / total, 2)}

    def calculate_accuracy(self, history: List[Dict]) -> Dict:
        if not history:
            return {"total": 0, "total_count": 0}
        correct = 0
        for r in history:
            pred = r.get("predicted_rate")
            actual = r.get("actual_result")
            if pred is None or actual is None: continue
            if (pred >= 0.5) == (actual == "success"): correct += 1
        total = len(history)
        return {"total": round(correct / total, 4) if total > 0 else 0, "total_count": total}
