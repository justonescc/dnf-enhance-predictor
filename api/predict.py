import sys
import os
import json
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.data.probabilities import ENHANCE_RATES, BADGE_RATES
from app.models.ensemble import EnsemblePredictor

_ensemble = EnsemblePredictor()


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        path = self.path
        if "/api/probabilities" in path:
            self._json({
                "enhance": ENHANCE_RATES,
                "badge": {str(k): v for k, v in BADGE_RATES.items()},
            })
        else:
            self._json({"service": "DNF Enhancement Predictor API", "version": "1.0.0"})

    def do_POST(self):
        path = self.path
        body = self._body()
        if "/api/predict" in path:
            self._predict(body)
        elif "/api/feedback" in path:
            self._feedback(body)
        elif "/api/learn" in path:
            self._learn(body)
        else:
            self._json({"error": "not found"}, 404)

    def _predict(self, body):
        weights = body.get("weights") or {"w1": 0.3, "w2": 0.4, "w3": 0.3}
        result = _ensemble.predict(
            enhance_level=body.get("enhance_level", "+10"),
            badge_level=body.get("badge_level", 7),
            results=body.get("results", []),
            weights=weights,
            history_count=body.get("history_count", 0),
            empirical_patterns=body.get("empirical_patterns"),
            personal_rates=body.get("personal_rates"),
        )
        self._json(result)

    def _feedback(self, body):
        history = body.get("history", [])
        new_weights = _ensemble.calibrate_weights(history)
        accuracy = _ensemble.calculate_accuracy(history)
        count = len(history)
        if count < 5:
            stage, label = "cold", "学习中"
        elif count < 20:
            stage, label = "growing", "成长中"
        elif count < 50:
            stage, label = "mature", "较成熟"
        else:
            stage, label = "expert", "高度个性化"
        model_names = {"w1": "马尔可夫", "w2": "HMM", "w3": "贝叶斯"}
        best = max(new_weights, key=new_weights.get)
        self._json({
            "new_weights": new_weights,
            "accuracy": accuracy,
            "learning_stage": stage,
            "stage_label": label,
            "message": f"模型权重已校准：{model_names[best]}模型表现最佳，权重提升至{new_weights[best]}",
        })

    def _learn(self, body):
        history = body.get("history", [])
        count = len(history)
        patterns = {}
        for rec in history:
            pads = rec.get("pad_results", [])
            suffix = "".join(pads[-3:]) if len(pads) >= 3 else "".join(pads)
            if suffix not in patterns:
                patterns[suffix] = {"count": 0, "success": 0}
            patterns[suffix]["count"] += 1
            if rec.get("actual_result") == "success":
                patterns[suffix]["success"] += 1
        empirical = {}
        for k, v in patterns.items():
            if v["count"] >= 2:
                empirical[k] = {"count": v["count"], "success_rate": round(v["success"] / v["count"], 4)}
        level_stats = {}
        for rec in history:
            lv = rec.get("enhance_level", "")
            level_stats.setdefault(lv, {"count": 0, "success": 0})
            level_stats[lv]["count"] += 1
            if rec.get("actual_result") == "success":
                level_stats[lv]["success"] += 1
        personal = {}
        for lv, st in level_stats.items():
            if st["count"] >= 3:
                personal[lv] = round(st["success"] / st["count"], 4)
        order = body.get("current_markov_order", 2)
        upgraded = count >= 30 and order < 4
        if upgraded:
            order += 1
        self._json({
            "hmm_retrained": count >= 10,
            "markov_order": order,
            "markov_order_upgraded": upgraded,
            "empirical_patterns": empirical,
            "personal_rates": personal,
            "message": f"已用{count}条数据分析，发现{len(empirical)}种经验模式",
        })

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length > 0 else {}

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._set_cors()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
