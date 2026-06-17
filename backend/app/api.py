from fastapi import APIRouter

from app.core.orchestrator import Orchestrator
from app.schemas.api import (
    ChatRequest,
    MoodCheckRequest,
    PlanGenerateRequest,
    StudyEndRequest,
    StudyStartRequest,
)

router = APIRouter(prefix="/api")
orchestrator = Orchestrator()


@router.post("/plan/generate")
def generate_plan(payload: PlanGenerateRequest) -> dict:
    return orchestrator.route("planner", payload.model_dump())


@router.post("/study/start")
def study_start(payload: StudyStartRequest) -> dict:
    return orchestrator.route("coach", payload.model_dump())


@router.post("/study/end")
def study_end(payload: StudyEndRequest) -> dict:
    return orchestrator.route("coach", payload.model_dump())


@router.post("/growth/update")
def growth_update(payload: StudyEndRequest) -> dict:
    completed = payload.task_completed >= 0.8
    return orchestrator.route("growth", payload.model_dump() | {"completed": completed})


@router.post("/mood/check")
def mood_check(payload: MoodCheckRequest) -> dict:
    return orchestrator.route("companion", payload.model_dump())


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    return orchestrator.route_from_text(payload.message, payload.model_dump())


@router.get("/report/daily")
def report_daily(user_id: str = "demo") -> dict:
    return orchestrator.route("growth", {"user_id": user_id, "scope": "daily"})


@router.get("/report/weekly")
def report_weekly(user_id: str = "demo") -> dict:
    return orchestrator.route("growth", {"user_id": user_id, "scope": "weekly"})


@router.get("/companion")
def companion(user_id: str = "demo") -> dict:
    return orchestrator.route("companion", {"user_id": user_id, "message": "我想学习但有点焦虑"})
