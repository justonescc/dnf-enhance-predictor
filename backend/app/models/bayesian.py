"""贝叶斯更新预测模型"""
from typing import List, Dict, Tuple


class BayesianPredictor:
    def __init__(self, prior_strength: float = 10):
        self.prior_strength = prior_strength

    def predict(self, results: List[str], base_rate: float) -> Tuple[float, float, float]:
        alpha = base_rate * self.prior_strength
        beta = (1 - base_rate) * self.prior_strength
        alpha += results.count("S")
        beta += results.count("F")
        prob = alpha / (alpha + beta)
        return round(alpha, 2), round(beta, 2), round(prob, 4)

    def get_trend(self, results: List[str], base_rate: float) -> List[Dict]:
        trend = []
        for i in range(1, len(results) + 1):
            _, _, prob = self.predict(results[:i], base_rate)
            trend.append({"step": i, "prob": prob})
        return trend