# DNF增幅概率预测器 - 后端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的 FastAPI 后端，实现马尔可夫链、HMM、贝叶斯更新三个预测模型，提供预测、反馈、学习三个 API 接口。

**Architecture:** FastAPI 无状态服务端。每次请求独立计算，不依赖数据库。前端通过 localStorage 管理历史数据，按需发送给后端计算。三个模型各自独立实现，由 ensemble 模块加权融合输出最终预测。

**Tech Stack:** Python 3.9 / FastAPI / NumPy / SciPy / hmmlearn / pytest

---

## 文件结构

```
backend/
├── app/
│   ├── __init__.py                # 空文件
│   ├── main.py                    # FastAPI 入口 + CORS
│   ├── api/
│   │   ├── __init__.py            # 空文件
│   │   └── predict.py             # 4个 API 路由
│   ├── models/
│   │   ├── __init__.py            # 空文件
│   │   ├── markov.py              # 马尔可夫链模型
│   │   ├── hmm_model.py           # 隐马尔可夫模型
│   │   ├── bayesian.py            # 贝叶斯更新模型
│   │   └── ensemble.py            # 模型融合 + 置信度 + 建议
│   └── data/
│       ├── __init__.py            # 空文件
│       └── probabilities.py       # 概率表常量
├── tests/
│   ├── __init__.py                # 空文件
│   ├── test_markov.py
│   ├── test_bayesian.py
│   ├── test_hmm.py
│   ├── test_ensemble.py
│   └── test_api.py
├── requirements.txt
└── render.yaml
```

---

### Task 1: 项目脚手架搭建

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/render.yaml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/data/__init__.py`
- Create: `backend/tests/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```
fastapi==0.115.0
uvicorn==0.32.0
numpy==1.24.4
scipy==1.10.1
hmmlearn==0.3.0
pytest==8.3.0
httpx==0.27.0
```

- [ ] **Step 2: 创建 render.yaml**

```yaml
services:
  - type: web
    name: dnf-enhance-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    plan: free
```

- [ ] **Step 3: 创建所有 __init__.py 空文件**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
touch app/__init__.py app/api/__init__.py app/models/__init__.py app/data/__init__.py
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 4: 安装依赖**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
source .venv/bin/activate
pip install -r backend/requirements.txt
```

- [ ] **Step 5: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/
git commit -m "feat: 初始化后端项目脚手架，添加依赖和目录结构"
```

---

### Task 2: 概率表数据 (probabilities.py)

**Files:**
- Create: `backend/app/data/probabilities.py`

- [ ] **Step 1: 编写 probabilities.py**

```python
"""DNF手游增幅概率表和徽章合成概率表"""

# 增幅成功率表：键为等级字符串，值为成功率
ENHANCE_RATES = {
    "+0": 0.55, "+1": 0.55, "+2": 0.55, "+3": 0.55,
    "+4": 0.80, "+5": 0.70, "+6": 0.60, "+7": 0.70,
    "+8": 0.60, "+9": 0.50, "+10": 0.40, "+11": 0.30,
    "+12": 0.20, "+13": 0.20, "+14": 0.20, "+15": 0.20,
    "+16": 0.20, "+17": 0.20, "+18": 0.20, "+19": 0.20,
}

# 徽章合成成功率表：键为起始等级（int），值为成功率
BADGE_RATES = {
    5: 0.70, 6: 0.60, 7: 0.50, 8: 0.40, 9: 0.30, 10: 0.30,
}


def get_enhance_rate(level: str) -> float:
    """获取增幅等级对应的基础成功率"""
    return ENHANCE_RATES.get(level, 0.20)


def get_badge_rate(badge_level: int) -> float:
    """获取徽章等级对应的合成成功率"""
    return BADGE_RATES.get(badge_level, 0.50)
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/app/data/probabilities.py
git commit -m "feat: 添加增幅和徽章概率表数据模块"
```

---

### Task 3: 马尔可夫链模型 (markov.py)

**Files:**
- Create: `backend/app/models/markov.py`
- Create: `backend/tests/test_markov.py`

- [ ] **Step 1: 编写测试 test_markov.py**

