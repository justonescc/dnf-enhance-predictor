<template>
  <div class="card">
    <h2 class="text-lg font-bold text-dnf-gold mb-3">模型详情</h2>

    <div class="space-y-2 text-sm">
      <!-- 马尔可夫 -->
      <div class="flex justify-between items-center">
        <span class="text-gray-400">马尔可夫链</span>
        <span class="font-mono" :class="models.markov_prob != null ? 'text-white' : 'text-gray-600'">
          {{ models.markov_prob != null ? (models.markov_prob * 100).toFixed(1) + '%' : '--' }}
        </span>
      </div>

      <!-- HMM -->
      <div class="flex justify-between items-center">
        <span class="text-gray-400">隐马尔可夫</span>
        <span class="font-mono" :class="models.hmm_prob != null ? 'text-white' : 'text-gray-600'">
          {{ models.hmm_prob != null ? (models.hmm_prob * 100).toFixed(1) + '%' : '--' }}
          <span v-if="models.hmm_state && models.hmm_state !== '不可用'" class="text-xs text-gray-500 ml-1">
            ({{ hmmStateLabel }})
          </span>
        </span>
      </div>

      <!-- 贝叶斯 -->
      <div class="flex justify-between items-center">
        <span class="text-gray-400">贝叶斯更新</span>
        <span class="font-mono" :class="models.bayesian_prob != null ? 'text-white' : 'text-gray-600'">
          {{ models.bayesian_prob != null ? (models.bayesian_prob * 100).toFixed(1) + '%' : '--' }}
        </span>
      </div>

      <hr class="border-dnf-card my-2">

      <!-- 准确率 -->
      <div class="flex justify-between items-center">
        <span class="text-gray-400">预测准确率</span>
        <span class="font-mono text-dnf-gold">
          {{ accuracy.total > 0 ? (accuracy.total * 100).toFixed(1) + '%' : '--' }}
          <span class="text-xs text-gray-500">({{ accuracy.total_count }}次)</span>
        </span>
      </div>

      <!-- 趋势指示 -->
      <div v-if="accuracy.trend !== 'none' && accuracy.total_count > 0" class="flex justify-between items-center">
        <span class="text-gray-400">近期趋势</span>
        <span :class="trendClass">
          {{ accuracy.trend === 'up' ? '上升 ↑' : accuracy.trend === 'down' ? '下降 ↓' : '稳定 →' }}
        </span>
      </div>

      <hr class="border-dnf-card my-2">

      <!-- 学习阶段 -->
      <div class="flex justify-between items-center">
        <span class="text-gray-400">学习阶段</span>
        <span :class="learningStage.color" class="font-medium">
          {{ learningStage.label }}
          <span class="text-xs text-gray-500">({{ recordCount }}条)</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  models: {
    type: Object,
    default: () => ({ markov_prob: null, hmm_prob: null, hmm_state: '', bayesian_prob: null })
  },
  accuracy: {
    type: Object,
    default: () => ({ total: 0, total_count: 0, trend: 'none' })
  },
  learningStage: {
    type: Object,
    default: () => ({ key: 'cold', label: '学习中', color: 'text-dnf-yellow' })
  },
  recordCount: { type: Number, default: 0 }
})

const hmmStateLabel = computed(() => {
  const map = { lucky: '好运', normal: '普通', unlucky: '差运' }
  return map[props.models.hmm_state] || props.models.hmm_state
})

const trendClass = computed(() => {
  if (props.accuracy.trend === 'up') return 'text-dnf-green'
  if (props.accuracy.trend === 'down') return 'text-dnf-red'
  return 'text-gray-400'
})
</script>
