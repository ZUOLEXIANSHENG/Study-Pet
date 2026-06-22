from __future__ import annotations

from app.agents.registry import AGENT_IDS
from app.graph.graph import StudyPetGraph
from app.graph.state import AgentId


class Orchestrator:
    def __init__(self) -> None:
        self.graph = StudyPetGraph()

    def route(self, agent_name: str, payload: dict) -> dict:
        return self.graph.invoke(payload=payload, requested_agent=self._validate_agent(agent_name))

    def route_from_text(self, text: str, payload: dict) -> dict:
        return self.graph.invoke(text=text, payload=payload)

    def _validate_agent(self, agent_name: str) -> AgentId:
        if agent_name not in AGENT_IDS:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent_name  # type: ignore[return-value]
