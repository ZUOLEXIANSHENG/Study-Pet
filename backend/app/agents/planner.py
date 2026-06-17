from __future__ import annotations

from app.agents.prompts import PLANNER_PROMPT
from app.core.llm import LLMClient, LLMUnavailable
from app.schemas.contracts import DailyPlanItem, PlannerInput, PlannerOutput, WeeklyPlanItem


class StudyPlannerAgent:
    confidence = 0.96

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def handle(self, payload: dict) -> dict:
        data = PlannerInput.model_validate(payload)
        try:
            output = self.llm.complete_json(
                system_prompt=PLANNER_PROMPT,
                payload=data.model_dump(),
                output_model=PlannerOutput,
                temperature=0.25,
            )
        except LLMUnavailable:
            output = self._fallback(data)
        return output.model_dump()

    def _fallback(self, data: PlannerInput) -> PlannerOutput:
        difficulty = "high" if data.days_left <= 14 else "medium" if data.days_left <= 45 else "low"
        topics = self._topics_for(data.exam_type)
        plan = [
            DailyPlanItem(day=index, task=f"{data.exam_type}：{topic}")
            for index, topic in enumerate(topics, start=1)
        ]
        weekly_plan = [
            WeeklyPlanItem(week=1, goal="建立知识框架，完成基础任务启动"),
            WeeklyPlanItem(week=2, goal="集中训练薄弱模块，开始限时练习"),
            WeeklyPlanItem(week=3, goal="进入综合练习与错题复盘"),
            WeeklyPlanItem(week=4, goal="模拟检验，压缩失分点"),
        ]
        warning = f"当前水平为{data.current_level}，建议先稳住基础，再逐步提高训练强度。"
        return PlannerOutput(plan=plan, weekly_plan=weekly_plan, difficulty=difficulty, warning=warning)

    def _topics_for(self, exam_type: str) -> list[str]:
        if any(keyword in exam_type for keyword in ["高考", "考研", "数学"]):
            return ["梳理核心公式与概念", "完成基础题型训练", "复盘错题并标记薄弱点", "进行限时小测"]
        if any(keyword in exam_type for keyword in ["四六级", "英语"]):
            return ["背诵高频词汇", "完成阅读专项训练", "练习听力精听", "整理作文模板"]
        return ["建立知识框架", "训练重点题型", "完成阶段自测", "复盘薄弱模块"]
