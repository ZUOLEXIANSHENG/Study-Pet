from pydantic import BaseModel, Field


class BaseUserRequest(BaseModel):
    user_id: str = "demo"
    goal: str | None = None


class PlanGenerateRequest(BaseUserRequest):
    exam_type: str
    target_score: int = Field(ge=0, le=750)
    days_left: int = Field(ge=1, le=3650)
    current_level: str = "unknown"


class StudyStartRequest(BaseUserRequest):
    study_time: int = Field(ge=0)
    task_completed: float = Field(ge=0.0, le=1.0)


class StudyEndRequest(StudyStartRequest):
    completed_tasks: list[str] = []


class MoodCheckRequest(BaseUserRequest):
    message: str
    companion_id: str = "cafe"
    history: list[dict[str, str]] = []


class ChatRequest(BaseUserRequest):
    message: str
    history: list[dict[str, str]] = []


class DailyReportRequest(BaseUserRequest):
    scope: str = "daily"


class WeeklyReportRequest(BaseUserRequest):
    scope: str = "weekly"
