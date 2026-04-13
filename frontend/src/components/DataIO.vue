<template>
  <div class="flex gap-2">
    <button class="text-sm bg-dnf-card text-gray-300 px-3 py-1.5 rounded-lg hover:bg-dnf-card/80 touch-target" @click="exportData">
      导出
    </button>
    <button class="text-sm bg-dnf-card text-gray-300 px-3 py-1.5 rounded-lg hover:bg-dnf-card/80 touch-target" @click="triggerImport">
      导入
    </button>
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      class="hidden"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { loadHistory, replaceHistory, getWeights } from '../services/storage.js'

const emit = defineEmits(['importComplete'])
const fileInput = ref(null)

function triggerImport() {
  fileInput.value.click()
}

function exportData() {
  const data = {
    version: '1.0',
    export_time: new Date().toISOString(),
    history: loadHistory(),
    weights: getWeights()
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `dnf_enhance_${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function onFileSelected(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      if (!data.history || !Array.isArray(data.history)) {
        alert('无效的数据文件：缺少 history 字段')
        return
      }
      replaceHistory(data.history)
      if (data.weights) {
        localStorage.setItem('dnf_enhance_weights', JSON.stringify(data.weights))
      }
      emit('importComplete', data.history)
      alert(`导入成功！共 ${data.history.length} 条记录`)
    } catch {
      alert('文件格式错误，请选择正确的 JSON 导出文件')
    }
  }
  reader.readAsText(file)
  // 重置 input 以允许重复选择同一文件
  event.target.value = ''
}
</script>