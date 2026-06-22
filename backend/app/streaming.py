from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any


def encode_sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def build_chat_stream_events(envelope: dict[str, Any]) -> Iterable[dict[str, Any]]:
    agent = envelope.get("agent", "companion")
    result = envelope.get("result", {})

    yield {"type": "thinking", "agent": agent}

    text = _display_text(agent, result)
    for chunk in _chunk_text(text):
        yield {"type": "text_delta", "content": chunk}

    emotion = result.get("emotion")
    if emotion:
        yield {"type": "emotion", "value": emotion}

    pet_action = _pet_action(agent, result)
    if pet_action:
        yield {"type": "pet_action", "value": pet_action}

    yield {"type": "done", "agent": agent, "result": result, "confidence": envelope.get("confidence", 0.0)}


def _display_text(agent: str, result: dict[str, Any]) -> str:
    if agent == "companion":
        return str(result.get("reply", ""))
    if agent == "planner":
        warning = result.get("warning", "")
        return f"学习计划已生成。{warning}".strip()
    if agent == "coach":
        return " ".join(part for part in [result.get("feedback", ""), result.get("suggestion", "")] if part)
    if agent == "growth":
        return str(result.get("growth_summary", "成长记录已更新。"))
    if agent == "radar":
        return " ".join(part for part in [result.get("signal", ""), result.get("action", "")] if part)
    return json.dumps(result, ensure_ascii=False)


def _pet_action(agent: str, result: dict[str, Any]) -> str:
    if agent == "companion":
        support_action = result.get("support_action", "encourage")
        mapping = {
            "reduce_task": "comfort",
            "short_break": "comfort",
            "start_small": "encourage",
            "encourage": "encourage",
        }
        return mapping.get(str(support_action), "encourage")
    if agent == "coach":
        status = result.get("status")
        return "celebrate" if status == "good" else "remind"
    if agent == "planner":
        return "plan"
    if agent == "growth":
        return "celebrate" if result.get("level_up") else "grow"
    if agent == "radar":
        return "comfort" if result.get("risk_level") in {"medium", "high"} else "steady"
    return "steady"


def _chunk_text(text: str, chunk_size: int = 12) -> Iterable[str]:
    for index in range(0, len(text), chunk_size):
        yield text[index : index + chunk_size]
