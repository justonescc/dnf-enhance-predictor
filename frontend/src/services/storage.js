const STORAGE_KEY = 'dnf_enhance_history'
const WEIGHTS_KEY = 'dnf_enhance_weights'

// 默认模型权重
const DEFAULT_WEIGHTS = { w1: 0.3, w2: 0.4, w3: 0.3 }

/**
 * 加载所有历史记录
 */
export function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

/**
 * 保存单条记录到历史（追加到头部）
 */
export function saveRecord(record) {
  const history = loadHistory()
  history.unshift(record)
  // 保留最近 200 条
  const trimmed = history.slice(0, 200)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
}

/**
 * 用完整数据替换历史（导入时用）
 */
export function replaceHistory(records) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(0, 200)))
}

/**
 * 清空历史
 */
export function clearHistory() {
  localStorage.removeItem(STORAGE_KEY)
}

/**
 * 加载模型权重
 */
export function getWeights() {
  try {
    const raw = localStorage.getItem(WEIGHTS_KEY)
    return raw ? JSON.parse(raw) : { ...DEFAULT_WEIGHTS }
  } catch {
    return { ...DEFAULT_WEIGHTS }
  }
}

/**
 * 保存模型权重
 */
export function saveWeights(weights) {
  localStorage.setItem(WEIGHTS_KEY, JSON.stringify(weights))
}

/**
 * 计算准确率统计
 */
export function getAccuracy(records) {
  if (records.length === 0) {
    return { total: 0, total_count: 0, by_level: {}, trend: 'none' }
  }

  let correct = 0
  const byLevel = {}

  for (const r of records) {
    if (!r.actual_result || !r.predicted_rate) continue
    const predictedSuccess = r.predicted_rate >= 0.5
    const actualSuccess = r.actual_result === 'success'
    if (predictedSuccess === actualSuccess) correct++

    const level = r.enhance_level || 'unknown'
    if (!byLevel[level]) byLevel[level] = { correct: 0, total: 0 }
    byLevel[level].total++
    if (predictedSuccess === actualSuccess) byLevel[level].correct++
  }

  const totalRate = records.length > 0 ? correct / records.length : 0

  // 最近 10 条趋势
  const recent10 = records.slice(0, 10)
  let recentCorrect = 0
  for (const r of recent10) {
    if (!r.actual_result || !r.predicted_rate) continue
    const predictedSuccess = r.predicted_rate >= 0.5
    const actualSuccess = r.actual_result === 'success'
    if (predictedSuccess === actualSuccess) recentCorrect++
  }
  const recentRate = recent10.length > 0 ? recentCorrect / recent10.length : 0
  const trend = recentRate > totalRate ? 'up' : recentRate < totalRate ? 'down' : 'stable'

  return {
    total: totalRate,
    total_count: records.length,
    by_level: byLevel,
    recent_rate: recentRate,
    trend
  }
}
