from __future__ import annotations

from app.agents.prompts import GROWTH_PROMPT
from app.core.llm import LLMClient, LLMUnavailable
from app.schemas.contracts import GrowthInput, GrowthOutput


class GrowthAgent:
    confidence = 0.93

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()
        self.level = 1
        self.exp = 0
        self.mood = 60
        self.focus = 60

    def handle(self, payload: dict) -> dict:
        data = GrowthInput.model_validate(payload)
        try:
            output = self.llm.complete_json(
                system_prompt=GROWTH_PROMPT,
                payload=data.model_dump() | {"current_level": self.level, "current_exp": self.exp},
                output_model=GrowthOutput,
                temperature=0.5,
            )
            self._sync_state(output)
        except LLMUnavailable:
            output = self._fallback(data)
        return output.model_dump()

    def _fallback(self, data: GrowthInput) -> GrowthOutput:
        gained = max(5, data.study_time // 6)
        if data.completed:
            gained += 10
            self.focus = min(100, self.focus + 5)
            self.mood = min(100, self.mood + 3)
        else:
            self.focus = max(0, self.focus - 2)
            self.mood = max(0, self.mood - 1)

        self.exp += gained
        level_up = False
        if self.exp >= self.level * 100:
            self.level += 1
            level_up = True

        summary = "连续学习让角色状态更稳定。" if data.completed else "本次学习有记录，但还可以提高完成度。"
        return GrowthOutput(
            exp=gained,
            level_up=level_up,
            growth_summary=summary,
            level=self.level,
            mood=self.mood,
            focus=self.focus,
        )

    def _sync_state(self, output: GrowthOutput) -> None:
        if output.level is not None:
            self.level = max(1, output.level)
        if output.mood is not None:
            self.mood = min(100, max(0, output.mood))
        if output.focus is not None:
            self.focus = min(100, max(0, output.focus))
        self.exp += max(0, output.exp)
