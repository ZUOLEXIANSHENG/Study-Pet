from app.core.orchestrator import Orchestrator


def test_plan_routes_to_planner() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route(
        "planner",
        {"exam_type": "考研数学", "target_score": 120, "days_left": 30, "current_level": "中等"},
    )
    assert result["agent"] == "planner"
    assert "plan" in result["result"]


def test_text_router_is_single_agent() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route_from_text("我今天很焦虑，学不动", {"user_id": "demo"})
    assert result["agent"] == "companion"
    assert set(result.keys()) == {"agent", "result", "confidence"}


def test_chinese_plan_intent_routes_to_planner() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route_from_text(
        "帮我制定考研数学计划",
        {"exam_type": "考研数学", "target_score": 120, "days_left": 30, "current_level": "中等"},
    )
    assert result["agent"] == "planner"
    assert set(result.keys()) == {"agent", "result", "confidence"}
    assert "weekly_plan" in result["result"]


def test_chinese_growth_intent_routes_to_growth() -> None:
    orchestrator = Orchestrator()
    result = orchestrator.route_from_text("看看我的成长等级和经验", {"user_id": "demo", "study_time": 60, "completed": True})
    assert result["agent"] == "growth"
    assert set(result.keys()) == {"agent", "result", "confidence"}
    assert "exp" in result["result"]
