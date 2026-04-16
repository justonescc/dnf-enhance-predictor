/**
 * 纯前端预测引擎 — 移植自后端 Python 实现
 * 包含：马尔可夫链、贝叶斯更新、HMM（Baum-Welch + Viterbi）、集成预测、权重校准、学习分析
 */

// ─── 概率表 ───
const ENHANCE_RATES = {
  '+0': 0.55, '+1': 0.55, '+2': 0.55, '+3': 0.55,
  '+4': 0.80, '+5': 0.70, '+6': 0.60, '+7': 0.70,
  '+8': 0.60, '+9': 0.50, '+10': 0.40, '+11': 0.30,
  '+12': 0.20, '+13': 0.20, '+14': 0.20, '+15': 0.20,
  '+16': 0.20, '+17': 0.20, '+18': 0.20, '+19': 0.20
}

const BADGE_RATES = {
  5: 0.70, 6: 0.60, 7: 0.50, 8: 0.40, 9: 0.30, 10: 0.30
}

function getEnhanceRate(level) {
  return ENHANCE_RATES[level] ?? 0.20
}

function getBadgeRate(badgeLevel) {
  return BADGE_RATES[badgeLevel] ?? 0.50
}

// ─── 马尔可夫链 ───
class MarkovPredictor {
  constructor(order = 2) {
    this.order = order
  }

  predict(results, baseRate) {
    if (results.length <= this.order) return baseRate

    const transitions = {}
    for (let i = 0; i < results.length - this.order; i++) {
      const state = results.slice(i, i + this.order).join('')
      const next = results[i + this.order]
      if (!transitions[state]) transitions[state] = { S: 0, F: 0 }
      transitions[state][next]++
    }

    const currentState = results.slice(-this.order).join('')
    const counts = transitions[currentState]
    if (!counts) return baseRate

    const total = counts.S + counts.F
    return total === 0 ? baseRate : counts.S / total
  }
}

// ─── 贝叶斯更新 ───
class BayesianPredictor {
  constructor(priorStrength = 10) {
    this.priorStrength = priorStrength
  }

  predict(results, baseRate) {
    let alpha = baseRate * this.priorStrength
    let beta = (1 - baseRate) * this.priorStrength
    alpha += results.filter(r => r === 'S').length
    beta += results.filter(r => r === 'F').length
    const prob = alpha / (alpha + beta)
    return { alpha: Math.round(alpha * 100) / 100, beta: Math.round(beta * 100) / 100, prob: Math.round(prob * 10000) / 10000 }
  }

  getTrend(results, baseRate) {
    const trend = []
    for (let i = 1; i <= results.length; i++) {
      const { prob } = this.predict(results.slice(0, i), baseRate)
      trend.push({ step: i, prob })
    }
    return trend
  }
}

// ─── HMM（纯 JS 实现 Baum-Welch + Viterbi）───
class HMMPredictor {
  constructor(nComponents = 3) {
    this.nComponents = nComponents
  }

  predict(results, baseRate) {
    if (results.length < 8) return { prob: baseRate, state: 'normal' }
    try {
      return this._hmmPredict(results, baseRate)
    } catch {
      return { prob: baseRate, state: 'normal' }
    }
  }

  _initTransmat(K) {
    const trans = Array.from({ length: K }, () => Array(K).fill(0.1))
    for (let i = 0; i < K; i++) trans[i][i] = 0.8
    for (let i = 0; i < K; i++) {
      const rowSum = trans[i].reduce((a, b) => a + b, 0)
      for (let j = 0; j < K; j++) trans[i][j] /= rowSum
    }
    return trans
  }

  _viterbi(obs, startprob, transmat, emissionprob, K) {
    const n = obs.length
    const V = Array.from({ length: n }, () => Array(K).fill(0))
    const backptr = Array.from({ length: n }, () => Array(K).fill(0))

    for (let k = 0; k < K; k++) {
      V[0][k] = Math.log(Math.max(startprob[k], 1e-10)) + Math.log(Math.max(emissionprob[k][obs[0]], 1e-10))
    }

    for (let t = 1; t < n; t++) {
      for (let j = 0; j < K; j++) {
        let bestVal = -Infinity, bestI = 0
        for (let i = 0; i < K; i++) {
          const val = V[t - 1][i] + Math.log(Math.max(transmat[i][j], 1e-10))
          if (val > bestVal) { bestVal = val; bestI = i }
        }
        V[t][j] = bestVal + Math.log(Math.max(emissionprob[j][obs[t]], 1e-10))
        backptr[t][j] = bestI
      }
    }

    const path = Array(n).fill(0)
    path[n - 1] = V[n - 1].reduce((best, v, k) => v > V[n - 1][best] ? k : best, 0)
    for (let t = n - 2; t >= 0; t--) path[t] = backptr[t + 1][path[t + 1]]
    return path
  }

