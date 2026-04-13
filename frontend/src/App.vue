<template>
  <div class="min-h-screen bg-dnf-dark">
    <!-- 顶部导航 -->
    <header class="border-b border-dnf-card px-4 py-3 flex items-center justify-between">
      <h1 class="text-xl font-bold text-dnf-gold">DNF增幅概率预测器</h1>
      <div class="flex gap-2">
        <button class="btn-gold text-sm" @click="showHistory = true">历史</button>
        <DataIO @import-complete="onImportComplete" />
      </div>
    </header>

    <main class="max-w-6xl mx-auto p-4">
      <!-- PC端：左右布局 / 移动端：纵向堆叠 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 左侧：设置 + 垫手记录 -->
        <div class="space-y-4">
          <EnhanceSetting
            v-model:enhance-level="enhanceLevel"
            v-model:badge-level="badgeLevel"
          />
          <PadRecord
            v-model:results="padResults"
            :badge-level="badgeLevel"
            @clear="onClear"
          />
        </div>

        <!-- 右侧：仪表盘 + 模型详情 -->
        <div class="space-y-4">
          <ProbGauge
            :predicted-rate="prediction.predicted_rate"
            :base-rate="prediction.base_rate"
            :confidence="prediction.confidence"
            :recommendation="prediction.recommendation_text"
            :recommendation-level="prediction.recommendation_level"
            :loading="loading"
          />
          <FeedbackButtons
            :can-feedback="padResults.length >= 10"
            @feedback="onFeedback"
          />
          <ModelDetail
            :models="prediction.models"
            :accuracy="accuracy"
            :learning-stage="learningStage"
            :record-count="recordCount"
          />
        </div>
      </div>

      <!-- 趋势图：全宽 -->
      <div class="mt-4">
        <TrendChart :trend-data="prediction.trend" />
      </div>
    </main>

    <!-- 历史面板弹窗 -->
    <HistoryPanel
      v-if="showHistory"
      :records="historyRecords"
      @close="showHistory = false"
      @clear-history="onClearHistory"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import EnhanceSetting from './components/EnhanceSetting.vue'
import PadRecord from './components/PadRecord.vue'
import ProbGauge from './components/ProbGauge.vue'
import FeedbackButtons from './components/FeedbackButtons.vue'
import ModelDetail from './components/ModelDetail.vue'
import TrendChart from './components/TrendChart.vue'
import HistoryPanel from './components/HistoryPanel.vue'
import DataIO from './components/DataIO.vue'
import { predict, feedback } from './services/api.js'
import { loadHistory, saveRecord, clearHistory, getAccuracy, getWeights, saveWeights } from './services/storage.js'

// --- 状态 ---
const enhanceLevel = ref('+10')
const badgeLevel = ref(7)
const padResults = ref([])
const loading = ref(false)
const showHistory = ref(false)

const prediction = reactive({
  predicted_rate: null,
  base_rate: null,
  confidence: null,
  recommendation: '',
  recommendation_text: '',
  recommendation_level: 'yellow',
  models: { markov_prob: null, hmm_prob: null, hmm_state: '', bayesian_prob: null },
  trend: []
})

const historyRecords = ref(loadHistory())
const recordCount = computed(() => historyRecords.value.length)
const accuracy = computed(() => getAccuracy(historyRecords.value))
const learningStage = computed(() => {
  const n = recordCount.value
  if (n < 5) return { key: 'cold', label: '学习中', color: 'text-dnf-yellow' }
  if (n < 20) return { key: 'growing', label: '成长中', color: 'text-dnf-green' }
  if (n < 50) return { key: 'mature', label: '较成熟', color: 'text-dnf-green' }
  return { key: 'expert', label: '高度个性化', color: 'text-dnf-gold' }
})

// --- 自动预测 ---
watch([padResults, enhanceLevel, badgeLevel], async () => {
  if (padResults.value.length < 2) {
    resetPrediction()
    return
  }
  loading.value = true
  try {
    const res = await predict(enhanceLevel.value, badgeLevel.value, padResults.value)
    Object.assign(prediction, res)
  } catch (e) {
    console.error('预测请求失败:', e)
  } finally {
    loading.value = false
  }
}, { deep: true })

function resetPrediction() {
  prediction.predicted_rate = null
  prediction.base_rate = null
  prediction.confidence = null
  prediction.recommendation = ''
  prediction.recommendation_text = ''
  prediction.recommendation_level = 'yellow'
  prediction.models = { markov_prob: null, hmm_prob: null, hmm_state: '', bayesian_prob: null }
  prediction.trend = []
}

// --- 垫手操作 ---
function onClear() {
  padResults.value = []
  resetPrediction()
}

// --- 反馈 ---
async function onFeedback(actualResult) {
  if (!prediction.predicted_rate) return
  const record = {
    timestamp: new Date().toISOString(),
    enhance_level: enhanceLevel.value,
    badge_level: badgeLevel.value,
    pad_results: [...padResults.value],
    predicted_rate: prediction.predicted_rate,
    base_rate: prediction.base_rate,
    recommendation: prediction.recommendation,
    actual_result: actualResult,
    models: { ...prediction.models }
  }
  historyRecords.value.unshift(record)
  saveRecord(record)

  // 发送反馈给后端进行权重校准
  try {
    const weights = getWeights()
    const res = await feedback(actualResult, historyRecords.value, weights)
    if (res.new_weights) {
      saveWeights(res.new_weights)
    }
  } catch (e) {
    console.error('反馈请求失败:', e)
  }

  // 清空垫手记录，准备下一轮
  onClear()
}

// --- 历史 ---
function onClearHistory() {
  clearHistory()
  historyRecords.value = []
}

function onImportComplete(data) {
  historyRecords.value = data
}
</script>
