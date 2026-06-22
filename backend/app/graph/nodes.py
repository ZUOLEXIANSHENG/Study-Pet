from __future__ import annotations

from app.agents.registry import AgentRegistry
from app.graph.router import determine_agent, normalize_payload, normalize_text, prepare_payload
from app.graph.state import AgentId, GraphEvent, StudyPetGraphState
from app.schemas.contracts import OrchestratorEnvelope


class StudyPetGraphNodes:
    def __init__(self) -> None:
        self.registry = AgentRegistry()
        self.recorded_events: list[GraphEvent] = []

    def input_normalizer(self, state: StudyPetGraphState) -> StudyPetGraphState:
        text = normalize_text(state.get("text"))
        payload = normalize_payload(state.get("payload"))
        return {
            **state,
            "normalized_text": text,
            "normalized_payload": payload,
            "events": self._append_event(state, "InputNormalizer", None, "input normalized"),
        }

    def intent_router(self, state: StudyPetGraphState) -> StudyPetGraphState:
        agent = determine_agent(
            text=state.get("normalized_text", ""),
            payload=state.get("normalized_payload", {}),
            requested_agent=state.get("requested_agent"),
        )
        payload = prepare_payload(agent, state.get("normalized_text", ""), state.get("normalized_payload", {}))
        return {
            **state,
            "agent": agent,
            "normalized_payload": payload,
            "events": self._append_event(state, "IntentRouter", agent, "single agent selected"),
        }

    def single_agent_executor(self, state: StudyPetGraphState) -> StudyPetGraphState:
        agent = state["agent"]
        handler = self.registry.get_handler(agent)
        result = handler.handle(state.get("normalized_payload", {}))
        confidence = self.registry.get_config(agent).confidence
        return {
            **state,
            "result": result,
            "confidence": confidence,
            "events": self._append_event(state, "SingleAgentExecutor", agent, "agent executed"),
        }

    def schema_validator(self, state: StudyPetGraphState) -> StudyPetGraphState:
        agent = state["agent"]
        output_model = self.registry.get_config(agent).output_schema
        validated_result = output_model.model_validate(state.get("result", {})).model_dump()
        envelope = OrchestratorEnvelope(
            agent=agent,
            result=validated_result,
            confidence=state.get("confidence", 0.0),
        ).model_dump()
        return {
            **state,
            "result": validated_result,
            "envelope": envelope,
            "events": self._append_event(state, "SchemaValidator", agent, "schema validated"),
        }

    def event_recorder(self, state: StudyPetGraphState) -> StudyPetGraphState:
        events = self._append_event(state, "EventRecorder", state.get("agent"), "request completed")
        self.recorded_events.extend(events[-1:])
        return {**state, "events": events}

    def _append_event(
        self,
        state: StudyPetGraphState,
        node: str,
        agent: AgentId | None,
        detail: str,
    ) -> list[GraphEvent]:
        events = list(state.get("events", []))
        events.append({"node": node, "agent": agent, "detail": detail})
        return events
