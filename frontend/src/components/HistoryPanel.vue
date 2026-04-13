<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70" @click.self="$emit('close')">
    <div class="bg-dnf-darker rounded-xl w-full max-w-2xl max-h-[85vh] flex flex-col border border-dnf-card mx-4">
      <!-- 头部 -->
      <div class="flex items-center justify-between p-4 border-b border-dnf-card">
        <h2 class="text-lg font-bold text-dnf-gold">历史记录</h2>
        <div class="flex gap-2">
          <button
            class="text-sm text-red-400 hover:text-red-300 px-2 py-1"
            @click="confirmClear"
          >
            清空历史
          </button>
          <button class="text-gray-400 hover:text-white text-2xl leading-none" @click="$emit('close')">&times;</button>
        </div>
      </div>

      <!-- 记录列表 -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="records.length === 0" class="text-center text-gray-500 py-8">
          暂无历史记录
        </div>
        <div
          v-for="(record, i) in records"
          :key="i"
          class="bg-dnf-dark rounded-lg p-3 border border-dnf-card"
        >
          <div class="flex items-center justify-between mb-1">
            <span class="text-sm text-gray-400">{{ formatTime(record.timestamp) }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded"
              :class="record.actual_result === 'success'
                ? 'bg-green-900/40 text-green-400'
                : 'bg-red-900/40 text-red-400'"
            >
              {{ record.actual_result === 'success' ? '成功' : '失败' }}
            </span>
          </div>
          <div class="flex items-center gap-4 text-sm">
            <span class="text-gray-400">等级: <span class="text-white">{{ record.enhance_level }}</span></span>
            <span class="text-gray-400">预测: <span class="text-dnf-gold">{{ (record.predicted_rate * 100).toFixed(1) }}%</span></span>
            <span class="text-gray-400">基础: <span class="text-white">{{ (record.base_rate * 100).toFixed(0) }}%</span></span>
          </div>
          <div class="mt-1 text-xs text-gray-500">
            垫手序列: {{ record.pad_results.map((r, idx) => `${idx + 1}${r === 'S' ? '✓' : '✗'}`).join(' ') }}
          </div>
          <!-- 按等级准确率 -->
          <div v-if="record.models" class="mt-1 flex gap-3 text-xs text-gray-500">
            <span>马: {{ record.models.markov_prob ? (record.models.markov_prob * 100).toFixed(0) + '%' : '--' }}</span>
            <span>HMM: {{ record.models.hmm_prob ? (record.models.hmm_prob * 100).toFixed(0) + '%' : '--' }}</span>
            <span>贝: {{ record.models.bayesian_prob ? (record.models.bayesian_prob * 100).toFixed(0) + '%' : '--' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  records: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'clearHistory'])

function formatTime(ts) {
  if (!ts) return '--'
  const d = new Date(ts)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

function confirmClear() {
  if (confirm('确定要清空所有历史记录吗？此操作不可撤销。')) {
    emit('clearHistory')
  }
}
</script>
