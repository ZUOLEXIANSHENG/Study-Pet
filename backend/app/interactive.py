from __future__ import annotations

from datetime import datetime
from uuid import uuid4


ActivityType = str


def generate_activity(payload: dict) -> dict:
    activity_type = payload.get("type") or "mindmap"
    topic = _clean(payload.get("topic")) or _clean(payload.get("goal")) or "待设置主题"
    source_text = _clean(payload.get("source_text"))
    plan_items = payload.get("plan_items") if isinstance(payload.get("plan_items"), list) else []

    if activity_type == "challenge":
        return _challenge_activity(topic, plan_items)
    if activity_type == "simulation":
        return _simulation_activity(topic)
    if activity_type == "coach_practice":
        return _coach_practice_activity(topic)
    return _mindmap_activity(topic, source_text, plan_items)


def complete_activity(payload: dict) -> dict:
    activity_id = _clean(payload.get("activity_id")) or str(uuid4())
    activity_type = _clean(payload.get("type")) or "mindmap"
    completed_steps = payload.get("completed_steps") if isinstance(payload.get("completed_steps"), list) else []
    exp = 10 + min(len(completed_steps), 5) * 4
    return {
        "activity_id": activity_id,
        "type": activity_type,
        "completed": True,
        "exp": exp,
        "pet_action": "celebrate",
        "message": "已记录这次探索。StudyPet 会把它计入你的成长轨迹。",
        "completed_at": datetime.utcnow().isoformat(),
    }


def _mindmap_activity(topic: str, source_text: str, plan_items: list) -> dict:
    branches = _extract_branches(topic, source_text, plan_items)
    nodes = [
        {
            "id": "root",
            "label": topic,
            "level": 0,
            "status": "待探索",
            "children": [branch["id"] for branch in branches],
        },
        *branches,
    ]
    return _activity(
        activity_type="mindmap",
        title=f"{topic}知识地图",
        objective="把学习目标拆成可点击、可推进的知识结构。",
        nodes=nodes,
        steps=[
            {"id": "scan", "title": "浏览知识地图", "description": "先看清主题和分支，不急着开始全部内容。"},
            {"id": "choose", "title": "选择一个分支", "description": "挑一个今天最想推进的节点。"},
            {"id": "commit", "title": "加入今日任务", "description": "把选中的节点变成一个 20-40 分钟的小任务。"},
        ],
        checkpoints=["已确认核心主题", "已选择今日分支", "已形成一个可执行任务"],
        completion_rule="完成至少一个分支选择并加入今日任务。",
        pet_action="guide",
    )


def _challenge_activity(topic: str, plan_items: list) -> dict:
    tasks = _tasks_from_plan(topic, plan_items)
    return _activity(
        activity_type="challenge",
        title=f"{topic}今日闯关",
        objective="把今天的学习拆成 3 个轻量关卡，完成后获得成长奖励。",
        nodes=[],
        steps=[
            {"id": f"stage-{index}", "title": task, "description": "完成后勾选这一关。"}
            for index, task in enumerate(tasks, start=1)
        ],
        checkpoints=["完成第一关", "完成第二关", "完成第三关"],
        completion_rule="至少完成 2 个关卡即可记录一次探索。",
        pet_action="encourage",
    )


def _simulation_activity(topic: str) -> dict:
    return _activity(
        activity_type="simulation",
        title=f"{topic}互动小实验",
        objective="用可调参数的方式观察概念变化，先建立直觉。",
        nodes=[],
        steps=[
            {"id": "variable", "title": "选择一个变量", "description": "例如时间、速度、难度、题量或复习频率。"},
            {"id": "observe", "title": "调整参数并观察", "description": "移动滑块，看结果如何变化。"},
            {"id": "summary", "title": "写下一句发现", "description": "用一句话总结你看到的规律。"},
        ],
        checkpoints=["已选择变量", "已完成一次调整", "已写下观察结论"],
        completion_rule="完成一次参数调整并留下观察结论。",
        pet_action="focus",
        widgets=[
            {"id": "intensity", "label": "练习强度", "min": 1, "max": 5, "value": 3},
            {"id": "duration", "label": "学习时长", "min": 10, "max": 90, "value": 30},
        ],
    )


def _coach_practice_activity(topic: str) -> dict:
    return _activity(
        activity_type="coach_practice",
        title=f"{topic}AI陪练室",
        objective="让 StudyPet 以提问方式陪你完成一次短练习。",
        nodes=[],
        steps=[
            {"id": "warmup", "title": "说出今天最卡的一点", "description": "不用完整，写一个关键词也可以。"},
            {"id": "answer", "title": "完成一个小问题", "description": "StudyPet 会根据你的主题给出下一步引导。"},
            {"id": "reflect", "title": "复盘一句话", "description": "写下这次练习最有用的一点。"},
        ],
        checkpoints=["已表达卡点", "已完成小问题", "已完成复盘"],
        completion_rule="完成一次表达、一次作答和一次复盘。",
        pet_action="comfort",
    )


def _activity(
    *,
    activity_type: ActivityType,
    title: str,
    objective: str,
    nodes: list,
    steps: list,
    checkpoints: list[str],
    completion_rule: str,
    pet_action: str,
    widgets: list | None = None,
) -> dict:
    return {
        "id": str(uuid4()),
        "type": activity_type,
        "title": title,
        "objective": objective,
        "source": "plan_or_user_input",
        "nodes": nodes,
        "steps": steps,
        "checkpoints": checkpoints,
        "completion_rule": completion_rule,
        "pet_action": pet_action,
        "widgets": widgets or [],
        "status": "ready",
        "created_at": datetime.utcnow().isoformat(),
    }


def _extract_branches(topic: str, source_text: str, plan_items: list) -> list[dict]:
    labels: list[str] = []
    for item in plan_items[:6]:
        if isinstance(item, dict):
            task = _clean(item.get("task")) or _clean(item.get("goal"))
            if task:
                labels.append(task[:18])
    if not labels and source_text:
        labels = [part[:18] for part in source_text.replace("\n", " ").split("。") if part.strip()][:5]
    if not labels:
        labels = ["核心概念", "基础练习", "薄弱点整理", "阶段自测"]

    return [
        {
            "id": f"node-{index}",
            "label": label,
            "level": 1,
            "status": "待探索",
            "children": [],
        }
        for index, label in enumerate(labels, start=1)
    ]


def _tasks_from_plan(topic: str, plan_items: list) -> list[str]:
    tasks: list[str] = []
    for item in plan_items[:3]:
        if isinstance(item, dict):
            task = _clean(item.get("task"))
            if task:
                tasks.append(task)
    while len(tasks) < 3:
        fallback = ["整理一个知识点", "完成一组小练习", "写下今日复盘"][len(tasks)]
        tasks.append(f"{topic}：{fallback}")
    return tasks[:3]


def _clean(value: object) -> str:
    return str(value or "").strip()
