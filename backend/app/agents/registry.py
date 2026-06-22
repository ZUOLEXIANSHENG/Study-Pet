from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.agents.coach import StudyCoachAgent
from app.agents.companion import CompanionAgent
from app.agents.growth import GrowthAgent
from app.agents.planner import StudyPlannerAgent
from app.agents.radar import AnxietyRadarAgent
from app.core.llm import LLMClient
from app.core.settings import Settings, get_settings
from app.graph.state import AgentId
from app.schemas.contracts import CoachOutput, CompanionOutput, GrowthOutput, PlannerOutput, RadarOutput


@dataclass(frozen=True)
class AgentConfig:
    id: AgentId
    name: str
    role: str
    persona: str
    allowed_actions: tuple[str, ...]
    output_schema: type[BaseModel]
    confidence: float
    priority: int
    llm_provider: str | None = None


def build_agent_configs(settings: Settings | None = None) -> dict[AgentId, AgentConfig]:
    settings = settings or get_settings()
    return {
        "planner": AgentConfig(
            id="planner",
            name="StudyPlannerAgent",
            role="learning_plan_generation",
            persona="只负责学习计划、目标拆解和时间安排。",
            allowed_actions=("generate_daily_plan", "generate_weekly_plan", "set_stage_goals"),
            output_schema=PlannerOutput,
            confidence=0.96,
            priority=10,
            llm_provider=settings.planner_llm_provider,
        ),
        "coach": AgentConfig(
            id="coach",
            name="StudyCoachAgent",
            role="study_behavior_feedback",
            persona="只负责学习行为评估、完成度判断和学习复盘。",
            allowed_actions=("evaluate_session", "summarize_completion", "suggest_behavior_adjustment"),
            output_schema=CoachOutput,
            confidence=0.94,
            priority=20,
            llm_provider=settings.coach_llm_provider,
        ),
        "companion": AgentConfig(
            id="companion",
            name="CompanionAgent",
            role="emotional_companionship",
            persona="只负责情绪共情、鼓励和陪伴对话。",
            allowed_actions=("detect_emotion", "reply_with_empathy", "suggest_support_action"),
            output_schema=CompanionOutput,
            confidence=0.97,
            priority=30,
            llm_provider=settings.companion_llm_provider,
        ),
        "growth": AgentConfig(
            id="growth",
            name="GrowthAgent",
            role="growth_and_reward_system",
            persona="只负责经验值、等级成长和成长记录。",
            allowed_actions=("calculate_exp", "update_level", "summarize_growth"),
            output_schema=GrowthOutput,
            confidence=0.93,
            priority=40,
            llm_provider=settings.growth_llm_provider,
        ),
        "radar": AgentConfig(
            id="radar",
            name="AnxietyRadarAgent",
            role="risk_detection",
            persona="只负责学习状态风险识别和焦虑趋势判断。",
            allowed_actions=("detect_risk", "summarize_signal", "suggest_risk_action"),
            output_schema=RadarOutput,
            confidence=0.91,
            priority=50,
            llm_provider=settings.radar_llm_provider,
        ),
    }


AGENT_IDS: set[AgentId] = {"planner", "coach", "companion", "growth", "radar"}


class AgentRegistry:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.configs = build_agent_configs(self.settings)
        self.handlers: dict[AgentId, Any] = {
            "planner": StudyPlannerAgent(llm=self._llm_for("planner")),
            "coach": StudyCoachAgent(llm=self._llm_for("coach")),
            "companion": CompanionAgent(llm=self._llm_for("companion")),
            "growth": GrowthAgent(llm=self._llm_for("growth")),
            "radar": AnxietyRadarAgent(llm=self._llm_for("radar")),
        }

    def get_config(self, agent_id: AgentId) -> AgentConfig:
        return self.configs[agent_id]

    def get_handler(self, agent_id: AgentId) -> Any:
        return self.handlers[agent_id]

    def allowed_agent_ids(self) -> set[AgentId]:
        return AGENT_IDS

    def _llm_for(self, agent_id: AgentId) -> LLMClient:
        return LLMClient(provider_id=self.configs[agent_id].llm_provider)