```python
import pytest
from app.models.markov import MarkovPredictor


def test_empty_results_returns_base_rate():
    """空序列应返回基础概率"""
    m = MarkovPredictor(order=2)
    result = m.predict([], base_rate=0.5)
    assert result == 0.5


def test_single_result_returns_base_rate():
    """序列不足 order 长度时返回基础概率"""
    m = MarkovPredictor(order=2)
    result = m.predict(["S"], base_rate=0.5)
    assert result == 0.5


def test_two_results_returns_base_rate():
    """恰好 order 长度的序列无转移数据，返回基础概率"""
    m = MarkovPredictor(order=2)
    result = m.predict(["S", "F"], base_rate=0.5)
    assert result == 0.5


def test_all_success_pattern():
    """全部成功的序列，最后状态 SS，后续也应倾向成功"""
    m = MarkovPredictor(order=2)
    results = ["S", "S", "S", "S", "S", "S"]
    prob = m.predict(results, base_rate=0.5)
    assert prob > 0.5


def test_all_failure_pattern():
    """全部失败的序列，最后状态 FF，后续也应倾向失败"""
    m = MarkovPredictor(order=2)
    results = ["F", "F", "F", "F", "F", "F"]
    prob = m.predict(results, base_rate=0.5)
    assert prob < 0.5


def test_alternating_pattern():
    """交替模式的序列 SF SF"""
    m = MarkovPredictor(order=2)
    results = ["S", "F", "S", "F", "S", "F"]
    prob = m.predict(results, base_rate=0.5)
    # 交替后应预测 F（因为 SF -> F 的转移概率高）
    assert 0.0 <= prob <= 1.0


def test_predict_with_order_3():
    """3阶马尔可夫链"""
    m = MarkovPredictor(order=3)
    results = ["S", "S", "S", "F", "F", "F", "S", "S", "S"]
    prob = m.predict(results, base_rate=0.5)
    assert 0.0 <= prob <= 1.0


def test_get_trend():
    """趋势数据应逐步返回累积概率"""
    m = MarkovPredictor(order=2)
    results = ["S", "F", "S", "F", "S"]
    trend = m.get_trend(results, base_rate=0.5)
    assert len(trend) == 5
    assert trend[0]["step"] == 1
    assert trend[4]["step"] == 5
    for t in trend:
        assert 0.0 <= t["prob"] <= 1.0


def test_get_trend_empty():
    """空序列返回空趋势"""
    m = MarkovPredictor(order=2)
    trend = m.get_trend([], base_rate=0.5)
    assert trend == []
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_markov.py -v
```

Expected: FAIL（模块不存在）

- [ ] **Step 3: 编写 markov.py**

```python
"""马尔可夫链预测模型

将垫手序列建模为 order 阶马尔可夫链。
基于最近 order 次结果的组合状态构建转移概率矩阵。
"""
from typing import List, Dict


class MarkovPredictor:
    def __init__(self, order: int = 2):
        self.order = order

    def predict(self, results: List[str], base_rate: float) -> float:
        """基于垫手序列预测下一次成功概率

        Args:
            results: 垫手结果列表，每个元素为 "S" 或 "F"
            base_rate: 基础成功率，作为无数据时的默认值

        Returns:
            预测的成功概率 [0, 1]
        """
        if len(results) <= self.order:
            return base_rate

        # 构建转移计数表
        transitions = {}  # state -> {"S": count, "F": count}
        for i in range(len(results) - self.order):
            state = "".join(results[i:i + self.order])
            next_result = results[i + self.order]
            if state not in transitions:
                transitions[state] = {"S": 0, "F": 0}
            transitions[state][next_result] += 1

        # 当前状态
        current_state = "".join(results[-self.order:])

        if current_state not in transitions:
            return base_rate

        counts = transitions[current_state]
        total = counts["S"] + counts["F"]
        if total == 0:
            return base_rate

        return counts["S"] / total

    def get_trend(self, results: List[str], base_rate: float) -> List[Dict]:
        """计算逐步累积的预测概率趋势

        对每个前缀子序列计算预测概率，形成趋势数据。
        """
        if not results:
            return []

        trend = []
        for i in range(1, len(results) + 1):
            prefix = results[:i]
            prob = self.predict(prefix, base_rate)
            trend.append({"step": i, "prob": round(prob, 4)})
        return trend
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_markov.py -v
```

Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/app/models/markov.py backend/tests/test_markov.py
git commit -m "feat: 添加马尔可夫链预测模型及测试"
```

---

### Task 4: 贝叶斯更新模型 (bayesian.py)

**Files:**
- Create: `backend/app/models/bayesian.py`
- Create: `backend/tests/test_bayesian.py`

- [ ] **Step 1: 编写测试 test_bayesian.py**

```python
import pytest
from app.models.bayesian import BayesianPredictor


