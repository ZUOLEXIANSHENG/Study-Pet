# 学习探索舱实现说明

## 目标

本次迁移参考 OpenMAIC 的“深度交互模式”，但没有直接搬运其课堂生成系统，而是将能力改造成 StudyPet 的陪伴式互动学习板块。

核心原则：

- 不生成任意 HTML/iframe，先返回稳定 JSON。
- 前端用 Vue 组件渲染互动内容。
- 互动活动可以被记录到数据库事件表。
- 保持 StudyPet 的 Agent 边界，不让单个 Agent 混合计划、情绪、评价和成长。

## 已实现页面

新增导航页：

```text
学习探索舱
```

包含四种互动类型：

```text
知识地图
今日闯关
互动小实验
AI 陪练室
```

页面位置：

```text
frontend/src/App.vue
```

相关状态和动作：

```text
frontend/src/stores/useStudyStore.ts
```

样式：

```text
frontend/src/styles.css
```

## 已实现接口

### 生成互动活动

```http
POST /api/interactive/generate
```

请求示例：

```json
{
  "user_id": "demo",
  "type": "mindmap",
  "topic": "考研数学",
  "source_text": "",
  "plan_items": [
    { "day": 1, "task": "极限基础" }
  ]
}
```

返回示例：

```json
{
  "id": "...",
  "type": "mindmap",
  "title": "考研数学知识地图",
  "objective": "把学习目标拆成可点击、可推进的知识结构。",
  "nodes": [],
  "steps": [],
  "checkpoints": [],
  "completion_rule": "完成至少一个分支选择并加入今日任务。",
  "pet_action": "guide",
  "widgets": [],
  "status": "ready"
}
```

### 完成互动活动

```http
POST /api/interactive/complete
```

请求示例：

```json
{
  "user_id": "demo",
  "activity_id": "activity-1",
  "type": "challenge",
  "completed_steps": ["stage-1", "stage-2"]
}
```

返回示例：

```json
{
  "activity_id": "activity-1",
  "type": "challenge",
  "completed": true,
  "exp": 18,
  "pet_action": "celebrate",
  "message": "已记录这次探索。StudyPet 会把它计入你的成长轨迹。"
}
```

## 后端文件

新增：

```text
backend/app/interactive.py
backend/tests/test_interactive.py
```

修改：

```text
backend/app/api.py
backend/app/schemas/api.py
```

事件持久化：

```text
interactive.generate
interactive.complete
```

可通过已有接口查看：

```http
GET /api/events?user_id=demo&limit=20
```

## 使用方式

1. 进入前端首页。
2. 点击顶部导航“学习探索舱”。
3. 选择一种互动类型。
4. 输入探索主题，或先在“学习规划”中生成计划。
5. 点击“生成互动活动”。
6. 勾选完成步骤。
7. 点击“记录这次探索”。
8. 到“成长中心”点击“查看保存记录”，可看到相关事件。

## 验证结果

已执行：

```bash
cd backend
python -m pytest -q
```

结果：

```text
24 passed
```

已执行：

```bash
cd frontend
npm run build
```

结果：

```text
build passed
```

浏览器自动化检查未完成，原因是当前 Python 环境缺少 `playwright` 包；Vite 本地服务可正常启动。

## 后续可扩展

下一步可以继续迁移 OpenMAIC 的更强能力：

- 使用 `diagram-content` 思想增强知识地图。
- 使用 `game-content` 思想生成更丰富的闯关卡。
- 使用 `simulation-content` 为数学/物理加入真实交互组件。
- 后续再评估是否接入 iframe 沙箱或 Three.js 3D 可视化。
