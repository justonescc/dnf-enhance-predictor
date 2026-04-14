"""隐马尔可夫模型预测"""
import numpy as np
from typing import List, Dict, Tuple

try:
    from hmmlearn import hmm
    HAS_HMMLEARN = True
except ImportError:
    HAS_HMMLEARN = False


class HMMPredictor:
    def __init__(self, n_components: int = 3):
        self.n_components = n_components

    def predict(self, results: List[str], base_rate: float) -> Tuple[float, str]:
        if not HAS_HMMLEARN or len(results) < 8:
            return base_rate, "normal"
        try:
            return self._hmm_predict(results, base_rate)
        except Exception:
            return base_rate, "normal"

    def _hmm_predict(self, results: List[str], base_rate: float) -> Tuple[float, str]:
        obs = np.array([[1 if r == "S" else 0] for r in results])
        s_count = results.count("S")
        f_count = results.count("F")

        model = hmm.CategoricalHMM(
            n_components=self.n_components, n_iter=50, random_state=42,
            init_params="",
        )
        model.n_features = 2
        model.startprob_ = np.array([1.0 / self.n_components] * self.n_components)
        trans = np.full((self.n_components, self.n_components), 0.1)
        np.fill_diagonal(trans, 0.8)
        trans /= trans.sum(axis=1, keepdims=True)
        model.transmat_ = trans
        model.emissionprob_ = np.array([
            [min(base_rate * 1.5, 0.95), max(1 - base_rate * 1.5, 0.05)],
            [base_rate, 1 - base_rate],
            [max(base_rate * 0.5, 0.05), min(1 - base_rate * 0.5, 0.95)],
        ])
        model.fit(obs)

        _, state_sequence = model.decode(obs)
        current_state = int(state_sequence[-1])

        # Determine state labels from fitted emission probabilities
        state_probs = model.emissionprob_[:, 0]
        unique_probs = np.unique(state_probs.round(6))

        if len(unique_probs) >= 3:
            # Non-degenerate: sort by emission probability
            sorted_idx = np.argsort(state_probs)
            labels = {sorted_idx[0]: "unlucky", sorted_idx[1]: "normal", sorted_idx[2]: "lucky"}
            prob = float(state_probs[current_state])
        elif len(unique_probs) == 2:
            sorted_idx = np.argsort(state_probs)
            labels = {sorted_idx[0]: "unlucky", sorted_idx[1]: "normal", sorted_idx[2]: "lucky"}
            prob = float(state_probs[current_state])
        else:
            # Degenerate: all states collapsed to same emission
            # Use observed data to infer probability and label
            if s_count == 0:
                prob = max(0.01, base_rate * 0.1)
                labels = {current_state: "unlucky"}
            elif f_count == 0:
                prob = min(0.99, base_rate + (0.99 - base_rate) * 0.8)
                labels = {current_state: "lucky"}
            else:
                prob = s_count / len(results)
                labels = {current_state: "normal"}

        state_label = labels.get(current_state, "normal")
        return round(max(0.01, min(0.99, prob)), 4), state_label

    def get_trend(self, results: List[str], base_rate: float) -> List[Dict]:
        trend = []
        for i in range(1, len(results) + 1):
            prob, _ = self.predict(results[:i], base_rate)
            trend.append({"step": i, "prob": prob})
        return trend
