"""马尔可夫链预测模型"""
from typing import List, Dict


class MarkovPredictor:
    def __init__(self, order: int = 2):
        self.order = order

    def predict(self, results: List[str], base_rate: float) -> float:
        if len(results) <= self.order:
            return base_rate
        transitions = {}
        for i in range(len(results) - self.order):
            state = "".join(results[i:i + self.order])
            next_result = results[i + self.order]
            if state not in transitions:
                transitions[state] = {"S": 0, "F": 0}
            transitions[state][next_result] += 1
        current_state = "".join(results[-self.order:])
        if current_state not in transitions:
            return base_rate
        counts = transitions[current_state]
        total = counts["S"] + counts["F"]
        if total == 0:
            return base_rate
        return counts["S"] / total

    def get_trend(self, results: List[str], base_rate: float) -> List[Dict]:
        if not results:
            return []
        trend = []
        for i in range(1, len(results) + 1):
            prob = self.predict(results[:i], base_rate)
            trend.append({"step": i, "prob": round(prob, 4)})
        return trend
