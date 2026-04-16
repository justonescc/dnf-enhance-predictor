# DNF 增幅概率预测器

纯前端单页应用，用于预测 DNF 手游增幅/徽章合成的成功率并给出操作建议。

## 技术栈

- **框架**: Vue 3 + Vite
- **样式**: Tailwind CSS
- **图表**: Chart.js
- **部署**: GitHub Pages (`.github/workflows/deploy.yml`)

## 项目结构

```
frontend/
├── src/
│   ├── App.vue                 # 主组件，状态管理 + 自动预测
│   ├── main.js                 # 入口
│   ├── style.css               # 全局样式（含 Tailwind 指令）
│   ├── components/
│   │   ├── EnhanceSetting.vue  # 增幅等级 + 徽章等级选择
│   │   ├── PadRecord.vue       # 垫手记录输入（成功/失败序列）
│   │   ├── ProbGauge.vue       # 概率仪表盘 + 建议
│   │   ├── FeedbackButtons.vue # 反馈按钮（成功/失败）
│   │   ├── ModelDetail.vue     # 三模型详情 + 学习阶段
│   │   ├── TrendChart.vue      # 概率趋势图（Chart.js）
│   │   ├── HistoryPanel.vue    # 历史记录面板
│   │   └── DataIO.vue          # 数据导入/导出
│   └── services/
│       ├── predictor.js        # 纯 JS 预测引擎（核心）
│       ├── api.js              # 前端 API 层（调用 predictor.js）
│       └── storage.js          # localStorage 持久化
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## 预测模型

核心引擎在 `frontend/src/services/predictor.js`，包含四个模型：

1. **马尔可夫链** (2阶) — 基于成功/失败序列的转移概率
2. **贝叶斯更新** — 以基础概率为 Beta 先验，用历史数据更新
3. **HMM** — 3状态隐马尔可夫模型，纯 JS 实现 Baum-Welch + Viterbi
4. **集成预测** — 加权融合三模型，数据<8次时 HMM 降级，50+条记录时引入经验模式

## 开发命令

```bash
cd frontend
npm install
npm run dev      # 开发服务器
npm run build    # 构建
npm run preview  # 预览构建产物
```

## 部署

推送到 `main` 分支后，GitHub Actions 自动构建并部署到 GitHub Pages。
Vite base path 配置为 `/dnf-enhance-predictor/`。

## 数据存储

所有数据存储在浏览器 localStorage 中：
- `dnf_enhance_history` — 历史记录（最多 200 条）
- `dnf_enhance_weights` — 模型权重
