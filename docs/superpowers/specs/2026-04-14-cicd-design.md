# CI/CD 设计方案

## 背景

DNF 增幅概率预测器项目（`github.com/justonescc/dnf-enhance-predictor`），前后端分离架构：

- 前端：Vue 3 + Vite + Tailwind CSS，已有 Vercel 部署配置
- 后端：FastAPI + Uvicorn，已有 Dockerfile 但未部署

当前无任何 CI/CD 配置。需求：免费、公网可访问、全自动化。

## 方案

**GitHub Actions（CI）+ Vercel 自动部署（CD）+ Vercel Serverless Function（后端）**

## 一、后端适配 Vercel Serverless

将 FastAPI 后端从 Docker 容器改为 Vercel Serverless Function：

- 在项目根目录创建 `api/index.py`，从 `backend/app/main.py` 导入 ASGI app
- 在 `api/` 下放 `requirements.txt`，Vercel 自动安装依赖
- 修改 `vercel.json`，配置 `functions` 指定 Python 运行时，配置 `rewrites` 将 `/api/*` 路由到 serverless function

架构变化：

```
# 之前
frontend/  → Vercel 静态站点
backend/   → Docker 容器（未部署）

# 之后
frontend/  → Vercel 静态站点
api/       → Vercel Serverless Function（导入 backend/app/main.py 的 FastAPI app）
```

免费版限制：10 秒超时、1024MB 内存、100GB/月带宽。对概率预测计算场景足够。

## 二、CI 流程（GitHub Actions）

触发条件：push 到 `main` 或任意 PR。

一个 workflow，两个并行 job：

### Job 1：后端测试

```
push/PR → Python 3.11 → pip install -r backend/requirements.txt → pytest backend/tests/
```

### Job 2：前端构建验证

```
push/PR → Node 20 → cd frontend && npm install → npm run build
```

不做的事：
- 不加 lint（项目当前无配置）
- 不加 e2e 测试（当前无测试用例）
- 不加部署步骤（Vercel 自动处理）

## 三、CD 流程（Vercel 自动部署）

Vercel 关联 GitHub 仓库，`main` 分支有新 commit 时自动部署。PR 自动生成 Preview URL。

## 四、文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `.github/workflows/ci.yml` | 新增 | GitHub Actions CI 配置 |
| `api/index.py` | 新增 | Serverless Function 入口 |
| `api/requirements.txt` | 新增 | 后端依赖（与 backend/requirements.txt 一致） |
| `vercel.json` | 修改 | 增加 functions 和 rewrites 配置 |

`backend/` 目录保持不变，继续作为源码和测试目录。`backend/Dockerfile` 保留不影响 Vercel 部署。

## 五、vercel.json 配置要点

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm install",
  "functions": {
    "api/index.py": {
      "runtime": "python-3.11"
    }
  },
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

## 六、api/index.py 要点

```python
from backend.app.main import app
# Vercel Python runtime 自动识别此 ASGI 应用
```
