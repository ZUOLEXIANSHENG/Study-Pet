from __future__ import annotations

from app.agents.prompts import RADAR_PROMPT
from app.core.llm import LLMClient, LLMUnavailable
from app.schemas.contracts import RadarInput, RadarOutput


class AnxietyRadarAgent:
    confidence = 0.91

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def handle(self, payload: dict) -> dict:
        data = RadarInput.model_validate(payload)
        try:
            output = self.llm.complete_json(
                system_prompt=RADAR_PROMPT,
                payload=data.model_dump(),
                output_model=RadarOutput,
                temperature=0.25,
            )
        except LLMUnavailable:
            output = self._fallback(data)
        return output.model_dump()

    def _fallback(self, data: RadarInput) -> RadarOutput:
        score = 0
        if data.study_days <= 2:
            score += 2
        if data.avg_time < 45:
            score += 2
        if data.negative_words >= 2:
            score += 2

        if score >= 5:
            return RadarOutput(
                risk_level="high",
                signal="学习频率、平均时长和负面表达同时偏弱。",
                action="立即缩短任务，只保留一个 10 分钟启动任务。",
            )
        if score >= 3:
            return RadarOutput(
                risk_level="medium",
                signal="学习节奏存在持续下滑迹象。",
                action="降低今日任务量，并安排一次轻量复盘。",
            )
        return RadarOutput(
            risk_level="low",
            signal="当前学习风险较低。",
            action="保持当前节奏，继续记录学习状态。",
        )
