# DNF增幅概率预测器 - 前端实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建完整的 Vue 3 前端应用，包含垫手记录、概率预测展示、趋势图表、历史记录、数据导入导出等全部前端功能。

**Architecture:** Vue 3 Composition API 单页应用，Vite 构建，Tailwind CSS 暗色主题，Chart.js 折线图。通过 Axios 调用后端 API，后端不可用时使用前端本地模拟算法降级运行。所有持久化数据存储在浏览器 localStorage。

**Tech Stack:** Vue 3.4+ / Vite 5 / Tailwind CSS 3 / Chart.js 4 / Axios

---

## 文件结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── EnhanceSetting.vue      # 增幅等级 + 徽章等级选择
│   │   ├── PadRecord.vue           # 垫手记录区：成功/失败按钮 + 序列展示
│   │   ├── ProbGauge.vue           # 概率仪表盘：弧形进度 + 数字 + 建议文字
│   │   ├── FeedbackButtons.vue     # 增幅结果反馈按钮
│   │   ├── ModelDetail.vue         # 三个模型详情 + 准确率 + 学习阶段
│   │   ├── TrendChart.vue          # Chart.js 概率趋势折线图
│   │   ├── HistoryPanel.vue        # 历史记录面板（弹窗）
│   │   └── DataIO.vue              # 导入/导出 JSON 数据
│   ├── services/
│   │   ├── api.js                  # Axios 封装，调用后端 API
│   │   └── storage.js              # localStorage 读写管理
│   ├── App.vue                     # 主布局：组装所有组件
│   ├── main.js                     # 入口：挂载 Vue 实例
│   └── style.css                   # Tailwind 指令 + 全局样式
├── index.html                      # HTML 入口
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── vercel.json
```

---

### Task 1: 项目脚手架搭建

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/style.css`
- Create: `frontend/src/App.vue`
- Create: `frontend/vercel.json`

- [ ] **Step 1: 初始化 Vite + Vue 3 项目**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npm create vite@latest . -- --template vue
```

如果提示目录非空，选择覆盖。完成后项目根目录会有 `package.json`, `vite.config.js`, `index.html` 等。

- [ ] **Step 2: 安装依赖**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npm install
npm install -D tailwindcss@3 postcss autoprefixer
npm install chart.js axios
```

- [ ] **Step 3: 初始化 Tailwind CSS**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npx tailwindcss init -p
```

这会生成 `tailwind.config.js` 和 `postcss.config.js`。

- [ ] **Step 4: 配置 tailwind.config.js**

替换 `tailwind.config.js` 的全部内容：

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'dnf-dark': '#1a1a2e',
        'dnf-darker': '#16213e',
        'dnf-card': '#0f3460',
        'dnf-gold': '#ffd700',
        'dnf-gold-dark': '#b8960f',
        'dnf-red': '#ff4444',
        'dnf-green': '#44ff44',
        'dnf-yellow': '#ffdd44',
        'dnf-orange': '#ff8844',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 5: 配置全局样式**

替换 `src/style.css` 的全部内容：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #1a1a2e;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  min-height: 100vh;
}

/* 金色发光按钮效果 */
.btn-gold {
  @apply bg-dnf-gold text-dnf-dark font-bold py-2 px-4 rounded-lg;
  box-shadow: 0 0 15px rgba(255, 215, 0, 0.4);
  transition: all 0.3s ease;
}
.btn-gold:hover {
  box-shadow: 0 0 25px rgba(255, 215, 0, 0.6);
  transform: translateY(-1px);
}
.btn-gold:active {
  transform: translateY(0);
}

/* 红色按钮 */
.btn-red {
  @apply bg-dnf-red text-white font-bold py-2 px-4 rounded-lg;
  box-shadow: 0 0 10px rgba(255, 68, 68, 0.3);
  transition: all 0.3s ease;
}
.btn-red:hover {
  box-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
}

/* 卡片容器 */
.card {
  @apply bg-dnf-darker rounded-xl p-4 border border-dnf-card;
}

/* 最小触屏点击区域 48px */
.touch-target {
  @apply min-w-[48px] min-h-[48px] flex items-center justify-center;
}
```

- [ ] **Step 6: 配置 index.html**

替换 `index.html` 的全部内容：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DNF增幅概率预测器</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

- [ ] **Step 7: 编写 main.js**

替换 `src/main.js` 的全部内容：

```js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')
```

- [ ] **Step 8: 编写 App.vue 骨架**

替换 `src/App.vue` 的全部内容：

```vue
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
```

- [ ] **Step 9: 创建 vercel.json**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vue"
}
```

- [ ] **Step 10: 清理 Vite 脚手架默认文件**

删除 Vite 默认生成的示例文件（如果有）：
```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
rm -f src/components/HelloWorld.vue src/assets/vue.svg public/vite.svg
```

- [ ] **Step 11: 验证开发服务器启动**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npm run dev
```

打开浏览器访问 `http://localhost:5173`，确认页面加载无报错（组件会暂时报错，因为还没创建，这是正常的）。

