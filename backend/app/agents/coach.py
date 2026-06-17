from __future__ import annotations

from app.agents.prompts import COACH_PROMPT
from app.core.llm import LLMClient, LLMUnavailable
from app.schemas.contracts import CoachInput, CoachOutput


class StudyCoachAgent:
    confidence = 0.94

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def handle(self, payload: dict) -> dict:
        data = CoachInput.model_validate(payload)
        try:
            output = self.llm.complete_json(
                system_prompt=COACH_PROMPT,
                payload=data.model_dump(),
                output_model=CoachOutput,
                temperature=0.55,
            )
        except LLMUnavailable:
            output = self._fallback(data)
        return output.model_dump()

    def _fallback(self, data: CoachInput) -> CoachOutput:
        if data.task_completed >= 0.8 and data.study_time >= 90:
            return CoachOutput(
                status="good",
                feedback="今天这节课完成得挺扎实，节奏是稳的。",
                suggestion="保持这个颗粒度，下一轮直接接着往下推。",
            )
        if data.task_completed >= 0.5 or data.study_time >= 45:
            return CoachOutput(
                status="warning",
                feedback="今天有推进，但还差一点点就能更稳。",
                suggestion="把剩下的部分拆成 20 分钟以内的小块。",
            )
        return CoachOutput(
            status="bad",
            feedback="今天启动有点慢，学习节奏还没完全拉起来。",
            suggestion="先做一个 10 分钟任务，找回进入状态的手感。",
        )
