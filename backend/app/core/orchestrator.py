from __future__ import annotations

from app.agents.coach import StudyCoachAgent
from app.agents.companion import CompanionAgent
from app.agents.growth import GrowthAgent
from app.agents.planner import StudyPlannerAgent
from app.agents.radar import AnxietyRadarAgent
from app.schemas.contracts import OrchestratorEnvelope


class Orchestrator:
    def __init__(self) -> None:
        self.planner = StudyPlannerAgent()
        self.coach = StudyCoachAgent()
        self.companion = CompanionAgent()
        self.growth = GrowthAgent()
        self.radar = AnxietyRadarAgent()

    def route(self, agent_name: str, payload: dict) -> dict:
        handler = self._resolve(agent_name)
        result = handler.handle(payload)
        envelope = OrchestratorEnvelope(agent=agent_name, result=result, confidence=handler.confidence)
        return envelope.model_dump()

    def route_from_text(self, text: str, payload: dict) -> dict:
        planner_fields = {"exam_type", "target_score", "days_left"}
        if self._contains(text, ["计划", "我该学什么", "制定", "备考", "目标"]) and planner_fields <= payload.keys():
            return self.route("planner", payload | {"goal": text})
        if self._contains(text, ["学不动", "焦虑", "难受", "压力", "紧张", "累", "崩溃"]):
            return self.route("companion", payload | {"message": text})
        if self._contains(text, ["多久", "完成", "打卡", "学了", "复盘"]):
            return self.route(
                "coach",
                payload | {"study_time": payload.get("study_time", 0), "task_completed": payload.get("task_completed", 0.0)},
            )
        if self._contains(text, ["连续没学", "风险", "趋势", "下降", "拖延"]):
            return self.route(
                "radar",
                payload
                | {
                    "study_days": payload.get("study_days", 0),
                    "avg_time": payload.get("avg_time", 0),
                    "negative_words": payload.get("negative_words", 0),
                },
            )
        if self._contains(text, ["成长", "等级", "经验", "奖励"]):
            return self.route(
                "growth",
                payload | {"study_time": payload.get("study_time", 0), "completed": payload.get("completed", False)},
            )
        return self.route("companion", payload | {"message": text})

    def _resolve(self, agent_name: str):
        mapping = {
            "planner": self.planner,
            "coach": self.coach,
            "companion": self.companion,
            "growth": self.growth,
            "radar": self.radar,
        }
        if agent_name not in mapping:
            raise ValueError(f"Unknown agent: {agent_name}")
        return mapping[agent_name]

    def _contains(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)
