from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import StudyPetGraphNodes
from app.graph.state import AgentId, StudyPetGraphState


class StudyPetGraph:
    def __init__(self) -> None:
        self.nodes = StudyPetGraphNodes()
        self.app = self._build_graph()

    def invoke(
        self,
        *,
        payload: dict[str, Any],
        text: str = "",
        requested_agent: AgentId | None = None,
    ) -> dict[str, Any]:
        state: StudyPetGraphState = {
            "text": text,
            "payload": payload,
            "requested_agent": requested_agent,
            "events": [],
        }
        result = self.app.invoke(state)
        return result["envelope"]

    def _build_graph(self):
        graph = StateGraph(StudyPetGraphState)
        graph.add_node("InputNormalizer", self.nodes.input_normalizer)
        graph.add_node("IntentRouter", self.nodes.intent_router)
        graph.add_node("SingleAgentExecutor", self.nodes.single_agent_executor)
        graph.add_node("SchemaValidator", self.nodes.schema_validator)
        graph.add_node("EventRecorder", self.nodes.event_recorder)
        graph.add_edge(START, "InputNormalizer")
        graph.add_edge("InputNormalizer", "IntentRouter")
        graph.add_edge("IntentRouter", "SingleAgentExecutor")
        graph.add_edge("SingleAgentExecutor", "SchemaValidator")
        graph.add_edge("SchemaValidator", "EventRecorder")
        graph.add_edge("EventRecorder", END)
        return graph.compile()
