<template>
  <div class="card">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-lg font-bold text-dnf-gold">垫手记录</h2>
      <span class="text-sm text-gray-400">{{ results.length }}/20</span>
    </div>

    <!-- 垫手序列展示 -->
    <div class="flex flex-wrap gap-2 mb-4 min-h-[60px]">
      <span
        v-for="(r, i) in results"
        :key="i"
        class="inline-flex items-center justify-center w-10 h-10 rounded-lg text-sm font-bold border"
        :class="r === 'S'
          ? 'bg-green-900/40 border-green-600 text-green-400'
          : 'bg-red-900/40 border-red-600 text-red-400'"
      >
        {{ i + 1 }}{{ r === 'S' ? '✓' : '✗' }}
      </span>
      <span
        v-if="results.length === 0"
        class="text-gray-500 text-sm flex items-center"
      >
        点击下方按钮记录垫手结果（10-20次）
      </span>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-2">
      <button
        class="flex-1 btn-gold touch-target"
        @click="addResult('S')"
        :disabled="results.length >= 20"
      >
        成功
      </button>
      <button
        class="flex-1 btn-red touch-target"
        @click="addResult('F')"
        :disabled="results.length >= 20"
      >
        失败
      </button>
      <button
        class="bg-gray-700 text-gray-300 px-3 py-2 rounded-lg text-sm hover:bg-gray-600 touch-target"
        @click="undo"
        :disabled="results.length === 0"
      >
        撤销
      </button>
      <button
        class="bg-gray-700 text-gray-300 px-3 py-2 rounded-lg text-sm hover:bg-gray-600 touch-target"
        @click="$emit('clear')"
        :disabled="results.length === 0"
      >
        清除
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  results: { type: Array, default: () => [] },
  badgeLevel: { type: Number, default: 7 }
})

const emit = defineEmits(['update:results', 'clear'])

function addResult(result) {
  if (props.results.length >= 20) return
  const newResults = [...props.results, result]
  emit('update:results', newResults)
}

function undo() {
  if (props.results.length === 0) return
  const newResults = props.results.slice(0, -1)
  emit('update:results', newResults)
}
</script>