Ctrl+C 停止开发服务器。

- [ ] **Step 12: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/
git commit -m "feat: 初始化 Vue 3 + Vite + Tailwind CSS 前端项目脚手架"
```

---

### Task 2: 本地存储服务 (storage.js)

**Files:**
- Create: `frontend/src/services/storage.js`

- [ ] **Step 1: 编写 storage.js**

```js
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/services/storage.js
git commit -m "feat: 添加 localStorage 存储服务，管理历史记录和模型权重"
```

---

### Task 3: API 调用服务 (api.js)

**Files:**
- Create: `frontend/src/services/api.js`

- [ ] **Step 1: 编写 api.js**

```js
import axios from 'axios'

// 后端 API 基础地址，部署后替换为实际 Render 地址
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/services/api.js
git commit -m "feat: 添加 API 调用服务，含后端不可用时的前端降级预测"
```

---

### Task 4: 增幅设置组件 (EnhanceSetting.vue)

**Files:**
- Create: `frontend/src/components/EnhanceSetting.vue`

- [ ] **Step 1: 编写 EnhanceSetting.vue**

```vue
<template>
  <div class="card">
    <h2 class="text-lg font-bold text-dnf-gold mb-3">增幅设置</h2>

    <div class="space-y-3">
      <!-- 目标增幅等级 -->
      <div>
        <label class="block text-sm text-gray-400 mb-1">目标增幅等级</label>
        <select
          :value="enhanceLevel"
          @change="$emit('update:enhanceLevel', $event.target.value)"
          class="w-full bg-dnf-dark border border-dnf-card rounded-lg px-3 py-2 text-white focus:border-dnf-gold focus:outline-none touch-target"
        >
          <option v-for="level in enhanceLevels" :key="level" :value="level">
            {{ level }} (成功率 {{ (rates[level] * 100).toFixed(0) }}%)
          </option>
        </select>
      </div>

      <!-- 徽章等级 -->
      <div>
        <label class="block text-sm text-gray-400 mb-1">垫手徽章等级</label>
        <select
          :value="badgeLevel"
          @change="$emit('update:badgeLevel', Number($event.target.value))"
          class="w-full bg-dnf-dark border border-dnf-card rounded-lg px-3 py-2 text-white focus:border-dnf-gold focus:outline-none touch-target"
        >
          <option v-for="lv in badgeLevels" :key="lv" :value="lv">
            {{ lv }}级 (合成成功率 {{ (badgeRates[lv] * 100).toFixed(0) }}%)
          </option>
        </select>
      </div>

      <!-- 基础成功率显示 -->
      <div class="flex items-center justify-between text-sm">
        <span class="text-gray-400">垫手基础成功率</span>
        <span class="text-dnf-gold font-bold">{{ (badgeRates[badgeLevel] * 100).toFixed(0) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ENHANCE_RATES, BADGE_RATES } from '../services/api.js'

defineProps({
  enhanceLevel: { type: String, default: '+10' },
  badgeLevel: { type: Number, default: 7 }
})

defineEmits(['update:enhanceLevel', 'update:badgeLevel'])

const rates = ENHANCE_RATES
const badgeRates = BADGE_RATES

const enhanceLevels = [
  '+4', '+5', '+6', '+7', '+8', '+9', '+10',
  '+11', '+12', '+13', '+14', '+15', '+16', '+17', '+18', '+19'
]

const badgeLevels = [5, 6, 7, 8, 9, 10]
</script>
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/EnhanceSetting.vue
git commit -m "feat: 添加增幅等级和徽章等级选择组件"
```

---

### Task 5: 垫手记录组件 (PadRecord.vue)

**Files:**
- Create: `frontend/src/components/PadRecord.vue`

- [ ] **Step 1: 编写 PadRecord.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/PadRecord.vue
git commit -m "feat: 添加垫手记录组件，支持成功/失败输入、撤销和清除"
```

---

### Task 6: 概率仪表盘组件 (ProbGauge.vue)

**Files:**
- Create: `frontend/src/components/ProbGauge.vue`

- [ ] **Step 1: 编写 ProbGauge.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/ProbGauge.vue
git commit -m "feat: 添加概率仪表盘组件，含弧形进度条、对比条和建议文字"
```

---

### Task 7: 反馈按钮组件 (FeedbackButtons.vue)

**Files:**
- Create: `frontend/src/components/FeedbackButtons.vue`

- [ ] **Step 1: 编写 FeedbackButtons.vue**

```vue
<template>
  <div class="flex gap-3">
    <button
      class="flex-1 btn-gold py-3 text-base touch-target"
      :disabled="!canFeedback"
      :class="{ 'opacity-40 cursor-not-allowed': !canFeedback }"
      @click="$emit('feedback', 'success')"
    >
      增幅成功
    </button>
    <button
      class="flex-1 btn-red py-3 text-base touch-target"
      :disabled="!canFeedback"
      :class="{ 'opacity-40 cursor-not-allowed': !canFeedback }"
      @click="$emit('feedback', 'failure')"
    >
      增幅失败
    </button>
  </div>
  <p v-if="!canFeedback" class="text-xs text-gray-500 mt-1 text-center">
    记录至少 10 次垫手结果后可反馈
  </p>
</template>

<script setup>
defineProps({
  canFeedback: { type: Boolean, default: false }
})

defineEmits(['feedback'])
</script>
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/FeedbackButtons.vue
git commit -m "feat: 添加增幅结果反馈按钮组件"
```

---

### Task 8: 模型详情组件 (ModelDetail.vue)

**Files:**
- Create: `frontend/src/components/ModelDetail.vue`

- [ ] **Step 1: 编写 ModelDetail.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/ModelDetail.vue
git commit -m "feat: 添加模型详情组件，展示三模型预测值、准确率和学习阶段"
```

---

### Task 9: 趋势图表组件 (TrendChart.vue)

**Files:**
- Create: `frontend/src/components/TrendChart.vue`

- [ ] **Step 1: 编写 TrendChart.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/TrendChart.vue
git commit -m "feat: 添加概率趋势折线图组件，使用 Chart.js"
```

---

### Task 10: 历史记录面板组件 (HistoryPanel.vue)

**Files:**
- Create: `frontend/src/components/HistoryPanel.vue`

- [ ] **Step 1: 编写 HistoryPanel.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/HistoryPanel.vue
git commit -m "feat: 添加历史记录弹窗面板组件"
```

---

### Task 11: 数据导入导出组件 (DataIO.vue)

**Files:**
- Create: `frontend/src/components/DataIO.vue`

- [ ] **Step 1: 编写 DataIO.vue**

```vue
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
```

- [ ] **Step 2: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/src/components/DataIO.vue
git commit -m "feat: 添加 JSON 数据导入导出组件"
```

---

### Task 12: 整合测试与修复

**Files:**
- Modify: `frontend/src/App.vue` (如有需要)

- [ ] **Step 1: 启动开发服务器并检查**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npm run dev
```

在浏览器中访问 `http://localhost:5173`，检查：
1. 页面正常渲染，暗色主题显示正确
2. 增幅等级和徽章等级下拉框可选择
3. 点击"成功/失败"按钮，垫手序列正常显示
4. 记录 2 次以上垫手后，仪表盘显示预测概率（前端降级模式）
5. 对比条、置信度条正常显示
6. 建议文字正确（颜色和文字内容）
7. 趋势图正常绘制
8. "历史"按钮打开历史面板
9. "导出"按钮下载 JSON 文件
10. 点击"增幅成功/失败"反馈后，记录清空，历史中出现新记录
11. 缩小浏览器窗口到 <768px，确认移动端纵向堆叠布局

Ctrl+C 停止开发服务器。

- [ ] **Step 2: 修复发现的问题**

根据 Step 1 的测试结果修复问题。

- [ ] **Step 3: 构建生产版本**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0/frontend"
npm run build
```

确认构建成功，无错误输出。

- [ ] **Step 4: 提交**

```bash
cd "/Users/shichangchun/Downloads/增幅1.0"
git add frontend/
git commit -m "feat: 完成前端全部组件整合，支持降级预测和响应式布局"
```

---

## 自审检查

### 1. 规格覆盖

| 规格需求 | 对应 Task |
|---------|----------|
| 增幅等级选择 (+4 到 +20) | Task 4 |
| 徽章等级选择 (5-10级) | Task 4 |
| 垫手记录 (10-20次成功/失败) | Task 5 |
| 概率预测展示 (仪表盘+数字+对比) | Task 6 |
| 操作建议 (颜色+文字) | Task 6 |
| 置信度展示 | Task 6 |
| 反馈按钮 (成功/失败) | Task 7 |
| 模型详情 (三模型+准确率+学习阶段) | Task 8 |
| 趋势图表 (Chart.js) | Task 9 |
| 历史记录面板 | Task 10 |
| 数据导入/导出 (JSON) | Task 11 |
| localStorage 持久化 | Task 2 |
| 后端不可用降级预测 | Task 3 |
| 暗色主题 + 金色强调 | Task 1 (CSS) |
| 响应式布局 (768px断点) | Task 1 (App.vue grid) |
| 触屏 48px 最小点击区域 | Task 1 (CSS) |
| 冷启动提示 (API超时) | Task 3 (30s timeout) |

### 2. 占位符扫描

无 TBD / TODO / "implement later" / "fill in details" / "add appropriate error handling" / "similar to Task N"。

### 3. 类型一致性

- `padResults` 在 App.vue 中为 `ref([])`，在 PadRecord.vue 中 props 为 `Array`，一致
- `prediction` reactive 对象的字段与 ProbGauge / ModelDetail props 匹配
- `historyRecords` 为 `Array`，与 HistoryPanel props `records` 匹配
- `accuracy` computed 返回结构体与 ModelDetail props `accuracy` 匹配
- `learningStage` computed 返回 `{ key, label, color }` 与 ModelDetail props 匹配
