"""API 路由定义"""
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.models.ensemble import EnsemblePredictor
from app.data.probabilities import ENHANCE_RATES, BADGE_RATES

router = APIRouter(prefix="/api")
ensemble = EnsemblePredictor()


class PredictRequest(BaseModel):
    enhance_level: str
    badge_level: int
    results: List[str]
    weights: Optional[dict] = None


class FeedbackHistoryItem(BaseModel):
    predicted_rate: float
    markov_prob: Optional[float] = None
    hmm_prob: Optional[float] = None
    bayesian_prob: Optional[float] = None
    actual_result: str


class FeedbackRequest(BaseModel):
    session_id: str
    actual_result: str
    history: List[FeedbackHistoryItem]


class LearnHistoryItem(BaseModel):
    pad_results: List[str]
    actual_result: str
    enhance_level: str


class LearnRequest(BaseModel):
    history: List[LearnHistoryItem]
    current_markov_order: int = 2


@router.post("/predict")
def predict(req: PredictRequest):
    weights = req.weights or {"w1": 0.3, "w2": 0.4, "w3": 0.3}
    return ensemble.predict(
        enhance_level=req.enhance_level,
        badge_level=req.badge_level,
        results=req.results,
        weights=weights,
    )


@router.get("/probabilities")
def probabilities():
    return {
        "enhance": ENHANCE_RATES,
        "badge": {str(k): v for k, v in BADGE_RATES.items()},
    }


@router.post("/feedback")
def feedback(req: FeedbackRequest):
    history_dicts = [h.model_dump() for h in req.history]
    new_weights = ensemble.calibrate_weights(history_dicts)
    accuracy = ensemble.calculate_accuracy(history_dicts)

    count = len(history_dicts)
    if count < 5:
        stage, label = "cold", "学习中"
    elif count < 20:
        stage, label = "growing", "成长中"
    elif count < 50:
        stage, label = "mature", "较成熟"
    else:
        stage, label = "expert", "高度个性化"

    model_names = {"w1": "马尔可夫", "w2": "HMM", "w3": "贝叶斯"}
    best_model = max(new_weights, key=new_weights.get)
    best_name = model_names[best_model]
    best_val = new_weights[best_model]

    return {
        "new_weights": new_weights,
        "accuracy": accuracy,
        "learning_stage": stage,
        "stage_label": label,
        "message": f"模型权重已校准：{best_name}模型表现最佳，权重提升至{best_val}",
    }


@router.post("/learn")
def learn(req: LearnRequest):
    history = [h.model_dump() for h in req.history]
    count = len(history)

    patterns = {}
    for record in history:
        pads = record["pad_results"]
        suffix = "".join(pads[-3:]) if len(pads) >= 3 else "".join(pads)
        if suffix not in patterns:
            patterns[suffix] = {"count": 0, "success": 0}
        patterns[suffix]["count"] += 1
        if record["actual_result"] == "success":
            patterns[suffix]["success"] += 1

    empirical_patterns = {}
    for k, v in patterns.items():
        if v["count"] >= 2:
            empirical_patterns[k] = {"count": v["count"], "success_rate": round(v["success"] / v["count"], 4)}

    level_stats = {}
    for record in history:
        level = record["enhance_level"]
        if level not in level_stats:
            level_stats[level] = {"count": 0, "success": 0}
        level_stats[level]["count"] += 1
        if record["actual_result"] == "success":
            level_stats[level]["success"] += 1

    personal_rates = {}
    for level, stats in level_stats.items():
        if stats["count"] >= 3:
            personal_rates[level] = round(stats["success"] / stats["count"], 4)

    markov_order = req.current_markov_order
    upgraded = False
    if count >= 30 and markov_order < 4:
        markov_order += 1
        upgraded = True

    return {
        "hmm_retrained": count >= 10,
        "markov_order": markov_order,
        "markov_order_upgraded": upgraded,
        "empirical_patterns": empirical_patterns,
        "personal_rates": personal_rates,
        "message": f"已用{count}条数据分析，发现{len(empirical_patterns)}种经验模式",
    }
