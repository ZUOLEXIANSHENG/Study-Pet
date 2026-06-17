from __future__ import annotations

from app.agents.prompts import COMPANION_PROMPT
from app.core.llm import LLMClient, LLMUnavailable
from app.schemas.contracts import CompanionInput, CompanionOutput


COMPANION_STYLES = {
    "cafe": "温柔、安静、像会陪你整理桌面的人，说话轻一点，但很稳。",
    "tamamo": "活泼一点，像会陪你打气的同伴，语气亲近。",
    "rice": "克制、耐心、很会安抚情绪，话不会很多，但句句落地。",
    "calstone": "偏成熟一点，像会替你稳住节奏的人，鼓励时有点坚定。",
    "staygold": "更坚定、清爽、有目标感，适合督促和拉回节奏。",
}


class CompanionAgent:
    confidence = 0.97

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def handle(self, payload: dict) -> dict:
        data = CompanionInput.model_validate(payload)
        style = COMPANION_STYLES.get(payload.get("companion_id", "cafe"), COMPANION_STYLES["cafe"])
        history = payload.get("history", [])[-4:]
        prompt = f"{COMPANION_PROMPT}\n\n角色风格: {style}\n\n最近对话: {history}"
        try:
            output = self.llm.complete_json(
                system_prompt=prompt,
                payload={
                    "user_id": data.user_id,
                    "message": data.message,
                    "history": history,
                    "companion_id": payload.get("companion_id", "cafe"),
                },
                output_model=CompanionOutput,
                temperature=0.82,
            )
        except LLMUnavailable:
            output = self._fallback(data)
        return output.model_dump()

    def _fallback(self, data: CompanionInput) -> CompanionOutput:
        message = data.message
        if any(word in message for word in ["焦虑", "紧张", "压力", "害怕", "慌"]):
            return CompanionOutput(
                emotion="anxious",
                reply="我知道你现在有点绷着，我们先不追求状态，先做一个很小的开头就行。",
                support_action="reduce_task",
            )
        if any(word in message for word in ["累", "困", "疲惫", "学不动"]):
            return CompanionOutput(
                emotion="tired",
                reply="你现在像是电量不太够，先缓一缓，再碰一个很轻的小任务。",
                support_action="short_break",
            )
        if any(word in message for word in ["失败", "挫折", "崩溃", "难受"]):
            return CompanionOutput(
                emotion="frustrated",
                reply="这一下确实有点重，我们先把心放稳，再找一个能完成的小步骤。",
                support_action="start_small",
            )
        return CompanionOutput(
            emotion="steady",
            reply="我在呢，我们先从一个很简单的小步骤开始。",
            support_action="start_small",
        )
