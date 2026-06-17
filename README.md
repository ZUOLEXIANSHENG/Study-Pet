# StudyMate AI

学习搭子（StudyMate AI）是一个模块化 AI 伴学系统，强调单 Agent、结构化 JSON 输出和 Orchestrator 路由。

## 目录

- `studymate-ai/backend`: FastAPI 后端，包含 5 个 Agent 和 Orchestrator
- `studymate-ai/frontend`: Vue 3 + TypeScript + Vite 工作台

## 后端启动

```bash
cd studymate-ai/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## 前端启动

```bash
cd studymate-ai/frontend
npm install
npm run dev
```

## 设计原则

- 单请求只进一个 Agent
- 所有输出必须是 JSON
- 不混合计划、情绪、成长等模块逻辑
- 所有模块通过 Orchestrator 调度
