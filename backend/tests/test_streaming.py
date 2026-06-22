import json

from fastapi.testclient import TestClient

from app.main import app
from app.streaming import build_chat_stream_events, encode_sse


def test_encode_sse_outputs_json_data_line() -> None:
    encoded = encode_sse({"type": "thinking", "agent": "companion"})
    assert encoded.startswith("data: ")
    assert encoded.endswith("\n\n")
    payload = json.loads(encoded.removeprefix("data: ").strip())
    assert payload == {"type": "thinking", "agent": "companion"}


def test_build_chat_stream_events_for_companion() -> None:
    envelope = {
        "agent": "companion",
        "result": {"emotion": "anxious", "reply": "我在这里，先做一个小任务。", "support_action": "reduce_task"},
        "confidence": 0.97,
    }
    events = list(build_chat_stream_events(envelope))
    assert events[0] == {"type": "thinking", "agent": "companion"}
    assert any(event["type"] == "text_delta" for event in events)
    assert {"type": "emotion", "value": "anxious"} in events
    assert {"type": "pet_action", "value": "comfort"} in events
    assert events[-1]["type"] == "done"
    assert events[-1]["agent"] == "companion"


def test_chat_stream_endpoint_returns_sse() -> None:
    client = TestClient(app)
    response = client.post("/api/chat/stream", json={"user_id": "demo", "message": "我今天很焦虑，学不动"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data: " in response.text
    assert '"type": "thinking"' in response.text
    assert '"type": "done"' in response.text
