import axios from 'axios'

// 后端 API 基础地址，部署后替换为实际 Render 地址
const API_BASE = import.meta.env.VITE_API_BASE || ''

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30秒超时，覆盖冷启动等待
  headers: { 'Content-Type': 'application/json' }
})

// 增幅概率表（前端本地备用）
const ENHANCE_RATES = {
  '+0': 0.55, '+1': 0.55, '+2': 0.55, '+3': 0.55,
  '+4': 0.80, '+5': 0.70, '+6': 0.60, '+7': 0.70,
  '+8': 0.60, '+9': 0.50, '+10': 0.40, '+11': 0.30,
  '+12': 0.20, '+13': 0.20, '+14': 0.20, '+15': 0.20,
  '+16': 0.20, '+17': 0.20, '+18': 0.20, '+19': 0.20
}

// 徽章合成概率表
const BADGE_RATES = {
  5: 0.70, 6: 0.60, 7: 0.50, 8: 0.40, 9: 0.30, 10: 0.30
}

/**
 * 发送预测请求
 */
export async function predict(enhanceLevel, badgeLevel, results) {
  try {
    const { data } = await apiClient.post('/api/predict', {
      enhance_level: enhanceLevel,
      badge_level: badgeLevel,
      results
    })
    return data
  } catch (error) {
    // 后端不可用时，使用前端简易算法降级
    console.warn('后端不可用，使用前端降级预测')
    return localFallbackPredict(enhanceLevel, badgeLevel, results)
  }
}

/**
 * 发送反馈请求
 */
export async function feedback(actualResult, historyRecords, currentWeights) {
  try {
    const feedbackHistory = historyRecords
      .filter(r => r.predicted_rate != null && r.actual_result)
      .slice(0, 20)
      .map(r => ({
        predicted_rate: r.predicted_rate,
        markov_prob: r.models?.markov_prob,
        hmm_prob: r.models?.hmm_prob,
        bayesian_prob: r.models?.bayesian_prob,
        actual_result: r.actual_result
      }))

    const { data } = await apiClient.post('/api/feedback', {
      session_id: Date.now().toString(36),
      actual_result: actualResult,
      history: feedbackHistory
    })
    return data
  } catch (error) {
    console.warn('反馈请求失败，跳过服务端校准')
    return { new_weights: null }
  }
}

/**
 * 获取概率表
 */
export async function getProbabilities() {
  try {
    const { data } = await apiClient.get('/api/probabilities')
    return data
  } catch {
    return { enhance: ENHANCE_RATES, badge: BADGE_RATES }
  }
}

/**
 * 前端降级预测（后端不可用时）
 * 简化版贝叶斯 + 马尔可夫
 */
function localFallbackPredict(enhanceLevel, badgeLevel, results) {
  const baseRate = ENHANCE_RATES[enhanceLevel] || 0.20
  const badgeRate = BADGE_RATES[badgeLevel] || 0.50

  // 简化贝叶斯：用垫手结果更新概率
  const successCount = results.filter(r => r === 'S').length
  const failCount = results.filter(r => r === 'F').length
  // 先验 alpha/beta 使得均值 = badgeRate
  let alpha = badgeRate * 10
  let beta = (1 - badgeRate) * 10
  alpha += successCount
  beta += failCount
  const bayesianProb = alpha / (alpha + beta)

  // 简化马尔可夫：看最后2次结果的转移
  let markovProb = badgeRate
  if (results.length >= 2) {
    const last2 = results.slice(-2).join('')
    const patternCounts = { SS: { s: 0, f: 0 }, SF: { s: 0, f: 0 }, FS: { s: 0, f: 0 }, FF: { s: 0, f: 0 } }
    for (let i = 0; i < results.length - 2; i++) {
      const key = results[i] + results[i + 1]
      const next = results[i + 2]
      if (patternCounts[key]) {
        if (next === 'S') patternCounts[key].s++
        else patternCounts[key].f++
      }
    }
    const match = patternCounts[last2]
    if (match && (match.s + match.f) > 0) {
      markovProb = match.s / (match.s + match.f)
    }
  }

  // 加权融合
  const predictedRate = 0.5 * markovProb + 0.5 * bayesianProb

  // 置信度
  const n = results.length
  let confidence = 0.2
  if (n >= 5) confidence = 0.3
  if (n >= 10) confidence = 0.5
  if (n >= 15) confidence = 0.7

  // 操作建议
  const { text, level, rec } = getRecommendation(predictedRate, baseRate)

  // 趋势数据：模拟每步的累积概率
  const trend = []
  for (let i = 1; i <= results.length; i++) {
    const partial = results.slice(0, i)
    const sc = partial.filter(r => r === 'S').length
    const fc = partial.filter(r => r === 'F').length
    const pa = badgeRate * 10 + sc
    const pb = (1 - badgeRate) * 10 + fc
    trend.push({ step: i, prob: Math.round((pa / (pa + pb)) * 1000) / 1000 })
  }

  return {
    predicted_rate: Math.round(predictedRate * 1000) / 1000,
    base_rate: baseRate,
    confidence,
    recommendation: rec,
    recommendation_text: text,
    recommendation_level: level,
    models: {
      markov_prob: Math.round(markovProb * 1000) / 1000,
      hmm_prob: null,
      hmm_state: '不可用',
      bayesian_prob: Math.round(bayesianProb * 1000) / 1000,
      bayesian_alpha: Math.round(alpha * 10) / 10,
      bayesian_beta: Math.round(beta * 10) / 10
    },
    trend
  }
}

function getRecommendation(predicted, base) {
  if (predicted > base * 1.3) {
    return {
      rec: 'enhance',
      text: `预测成功率 ${(predicted * 100).toFixed(1)}%，高于基础 ${(base * 100).toFixed(0)}%，建议直接增幅`,
      level: 'green'
    }
  }
  if (predicted >= base * 1.1) {
    return {
      rec: 'consider',
      text: `预测成功率 ${(predicted * 100).toFixed(1)}%，略高于基础 ${(base * 100).toFixed(0)}%，可以再垫几手`,
      level: 'yellow'
    }
  }
  if (predicted >= base * 0.8) {
    return {
      rec: 'pad',
      text: `预测成功率 ${(predicted * 100).toFixed(1)}%，接近基础 ${(base * 100).toFixed(0)}%，建议继续垫手`,
      level: 'orange'
    }
  }
  return {
    rec: 'avoid',
    text: `预测成功率 ${(predicted * 100).toFixed(1)}%，低于基础 ${(base * 100).toFixed(0)}%，不建议此时增幅`,
    level: 'red'
  }
}

export { ENHANCE_RATES, BADGE_RATES }
