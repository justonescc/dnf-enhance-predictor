/**
 * 增幅概率预测 API
 * 纯前端实现 — 无需后端服务
 */
import { ensemble, ENHANCE_RATES, BADGE_RATES } from './predictor.js'

/**
 * 发送预测请求
 */
export async function predict(enhanceLevel, badgeLevel, results) {
  return ensemble.predict({
    enhanceLevel,
    badgeLevel,
    results,
    weights: { w1: 0.3, w2: 0.4, w3: 0.3 },
    historyCount: 0,
    empiricalPatterns: null,
    personalRates: null
  })
}

/**
 * 发送反馈请求
 */
export async function feedback(actualResult, historyRecords, currentWeights) {
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

  const newWeights = ensemble.calibrateWeights(feedbackHistory)
  const accuracy = ensemble.calculateAccuracy(feedbackHistory)

  const count = feedbackHistory.length
  let stage, label
  if (count < 5) { stage = 'cold'; label = '学习中' }
  else if (count < 20) { stage = 'growing'; label = '成长中' }
  else if (count < 50) { stage = 'mature'; label = '较成熟' }
  else { stage = 'expert'; label = '高度个性化' }

  const modelNames = { w1: '马尔可夫', w2: 'HMM', w3: '贝叶斯' }
  const bestModel = Object.entries(newWeights).sort((a, b) => b[1] - a[1])[0][0]
  const bestName = modelNames[bestModel]
  const bestVal = newWeights[bestModel]

  return {
    new_weights: newWeights,
    accuracy,
    learning_stage: stage,
    stage_label: label,
    message: `模型权重已校准：${bestName}模型表现最佳，权重提升至${bestVal}`
  }
}

/**
 * 获取概率表
 */
export async function getProbabilities() {
  return { enhance: ENHANCE_RATES, badge: BADGE_RATES }
}

/**
 * 学习分析
 */
export async function learn(history, currentMarkovOrder = 2) {
  const count = history.length

  const patterns = {}
  for (const record of history) {
    const pads = record.pad_results || []
    const suffix = pads.length >= 3 ? pads.slice(-3).join('') : pads.join('')
    if (!patterns[suffix]) patterns[suffix] = { count: 0, success: 0 }
    patterns[suffix].count++
    if (record.actual_result === 'success') patterns[suffix].success++
  }

  const empiricalPatterns = {}
  for (const [k, v] of Object.entries(patterns)) {
    if (v.count >= 2) {
      empiricalPatterns[k] = { count: v.count, success_rate: Math.round(v.success / v.count * 10000) / 10000 }
    }
  }

  const levelStats = {}
  for (const record of history) {
    const level = record.enhance_level || ''
    if (!levelStats[level]) levelStats[level] = { count: 0, success: 0 }
    levelStats[level].count++
    if (record.actual_result === 'success') levelStats[level].success++
  }

  const personalRates = {}
  for (const [level, stats] of Object.entries(levelStats)) {
    if (stats.count >= 3) personalRates[level] = Math.round(stats.success / stats.count * 10000) / 10000
  }

  let markovOrder = currentMarkovOrder
  let upgraded = false
  if (count >= 30 && markovOrder < 4) { markovOrder++; upgraded = true }

  return {
    hmm_retrained: count >= 10,
    markov_order: markovOrder,
    markov_order_upgraded: upgraded,
    empirical_patterns: empiricalPatterns,
    personal_rates: personalRates,
    message: `已用${count}条数据分析，发现${Object.keys(empiricalPatterns).length}种经验模式`
  }
}

export { ENHANCE_RATES, BADGE_RATES }
