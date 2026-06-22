from __future__ import annotations

from typing import Any

from app.graph.state import AgentId


PLANNER_KEYWORDS = ["计划", "规划", "我该学什么", "制定", "备考", "目标", "复习安排", "学习路线"]
COMPANION_KEYWORDS = ["学不动", "焦虑", "难受", "压力", "紧张", "累", "崩溃", "沮丧", "害怕", "想放弃"]
COACH_KEYWORDS = ["多久", "完成", "打卡", "学了", "复盘", "今日表现", "学习时长"]
RADAR_KEYWORDS = ["连续没学习", "风险", "趋势", "下降", "拖延", "中断", "预警"]
GROWTH_KEYWORDS = ["成长", "等级", "经验", "奖励", "徽章", "升级"]


def normalize_text(text: str | None) -> str:
    return (text or "").strip()


def normalize_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict(payload or {})


def determine_agent(
    *,
    text: str,
    payload: dict[str, Any],
    requested_agent: AgentId | None = None,
) -> AgentId:
    if requested_agent:
        return requested_agent

    planner_fields = {"exam_type", "target_score", "days_left"}
    if planner_fields <= payload.keys():
        return "planner"
    if _contains(text, PLANNER_KEYWORDS):
        return "planner"
    if _contains(text, COMPANION_KEYWORDS):
        return "companion"
    if _contains(text, COACH_KEYWORDS):
        return "coach"
    if _contains(text, RADAR_KEYWORDS):
        return "radar"
    if _contains(text, GROWTH_KEYWORDS):
        return "growth"
    return "companion"


def prepare_payload(agent: AgentId, text: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    if agent == "planner" and text:
        data.setdefault("goal", text)
    if agent == "companion":
        data.setdefault("message", text)
    if agent == "coach":
        data.setdefault("study_time", 0)
        data.setdefault("task_completed", 0.0)
    if agent == "radar":
        data.setdefault("study_days", 0)
        data.setdefault("avg_time", 0)
        data.setdefault("negative_words", 0)
    if agent == "growth":
        data.setdefault("study_time", 0)
        data.setdefault("completed", False)
    return data


def _contains(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)