  _hmmPredict(results, baseRate) {
    const obs = results.map(r => r === 'S' ? 1 : 0)
    const n = obs.length
    const K = this.nComponents

    let startprob = Array(K).fill(1.0 / K)
    let transmat = this._initTransmat(K)

    let emissionprob = [
      [Math.min(baseRate * 1.5, 0.95), Math.max(1 - baseRate * 1.5, 0.05)],
      [baseRate, 1 - baseRate],
      [Math.max(baseRate * 0.5, 0.05), Math.min(1 - baseRate * 0.5, 0.95)]
    ]

    // Baum-Welch EM iterations
    for (let iter = 0; iter < 50; iter++) {
      // Forward
      const alpha = Array.from({ length: n }, () => Array(K).fill(0))
      const scale = Array(n).fill(0)

      for (let k = 0; k < K; k++) alpha[0][k] = startprob[k] * emissionprob[k][obs[0]]
      scale[0] = alpha[0].reduce((a, b) => a + b, 0)
      if (scale[0] > 0) for (let k = 0; k < K; k++) alpha[0][k] /= scale[0]

      for (let t = 1; t < n; t++) {
        for (let j = 0; j < K; j++) {
          let s = 0
          for (let i = 0; i < K; i++) s += alpha[t - 1][i] * transmat[i][j]
          alpha[t][j] = s * emissionprob[j][obs[t]]
        }
        scale[t] = alpha[t].reduce((a, b) => a + b, 0)
        if (scale[t] > 0) for (let j = 0; j < K; j++) alpha[t][j] /= scale[t]
      }

      // Backward
      const beta = Array.from({ length: n }, () => Array(K).fill(0))
      for (let k = 0; k < K; k++) beta[n - 1][k] = 1.0

      for (let t = n - 2; t >= 0; t--) {
        for (let i = 0; i < K; i++) {
          let s = 0
          for (let j = 0; j < K; j++) s += transmat[i][j] * emissionprob[j][obs[t + 1]] * beta[t + 1][j]
          beta[t][i] = s
        }
        if (scale[t + 1] > 0) for (let i = 0; i < K; i++) beta[t][i] /= scale[t + 1]
      }

      // Gamma
      const gamma = Array.from({ length: n }, () => Array(K).fill(0))
      for (let t = 0; t < n; t++) {
        let total = 0
        for (let k = 0; k < K; k++) total += alpha[t][k] * beta[t][k]
        if (total > 0) for (let k = 0; k < K; k++) gamma[t][k] = alpha[t][k] * beta[t][k] / total
      }

      // Update startprob
      for (let k = 0; k < K; k++) startprob[k] = gamma[0][k]

      // Update transmat
      for (let i = 0; i < K; i++) {
        let denom = 0
        for (let t = 0; t < n - 1; t++) denom += gamma[t][i]
        if (denom > 0) {
          for (let j = 0; j < K; j++) {
            let num = 0
            for (let t = 0; t < n - 1; t++) {
              let xiVal = alpha[t][i] * transmat[i][j] * emissionprob[j][obs[t + 1]] * beta[t + 1][j]
              let xiTotal = 0
              for (let a = 0; a < K; a++) xiTotal += alpha[t][a] * transmat[a][j] * emissionprob[j][obs[t + 1]] * beta[t + 1][j]
              if (xiTotal > 0) xiVal /= xiTotal
              num += xiVal
            }
            transmat[i][j] = num / denom
          }
        }
        // Normalize
        const rowSum = transmat[i].reduce((a, b) => a + b, 0)
        if (rowSum > 0) for (let j = 0; j < K; j++) transmat[i][j] /= rowSum
      }

      // Update emissionprob
      for (let k = 0; k < K; k++) {
        for (let v = 0; v < 2; v++) {
          let num = 0, denom = 0
          for (let t = 0; t < n; t++) {
            if (obs[t] === v) num += gamma[t][k]
            denom += gamma[t][k]
          }
          if (denom > 0) emissionprob[k][v] = num / denom
        }
        // Clamp & normalize
        emissionprob[k] = emissionprob[k].map(p => Math.max(0.01, Math.min(0.99, p)))
        const epSum = emissionprob[k].reduce((a, b) => a + b, 0)
        emissionprob[k] = emissionprob[k].map(p => p / epSum)
      }
    }

    // Viterbi decode
    const stateSequence = this._viterbi(obs, startprob, transmat, emissionprob, K)
    const currentState = stateSequence[n - 1]

    // Determine state labels
    const stateProbs = emissionprob.map(row => row[0])
    const uniqueProbs = [...new Set(stateProbs.map(p => Math.round(p * 1e6) / 1e6))].sort((a, b) => a - b)
    let prob, labels

    if (uniqueProbs.length >= 2) {
      const sortedIdx = stateProbs.map((p, i) => ({ p, i })).sort((a, b) => a.p - b.p).map(x => x.i)
      labels = { [sortedIdx[0]]: 'unlucky', [sortedIdx[1]]: 'normal', [sortedIdx[2]]: 'lucky' }
      prob = stateProbs[currentState]
    } else {
      const sCount = results.filter(r => r === 'S').length
      const fCount = results.filter(r => r === 'F').length
      if (sCount === 0) {
        prob = Math.max(0.01, baseRate * 0.1)
        labels = { [currentState]: 'unlucky' }
      } else if (fCount === 0) {
        prob = Math.min(0.99, baseRate + (0.99 - baseRate) * 0.8)
        labels = { [currentState]: 'lucky' }
      } else {
        prob = sCount / results.length
        labels = { [currentState]: 'normal' }
      }
    }

    const stateLabel = labels[currentState] ?? 'normal'
    return { prob: Math.round(Math.max(0.01, Math.min(0.99, prob)) * 10000) / 10000, state: stateLabel }
  }
}