def test_no_results_returns_base_rate():
    """无数据时后验均值等于基础概率"""
    b = BayesianPredictor()
    alpha, beta, prob = b.predict([], base_rate=0.5)
    assert abs(prob - 0.5) < 0.01
    assert alpha == 5.0
    assert beta == 5.0


def test_all_success_increases_probability():
    """全部成功应提高预测概率"""
    b = BayesianPredictor()
    _, _, prob = b.predict(["S", "S", "S", "S", "S"], base_rate=0.5)
    assert prob > 0.5


def test_all_failure_decreases_probability():
    """全部失败应降低预测概率"""
    b = BayesianPredictor()
    _, _, prob = b.predict(["F", "F", "F", "F", "F"], base_rate=0.5)
    assert prob < 0.5


def test_balanced_results_stays_near_base():
    """成功失败各半应接近基础概率"""
    b = BayesianPredictor()
    _, _, prob = b.predict(["S", "F", "S", "F", "S", "F"], base_rate=0.5)
    assert abs(prob - 0.5) < 0.1


def test_returns_alpha_beta():
    """应返回更新后的 alpha 和 beta"""
    b = BayesianPredictor()
    alpha, beta, _ = b.predict(["S", "F", "S"], base_rate=0.5)
    # 初始 alpha=5, beta=5，+2成功+1失败 -> alpha=7, beta=6
    assert alpha == 7.0
    assert beta == 6.0


def test_custom_prior_strength():
    """自定义先验强度"""
    b = BayesianPredictor(prior_strength=20)
    alpha, beta, _ = b.predict([], base_rate=0.5)
    assert alpha == 10.0  # 0.5 * 20
    assert beta == 10.0   # 0.5 * 20


def test_get_trend():
    """趋势逐步更新"""
    b = BayesianPredictor()
    results = ["S", "F", "S", "F", "S"]
    trend = b.get_trend(results, base_rate=0.5)
    assert len(trend) == 5
    assert trend[0]["step"] == 1
    for t in trend:
        assert 0.0 < t["prob"] < 1.0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_bayesian.py -v
```

Expected: FAIL

- [ ] **Step 3: 编写 bayesian.py**

```python
"""贝叶斯更新预测模型

将基础成功率作为先验概率（Beta分布），垫手结果作为观测证据。
每次观测更新 Beta 分布参数，后验均值作为预测概率。
"""
from typing import List, Dict, Tuple


class BayesianPredictor:
    def __init__(self, prior_strength: float = 10):
        """先验强度决定先验分布的"等效样本数"。
        值越大，先验越强，需要更多数据才能偏离基础概率。
        """
        self.prior_strength = prior_strength

    def predict(
        self, results: List[str], base_rate: float
    ) -> Tuple[float, float, float]:
        """基于垫手序列预测下一次成功概率

        Args:
            results: 垫手结果列表，每个元素为 "S" 或 "F"
            base_rate: 基础成功率，作为 Beta 先验的均值

        Returns:
            (alpha, beta, probability): 更新后的 Beta 参数和预测概率
        """
        alpha = base_rate * self.prior_strength
        beta = (1 - base_rate) * self.prior_strength

        success_count = results.count("S")
        fail_count = results.count("F")

        alpha += success_count
        beta += fail_count

        prob = alpha / (alpha + beta)
        return round(alpha, 2), round(beta, 2), round(prob, 4)

    def get_trend(
        self, results: List[str], base_rate: float
    ) -> List[Dict]:
        """计算逐步累积的贝叶斯预测趋势"""
        trend = []
        for i in range(1, len(results) + 1):
            prefix = results[:i]
            _, _, prob = self.predict(prefix, base_rate)
            trend.append({"step": i, "prob": prob})
        return trend
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_bayesian.py -v
```

Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/app/models/bayesian.py backend/tests/test_bayesian.py
git commit -m "feat: 添加贝叶斯更新预测模型及测试"
```

