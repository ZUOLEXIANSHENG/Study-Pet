from fastapi.testclient import TestClient

from app.main import app


def test_api_events_persist_after_chat() -> None:
    client = TestClient(app)
    response = client.post("/api/chat", json={"user_id": "persist-demo", "message": "我今天很焦虑"})
    assert response.status_code == 200

    events = client.get("/api/events?user_id=persist-demo&limit=5")
    assert events.status_code == 200
    data = events.json()["events"]
    assert any(event["event_type"] == "chat.message" for event in data)