// ─── 集成预测 ───
class EnsemblePredictor {
  constructor() {
    this.markov = new MarkovPredictor(2)
    this.hmm = new HMMPredictor()
    this.bayesian = new BayesianPredictor()
  }

  predict({ enhanceLevel, badgeLevel, results, weights, historyCount, empiricalPatterns, personalRates }) {
    const baseRate = getEnhanceRate(enhanceLevel)
    const badgeRate = getBadgeRate(badgeLevel)

    let bayesianPrior = badgeRate
    if (personalRates && personalRates[enhanceLevel] != null) bayesianPrior = personalRates[enhanceLevel]

    const markovProb = this.markov.predict(results, badgeRate)
    const { prob: hmmProb, state: hmmState } = this.hmm.predict(results, badgeRate)
    const { alpha: bayesianAlpha, beta: bayesianBeta, prob: bayesianProb } = this.bayesian.predict(results, bayesianPrior)

    let w1 = weights?.w1 ?? 0.3
    let w2 = weights?.w2 ?? 0.4
    let w3 = weights?.w3 ?? 0.3

    // HMM 降级: 数据<8次
    let resolvedHmmState = hmmState
    if (results.length < 8) {
      w2 = 0; w1 = 0.5; w3 = 0.5
      resolvedHmmState = 'normal'
    }

    // 经验模型
    let empiricalProb = null
    let w4 = 0
    if (historyCount >= 50 && empiricalPatterns && results.length >= 2) {
      for (const suffixLen of [3, 2]) {
        if (results.length >= suffixLen) {
          const suffix = results.slice(-suffixLen).join('')
          const pattern = empiricalPatterns[suffix]
          if (pattern && pattern.count >= 3) {
            empiricalProb = pattern.success_rate
            w1 = 0.2; w2 = 0.3; w3 = 0.2; w4 = 0.3
            break
          }
        }
      }
    }

    let predictedRate = w1 * markovProb + w2 * hmmProb + w3 * bayesianProb
    if (empiricalProb != null) predictedRate += w4 * empiricalProb

    predictedRate = Math.round(Math.max(0.01, Math.min(0.99, predictedRate)) * 10000) / 10000
    const confidence = this._calculateConfidence(results.length, markovProb, hmmProb, bayesianProb)
    const { rec, text, level } = this._getRecommendation(predictedRate, baseRate, confidence)
    const trend = this.bayesian.getTrend(results, bayesianPrior)

    const models = {
      markov_prob: Math.round(markovProb * 10000) / 10000,
      hmm_prob: results.length >= 8 ? Math.round(hmmProb * 10000) / 10000 : null,
      hmm_state: resolvedHmmState,
      bayesian_prob: Math.round(bayesianProb * 10000) / 10000,
      bayesian_alpha: bayesianAlpha,
      bayesian_beta: bayesianBeta
    }
    if (empiricalProb != null) models.empirical_prob = Math.round(empiricalProb * 10000) / 10000

    return {
      predicted_rate: predictedRate,
      base_rate: baseRate,
      confidence: Math.round(confidence * 10000) / 10000,
      recommendation: rec,
      recommendation_text: text,
      recommendation_level: level,
      models,
      trend
    }
  }