---

### Task 5: 隐马尔可夫模型 (hmm_model.py)

**Files:**
- Create: `backend/app/models/hmm_model.py`
- Create: `backend/tests/test_hmm.py`

- [ ] **Step 1: 编写测试 test_hmm.py**

```python
import pytest
from app.models.hmm_model import HMMPredictor


def test_short_sequence_returns_base_rate():
    """序列太短（<8）时返回基础概率"""
    h = HMMPredictor()
    prob, state = h.predict(["S", "F", "S"], base_rate=0.5)
    assert prob == 0.5
    assert state == "normal"


def test_sufficient_sequence_returns_probability():
    """足够长的序列应返回有效概率"""
    h = HMMPredictor()
    results = ["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"]
    prob, state = h.predict(results, base_rate=0.5)
    assert 0.0 <= prob <= 1.0
    assert state in ("lucky", "normal", "unlucky")


def test_all_success_sequence():
    """全部成功应倾向好运状态"""
    h = HMMPredictor()
    results = ["S"] * 10
    prob, state = h.predict(results, base_rate=0.5)
    assert prob > 0.5
    assert state == "lucky"


def test_all_failure_sequence():
    """全部失败应倾向差运状态"""
    h = HMMPredictor()
    results = ["F"] * 10
    prob, state = h.predict(results, base_rate=0.5)
    assert prob < 0.5
    assert state == "unlucky"


def test_predict_with_custom_base():
    """不同基础概率的预测"""
    h = HMMPredictor()
    results = ["S", "F"] * 6
    prob, _ = h.predict(results, base_rate=0.3)
    assert 0.0 <= prob <= 1.0


def test_get_trend():
    """趋势数据"""
    h = HMMPredictor()
    results = ["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"]
    trend = h.get_trend(results, base_rate=0.5)
    assert len(trend) == 10
    for t in trend:
        assert 0.0 <= t["prob"] <= 1.0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_hmm.py -v
```

Expected: FAIL

- [ ] **Step 3: 编写 hmm_model.py**

```python
"""隐马尔可夫模型预测

假设游戏内部存在3个隐藏"运气状态"：好运、普通、差运。
用 hmmlearn 的 CategoricalHMM 训练和推断。
数据不足时（<8次）降级返回基础概率。
"""
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

    def predict(
        self, results: List[str], base_rate: float
    ) -> Tuple[float, str]:
        """基于垫手序列预测下一次成功概率

        Args:
            results: 垫手结果列表
            base_rate: 基础成功率

        Returns:
            (probability, state_label): 预测概率和隐藏状态标签
        """
        if not HAS_HMMLEARN or len(results) < 8:
            return base_rate, "normal"

        try:
            return self._hmm_predict(results, base_rate)
        except Exception:
            return base_rate, "normal"

    def _hmm_predict(
        self, results: List[str], base_rate: float
    ) -> Tuple[float, str]:
        obs = np.array([[1 if r == "S" else 0] for r in results])

        model = hmm.CategoricalHMM(
            n_components=self.n_components,
            n_iter=50,
            random_state=42,
            init_params="ste",
        )

        # 初始化发射概率：3个状态对应不同成功概率
        model.emissionprob_ = np.array([
            [min(base_rate * 1.5, 0.95), max(1 - base_rate * 1.5, 0.05)],  # 好运
            [base_rate, 1 - base_rate],                                      # 普通
            [max(base_rate * 0.5, 0.05), min(1 - base_rate * 0.5, 0.95)],   # 差运
        ])

        # 均匀初始分布
        model.startprob_ = np.array([1.0 / self.n_components] * self.n_components)

        # 均匀转移矩阵（对角线略高）
        trans = np.full((self.n_components, self.n_components), 0.1)
        np.fill_diagonal(trans, 0.8)
        trans /= trans.sum(axis=1, keepdims=True)
        model.transmat_ = trans

        model.fit(obs)

        # 用 Viterbi 推断当前最可能的隐藏状态序列
        _, state_sequence = model.decode(obs)
        current_state = int(state_sequence[-1])

        # 基于当前状态的发射概率预测
        prob = float(model.emissionprob_[current_state][0])

        # 排序确定状态标签
        state_probs = model.emissionprob_[:, 0]
        sorted_idx = np.argsort(state_probs)
        labels = {sorted_idx[0]: "unlucky", sorted_idx[1]: "normal", sorted_idx[2]: "lucky"}
        state_label = labels.get(current_state, "normal")

        return round(max(0.01, min(0.99, prob)), 4), state_label

    def get_trend(self, results: List[str], base_rate: float) -> List[Dict]:
        """计算趋势：对每个前缀子序列计算预测概率"""
        trend = []
        for i in range(1, len(results) + 1):
            prefix = results[:i]
            prob, _ = self.predict(prefix, base_rate)
            trend.append({"step": i, "prob": prob})
        return trend
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_hmm.py -v
```

Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/app/models/hmm_model.py backend/tests/test_hmm.py
git commit -m "feat: 添加隐马尔可夫预测模型及测试"
```

---

### Task 6: 模型融合 (ensemble.py)

**Files:**
- Create: `backend/app/models/ensemble.py`
- Create: `backend/tests/test_ensemble.py`

- [ ] **Step 1: 编写测试 test_ensemble.py**

```python
import pytest
from app.models.ensemble import EnsemblePredictor


