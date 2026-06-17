from app.core.orchestrator import Orchestrator


def test_plan_routes_to_planner() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route("planner", {"exam_type": "考研数学", "target_score": 120, "days_left": 30, "current_level": "中等"})
    assert result["agent"] == "planner"
    assert "plan" in result["result"]


def test_text_router_is_single_agent() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route_from_text("我今天很焦虑，学不动", {"user_id": "demo"})
    assert result["agent"] == "companion"
    assert set(result.keys()) == {"agent", "result", "confidence"}