  _calculateConfidence(n, p1, p2, p3) {
    let sizeFactor
    if (n < 5) sizeFactor = 0.2
    else if (n < 10) sizeFactor = 0.4
    else if (n < 15) sizeFactor = 0.6
    else sizeFactor = 0.8

    const mean = (p1 + p2 + p3) / 3
    const variance = ((p1 - mean) ** 2 + (p2 - mean) ** 2 + (p3 - mean) ** 2) / 3
    const std = Math.sqrt(variance)
    const agreement = Math.max(0, 1.0 - std * 4)
    return Math.min(0.85, sizeFactor * 0.7 + agreement * 0.3)
  }

  _getRecommendation(predicted, base, confidence) {
    const pct = (predicted * 100).toFixed(1)
    const basePct = (base * 100).toFixed(0)
    if (predicted > base * 1.3 && confidence > 0.5) {
      return { rec: 'enhance', text: `预测成功率 ${pct}%，高于基础 ${basePct}%，建议直接增幅`, level: 'green' }
    }
    if (predicted >= base * 1.1) {
      return { rec: 'consider', text: `预测成功率 ${pct}%，略高于基础 ${basePct}%，可以再垫几手`, level: 'yellow' }
    }
    if (predicted >= base * 0.8) {
      return { rec: 'pad', text: `预测成功率 ${pct}%，接近基础 ${basePct}%，建议继续垫手`, level: 'orange' }
    }
    return { rec: 'avoid', text: `预测成功率 ${pct}%，低于基础 ${basePct}%，不建议此时增幅`, level: 'red' }
  }

  calibrateWeights(history) {
    if (!history || history.length === 0) return { w1: 0.3, w2: 0.4, w3: 0.3 }
    const recent = history.slice(-20)
    const scores = { markov: 0, hmm: 0, bayesian: 0 }
    for (const record of recent) {
      const actualSuccess = record.actual_result === 'success'
      for (const [modelKey, probKey] of [['markov', 'markov_prob'], ['hmm', 'hmm_prob'], ['bayesian', 'bayesian_prob']]) {
        const prob = record[probKey]
        if (prob == null) continue
        scores[modelKey] += (prob >= 0.5) === actualSuccess ? 1.0 : -0.5
      }
    }
    const minScore = 0.1
    const totalScore = Object.values(scores).reduce((sum, s) => sum + Math.max(minScore, s + 1), 0)
    let w1 = Math.max(minScore, (scores.markov + 1) / totalScore)
    let w2 = Math.max(minScore, (scores.hmm + 1) / totalScore)
    let w3 = Math.max(minScore, (scores.bayesian + 1) / totalScore)
    const total = w1 + w2 + w3
    return { w1: Math.round(w1 / total * 100) / 100, w2: Math.round(w2 / total * 100) / 100, w3: Math.round(w3 / total * 100) / 100 }
  }

  calculateAccuracy(history) {
    if (!history || history.length === 0) return { total: 0, total_count: 0 }
    let correct = 0
    for (const r of history) {
      if (r.predicted_rate == null || r.actual_result == null) continue
      if ((r.predicted_rate >= 0.5) === (r.actual_result === 'success')) correct++
    }
    const total = history.length
    return { total: total > 0 ? Math.round(correct / total * 10000) / 10000 : 0, total_count: total }
  }
}

// ─── 导出单例 ───
const ensemble = new EnsemblePredictor()

export { ensemble, ENHANCE_RATES, BADGE_RATES, getEnhanceRate, getBadgeRate }