def test_basic_prediction_structure():
    """基本预测应返回完整结构"""
    e = EnsemblePredictor()
    result = e.predict(
        enhance_level="+10",
        badge_level=7,
        results=["S", "F", "S", "F", "S", "F", "S", "F", "S", "F"],
        weights={"w1": 0.3, "w2": 0.4, "w3": 0.3},
    )
    assert "predicted_rate" in result
    assert "base_rate" in result
    assert "confidence" in result
    assert "recommendation" in result
    assert "recommendation_text" in result
    assert "recommendation_level" in result
    assert "models" in result
    assert "trend" in result


def test_base_rate_correct():
    """返回的基础概率应匹配增幅等级"""
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert result["base_rate"] == 0.40


def test_predicted_rate_in_range():
    """预测概率应在 [0, 1] 范围内"""
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert 0.0 <= result["predicted_rate"] <= 1.0


def test_confidence_increases_with_length():
    """置信度应随垫手次数增加"""
    e = EnsemblePredictor()
    short = e.predict("+10", 7, ["S", "F", "S"], {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    long = e.predict("+10", 7, ["S", "F"] * 8, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert long["confidence"] > short["confidence"]


def test_recommendation_levels():
    """建议级别应为 green/yellow/orange/red 之一"""
    e = EnsemblePredictor()
    result = e.predict("+10", 7, ["S", "F"] * 6, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert result["recommendation_level"] in ("green", "yellow", "orange", "red")


def test_trend_length_matches_results():
    """趋势数据长度应等于垫手次数"""
    results = ["S", "F", "S", "F", "S"]
    e = EnsemblePredictor()
    r = e.predict("+10", 7, results, {"w1": 0.3, "w2": 0.4, "w3": 0.3})
    assert len(r["trend"]) == len(results)


def test_calibrate_weights():
    """权重校准应返回和为1的权重"""
    e = EnsemblePredictor()
    history = [
        {"markov_prob": 0.7, "hmm_prob": 0.6, "bayesian_prob": 0.65, "actual_result": "success"},
        {"markov_prob": 0.5, "hmm_prob": 0.4, "bayesian_prob": 0.55, "actual_result": "failure"},
        {"markov_prob": 0.6, "hmm_prob": 0.7, "bayesian_prob": 0.65, "actual_result": "success"},
    ]
    new_weights = e.calibrate_weights(history)
    total = new_weights["w1"] + new_weights["w2"] + new_weights["w3"]
    assert abs(total - 1.0) < 0.01
    assert new_weights["w1"] >= 0.1
    assert new_weights["w2"] >= 0.1
    assert new_weights["w3"] >= 0.1


def test_calibrate_with_empty_history():
    """空历史应返回默认权重"""
    e = EnsemblePredictor()
    weights = e.calibrate_weights([])
    assert weights == {"w1": 0.3, "w2": 0.4, "w3": 0.3}


def test_calculate_accuracy():
    """准确率计算"""
    e = EnsemblePredictor()
    history = [
        {"predicted_rate": 0.7, "actual_result": "success"},
        {"predicted_rate": 0.3, "actual_result": "failure"},
        {"predicted_rate": 0.6, "actual_result": "failure"},
    ]
    acc = e.calculate_accuracy(history)
    assert acc["total"] == pytest.approx(2.0 / 3.0, abs=0.01)
    assert acc["total_count"] == 3
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_ensemble.py -v
```

Expected: FAIL

- [ ] **Step 3: 编写 ensemble.py**

```python
"""模型融合模块

将马尔可夫链、HMM、贝叶斯三个模型的预测结果加权融合。
包含置信度计算、操作建议生成、模型权重校准。
"""
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

    def predict(
        self,
        enhance_level: str,
        badge_level: int,
        results: List[str],
        weights: Dict[str, float],
    ) -> Dict:
        """综合三个模型预测

        Args:
            enhance_level: 增幅等级如 "+10"
            badge_level: 徽章等级如 7
            results: 垫手结果列表 ["S", "F", ...]
            weights: 模型权重 {"w1": 0.3, "w2": 0.4, "w3": 0.3}

        Returns:
            完整的预测结果字典
        """
        base_rate = get_enhance_rate(enhance_level)
        badge_rate = get_badge_rate(badge_level)

        # 各模型独立预测
        markov_prob = self.markov.predict(results, badge_rate)
        hmm_prob, hmm_state = self.hmm.predict(results, badge_rate)
        bayesian_alpha, bayesian_beta, bayesian_prob = self.bayesian.predict(
            results, badge_rate
        )

        # 加权融合
        w1 = weights.get("w1", 0.3)
        w2 = weights.get("w2", 0.4)
        w3 = weights.get("w3", 0.3)
        predicted_rate = w1 * markov_prob + w2 * hmm_prob + w3 * bayesian_prob
        predicted_rate = round(max(0.01, min(0.99, predicted_rate)), 4)

        # 置信度
        confidence = self._calculate_confidence(
            len(results), markov_prob, hmm_prob, bayesian_prob
        )

        # 操作建议
        rec, rec_text, rec_level = self._get_recommendation(
            predicted_rate, base_rate, confidence
        )

        # 趋势数据（使用贝叶斯趋势，因为它最稳定）
        trend = self.bayesian.get_trend(results, badge_rate)

        return {
            "predicted_rate": predicted_rate,
            "base_rate": base_rate,
            "confidence": round(confidence, 4),
            "recommendation": rec,
            "recommendation_text": rec_text,
            "recommendation_level": rec_level,
            "models": {
                "markov_prob": round(markov_prob, 4),
                "hmm_prob": round(hmm_prob, 4),
                "hmm_state": hmm_state,
                "bayesian_prob": round(bayesian_prob, 4),
                "bayesian_alpha": bayesian_alpha,
                "bayesian_beta": bayesian_beta,
            },
            "trend": trend,
        }

    def _calculate_confidence(
        self, n: int, p1: float, p2: float, p3: float
    ) -> float:
        """基于垫手次数和模型一致性计算置信度"""
        # 次数因子
        if n < 5:
            size_factor = 0.2
        elif n < 10:
            size_factor = 0.4
        elif n < 15:
            size_factor = 0.6
        else:
            size_factor = 0.8

        # 一致性因子：三个模型结果越接近，置信度越高
        probs = [p1, p2, p3]
        std = float(np.std(probs))
        agreement = max(0, 1.0 - std * 4)

        return min(0.85, size_factor * 0.7 + agreement * 0.3)

    def _get_recommendation(
        self, predicted: float, base: float, confidence: float
    ) -> Tuple[str, str, str]:
        """根据预测概率和基础概率生成操作建议

        Returns:
            (recommendation_key, text, color_level)
        """
        pct = predicted * 100
        base_pct = base * 100

        if predicted > base * 1.3 and confidence > 0.5:
            return (
                "enhance",
                f"预测成功率 {pct:.1f}%，高于基础 {base_pct:.0f}%，建议直接增幅",
                "green",
            )
        if predicted >= base * 1.1:
            return (
                "consider",
                f"预测成功率 {pct:.1f}%，略高于基础 {base_pct:.0f}%，可以再垫几手",
                "yellow",
            )
        if predicted >= base * 0.8:
            return (
                "pad",
                f"预测成功率 {pct:.1f}%，接近基础 {base_pct:.0f}%，建议继续垫手",
                "orange",
            )
        return (
            "avoid",
            f"预测成功率 {pct:.1f}%，低于基础 {base_pct:.0f}%，不建议此时增幅",
            "red",
        )

    def calibrate_weights(
        self, history: List[Dict]
    ) -> Dict[str, float]:
        """根据历史记录校准模型权重

        比较各模型最近20次预测与实际结果的偏差，
        按准确率比例重新分配权重。最小权重 0.1。
        """
        if not history:
            return {"w1": 0.3, "w2": 0.4, "w3": 0.3}

        recent = history[-20:]

        # 计算每个模型的"得分"
        scores = {"markov": 0.0, "hmm": 0.0, "bayesian": 0.0}
        for record in recent:
            actual_success = record.get("actual_result") == "success"

            for model_key, prob_key in [
                ("markov", "markov_prob"),
                ("hmm", "hmm_prob"),
                ("bayesian", "bayesian_prob"),
            ]:
                prob = record.get(prob_key)
                if prob is None:
                    continue
                predicted_success = prob >= 0.5
                if predicted_success == actual_success:
                    scores[model_key] += 1.0
                else:
                    scores[model_key] -= 0.5

        # 确保所有分数非负（最低 0.1 的等效分数）
        min_score = 0.1
        total_score = sum(max(min_score, s + 1) for s in scores.values())

        w1 = max(min_score, (scores["markov"] + 1) / total_score)
        w2 = max(min_score, (scores["hmm"] + 1) / total_score)
        w3 = max(min_score, (scores["bayesian"] + 1) / total_score)

        # 归一化
        total = w1 + w2 + w3
        return {
            "w1": round(w1 / total, 2),
            "w2": round(w2 / total, 2),
            "w3": round(w3 / total, 2),
        }

    def calculate_accuracy(self, history: List[Dict]) -> Dict:
        """计算预测准确率统计"""
        if not history:
            return {"total": 0, "total_count": 0}

        correct = 0
        for r in history:
            pred = r.get("predicted_rate")
            actual = r.get("actual_result")
            if pred is None or actual is None:
                continue
            if (pred >= 0.5) == (actual == "success"):
                correct += 1

        total = len(history)
        return {
            "total": round(correct / total, 4) if total > 0 else 0,
            "total_count": total,
        }
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_ensemble.py -v
```

Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/app/models/ensemble.py backend/tests/test_ensemble.py
git commit -m "feat: 添加模型融合、置信度计算、操作建议和权重校准模块"
```

---

### Task 7: API 路由 (predict.py)

**Files:**
- Create: `backend/app/api/predict.py`
- Create: `backend/tests/test_api.py`

- [ ] **Step 1: 编写测试 test_api.py**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint():
    """POST /api/predict 应返回完整预测结果"""
    response = client.post("/api/predict", json={
        "enhance_level": "+10",
        "badge_level": 7,
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
    """短序列预测也能工作"""
    response = client.post("/api/predict", json={
        "enhance_level": "+10",
        "badge_level": 7,
        "results": ["S", "F"],
    })
    assert response.status_code == 200


def test_probabilities_endpoint():
    """GET /api/probabilities 应返回概率表"""
    response = client.get("/api/probabilities")
    assert response.status_code == 200
    data = response.json()
    assert "enhance" in data
    assert "badge" in data
    assert data["enhance"]["+10"] == 0.40
    assert data["badge"]["7"] == 0.50


def test_feedback_endpoint():
    """POST /api/feedback 应返回校准后的权重"""
    response = client.post("/api/feedback", json={
        "session_id": "test123",
        "actual_result": "success",
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
    """POST /api/learn 应返回学习结果"""
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/test_api.py -v
```

Expected: FAIL（app.main 不存在）

- [ ] **Step 3: 编写 predict.py（API 路由）**

```python
"""API 路由定义

四个端点：
- POST /api/predict    预测增幅概率
- GET  /api/probabilities  返回概率表
- POST /api/feedback   用户反馈结果，校准权重
- POST /api/learn      长期学习（经验模式表、马尔可夫阶数测试）
"""
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.models.ensemble import EnsemblePredictor
from app.data.probabilities import ENHANCE_RATES, BADGE_RATES

router = APIRouter(prefix="/api")
ensemble = EnsemblePredictor()


# --- 请求/响应模型 ---

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


# --- 路由 ---

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
        stage = "cold"
        label = "学习中"
    elif count < 20:
        stage = "growing"
        label = "成长中"
    elif count < 50:
        stage = "mature"
        label = "较成熟"
    else:
        stage = "expert"
        label = "高度个性化"

    # 找出表现最好的模型
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

    # 构建经验模式表：按最后3次垫手结果分组统计
    patterns = {}
    for record in history:
        pads = record["pad_results"]
        if len(pads) >= 3:
            suffix = "".join(pads[-3:])
        else:
            suffix = "".join(pads)

        if suffix not in patterns:
            patterns[suffix] = {"count": 0, "success": 0}
        patterns[suffix]["count"] += 1
        if record["actual_result"] == "success":
            patterns[suffix]["success"] += 1

    empirical_patterns = {}
    for k, v in patterns.items():
        if v["count"] >= 2:
            empirical_patterns[k] = {
                "count": v["count"],
                "success_rate": round(v["success"] / v["count"], 4),
            }

    # 计算个人实际成功率（按增幅等级）
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

    # 马尔可夫阶数测试（简单版：数据>30时建议升级）
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
```

- [ ] **Step 4: 编写 main.py（FastAPI 入口 + CORS）**

```python
"""FastAPI 应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.predict import router

app = FastAPI(
    title="DNF增幅概率预测器 API",
    description="基于马尔可夫链、HMM、贝叶斯更新的增幅概率预测服务",
    version="1.0.0",
)

# CORS 配置：允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为 Vercel 域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"service": "DNF Enhancement Predictor API", "version": "1.0.0"}
```

- [ ] **Step 5: 运行全部测试**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
python -m pytest tests/ -v
```

Expected: 全部 PASS

- [ ] **Step 6: 验证 API 启动**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/backend"
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/ | python -m json.tool
curl -s http://localhost:8000/api/probabilities | python -m json.tool
kill %1
```

Expected: 返回正确的 JSON

- [ ] **Step 7: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add backend/
git commit -m "feat: 添加 FastAPI 路由、CORS 配置和完整 API 测试"
```

---

## 自审检查

### 1. 规格覆盖

| 规格需求 | 对应 Task |
|---------|----------|
| FastAPI + Uvicorn 框架 | Task 7 (main.py) |
| NumPy / SciPy / hmmlearn | Task 1 (requirements.txt) |
| 马尔可夫链模型（2阶，可升级3-4阶） | Task 3 (markov.py) |
| HMM 模型（3隐藏状态，Baum-Welch 训练，Viterbi 推断） | Task 5 (hmm_model.py) |
| 贝叶斯更新（Beta 分布先验） | Task 4 (bayesian.py) |
| 三模型加权融合 | Task 6 (ensemble.py) |
| 置信度计算（次数+一致性） | Task 6 (ensemble.py) |
| 操作建议逻辑（4级建议+颜色） | Task 6 (ensemble.py) |
| POST /api/predict | Task 7 (predict.py) |
| GET /api/probabilities | Task 7 (predict.py) |
| POST /api/feedback（权重校准） | Task 6 + Task 7 |
| POST /api/learn（经验模式表+马尔可夫阶数） | Task 7 (predict.py) |
| CORS 跨域配置 | Task 7 (main.py) |
| 概率表数据 | Task 2 (probabilities.py) |
| Render 部署配置 | Task 1 (render.yaml) |
| HMM 降级（数据<8次时） | Task 5 (hmm_model.py) |

### 2. 占位符扫描

无 TBD / TODO / "implement later" / "add appropriate error handling"。

### 3. 类型一致性

- `predict()` 返回字典的 key 在 test_api.py 和 ensemble.py 中一致
- `calibrate_weights()` 输入 `List[Dict]` 在 ensemble.py 定义和 test_ensemble.py/test_api.py 中使用一致
- `calculate_accuracy()` 输入 `List[Dict]`，key `predicted_rate`、`actual_result` 在测试和实现中一致
- `FeedbackHistoryItem` 和 `LearnHistoryItem` 的字段名与前端 `api.js` 发送的 JSON key 匹配
- `ENHANCE_RATES` 和 `BADGE_RATES` 的 key 格式与前端 `api.js` 一致
