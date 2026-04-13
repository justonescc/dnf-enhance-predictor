<template>
  <div class="card">
    <h2 class="text-lg font-bold text-dnf-gold mb-3">概率趋势图</h2>
    <div class="relative" style="height: 250px;">
      <canvas ref="chartCanvas"></canvas>
      <div v-if="!trendData || trendData.length === 0" class="absolute inset-0 flex items-center justify-center text-gray-500 text-sm">
        记录垫手结果后显示趋势
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  trendData: { type: Array, default: () => [] }
})

const chartCanvas = ref(null)
let chartInstance = null

function createChart() {
  if (!chartCanvas.value) return
  if (chartInstance) {
    chartInstance.destroy()
  }

  const labels = props.trendData.map(d => `第${d.step}手`)
  const data = props.trendData.map(d => Math.round(d.prob * 1000) / 10)

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: '预测概率 (%)',
        data,
        borderColor: '#ffd700',
        backgroundColor: 'rgba(255, 215, 0, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: '#ffd700',
        pointBorderColor: '#ffd700',
        pointRadius: 4,
        pointHoverRadius: 6,
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#16213e',
          titleColor: '#ffd700',
          bodyColor: '#e0e0e0',
          borderColor: '#0f3460',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => `预测概率: ${ctx.parsed.y.toFixed(1)}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#888', maxRotation: 0 }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: {
            color: '#888',
            callback: (v) => v + '%'
          }
        }
      }
    }
  })
}

watch(() => props.trendData, () => {
  if (props.trendData && props.trendData.length > 0) {
    createChart()
  } else if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}, { deep: true })

onMounted(() => {
  if (props.trendData && props.trendData.length > 0) {
    createChart()
  }
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})
</script>