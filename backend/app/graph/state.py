from __future__ import annotations

from typing import Any, Literal, TypedDict


AgentId = Literal["planner", "coach", "companion", "growth", "radar"]


class GraphEvent(TypedDict):
    node: str
    agent: str | None
    detail: str


class StudyPetGraphState(TypedDict, total=False):
    text: str
    payload: dict[str, Any]
    requested_agent: AgentId | None
    agent: AgentId
    normalized_text: str
    normalized_payload: dict[str, Any]
    result: dict[str, Any]
    confidence: float
    envelope: dict[str, Any]
    events: list[GraphEvent]
