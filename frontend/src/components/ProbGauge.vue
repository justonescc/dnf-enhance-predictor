<template>
  <div class="card text-center">
    <h2 class="text-lg font-bold text-dnf-gold mb-4">概率仪表盘</h2>

    <!-- 无数据状态 -->
    <div v-if="predictedRate == null && !loading" class="py-8 text-gray-500">
      开始记录垫手结果后将显示预测概率
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="py-8 text-gray-400">
      <div class="animate-pulse text-2xl mb-2">...</div>
      <p class="text-sm">正在计算预测...</p>
    </div>

    <!-- 仪表盘主体 -->
    <div v-if="predictedRate != null && !loading">
      <!-- 弧形进度条 -->
      <div class="relative w-48 h-28 mx-auto mb-2">
        <svg viewBox="0 0 200 120" class="w-full h-full">
          <!-- 背景弧 -->
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#333"
            stroke-width="16"
            stroke-linecap="round"
          />
          <!-- 概率弧 -->
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            :stroke="arcColor"
            :stroke-width="16"
            stroke-linecap="round"
            :stroke-dasharray="arcLength"
            class="transition-all duration-700 ease-out"
          />
        </svg>
        <!-- 中央数字 -->
        <div class="absolute inset-0 flex flex-col items-center justify-end pb-1">
          <span class="text-4xl font-bold" :class="textColor">
            {{ (predictedRate * 100).toFixed(1) }}%
          </span>
        </div>
      </div>

      <!-- 对比条 -->
      <div class="max-w-xs mx-auto mb-3 space-y-1">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-gray-400 w-16 text-right">基础</span>
          <div class="flex-1 bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              class="h-full bg-gray-400 rounded-full transition-all duration-500"
              :style="{ width: (baseRate * 100) + '%' }"
            ></div>
          </div>
          <span class="text-gray-400 w-12">{{ (baseRate * 100).toFixed(0) }}%</span>
        </div>
        <div class="flex items-center gap-2 text-sm">
          <span class="text-gray-400 w-16 text-right">预测</span>
          <div class="flex-1 bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-500"
              :class="barColor"
              :style="{ width: Math.min(predictedRate * 100, 100) + '%' }"
            ></div>
          </div>
          <span class="font-bold w-12" :class="textColor">{{ (predictedRate * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <!-- 置信度 -->
      <div class="mb-3">
        <div class="flex items-center justify-center gap-2 text-sm">
          <span class="text-gray-400">置信度:</span>
          <div class="w-24 bg-gray-700 rounded-full h-2 overflow-hidden">
            <div
              class="h-full bg-dnf-yellow rounded-full transition-all duration-500"
              :style="{ width: (confidence * 100) + '%' }"
            ></div>
          </div>
          <span class="text-dnf-yellow font-bold">{{ (confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>

      <!-- 建议文字 -->
      <div
        class="rounded-lg px-4 py-2 text-sm font-medium"
        :class="recBgClass"
      >
        {{ recommendation }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  predictedRate: { type: Number, default: null },
  baseRate: { type: Number, default: null },
  confidence: { type: Number, default: 0 },
  recommendation: { type: String, default: '' },
  recommendationLevel: { type: String, default: 'yellow' },
  loading: { type: Boolean, default: false }
})

// 弧形总长度 ≈ π * 80 ≈ 251
const arcLength = computed(() => {
  const total = 251
  const filled = total * (props.predictedRate || 0)
  return `${filled} ${total - filled}`
})

const arcColor = computed(() => {
  const rate = props.predictedRate || 0
  if (rate > 0.6) return '#44ff44'
  if (rate > 0.4) return '#ffdd44'
  return '#ff4444'
})

const textColor = computed(() => {
  const map = { green: 'text-dnf-green', yellow: 'text-dnf-yellow', orange: 'text-dnf-orange', red: 'text-dnf-red' }
  return map[props.recommendationLevel] || 'text-dnf-yellow'
})

const barColor = computed(() => {
  const map = { green: 'bg-dnf-green', yellow: 'bg-dnf-yellow', orange: 'bg-dnf-orange', red: 'bg-dnf-red' }
  return map[props.recommendationLevel] || 'bg-dnf-yellow'
})

const recBgClass = computed(() => {
  const map = {
    green: 'bg-green-900/30 border border-green-700 text-green-300',
    yellow: 'bg-yellow-900/30 border border-yellow-700 text-yellow-300',
    orange: 'bg-orange-900/30 border border-orange-700 text-orange-300',
    red: 'bg-red-900/30 border border-red-700 text-red-300'
  }
  return map[props.recommendationLevel] || map.yellow
})
</script>