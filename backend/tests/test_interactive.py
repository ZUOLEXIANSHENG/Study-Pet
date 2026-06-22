from fastapi.testclient import TestClient

from app.main import app


def test_generate_interactive_mindmap() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/interactive/generate",
        json={
            "user_id": "interactive-demo",
            "type": "mindmap",
            "topic": "考研数学",
            "plan_items": [{"day": 1, "task": "极限基础"}],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "mindmap"
    assert data["title"] == "考研数学知识地图"
    assert data["nodes"][0]["id"] == "root"
    assert data["steps"]
    assert data["completion_rule"]


def test_complete_interactive_activity_is_persisted() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/interactive/complete",
        json={
            "user_id": "interactive-complete-demo",
            "activity_id": "activity-1",
            "type": "challenge",
            "completed_steps": ["stage-1", "stage-2"],
        },
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True

    events = client.get("/api/events?user_id=interactive-complete-demo&limit=5")
    assert events.status_code == 200
    data = events.json()["events"]
    assert any(event["event_type"] == "interactive.complete" for event in data)
