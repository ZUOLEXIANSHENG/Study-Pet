from pydantic import BaseModel, Field


class OrchestratorEnvelope(BaseModel):
    agent: str
    result: dict
    confidence: float = Field(ge=0.0, le=1.0)


class PlannerInput(BaseModel):
    user_id: str = "demo"
    goal: str | None = None
    exam_type: str
    target_score: int
    days_left: int
    current_level: str = "unknown"


class DailyPlanItem(BaseModel):
    day: int
    task: str


class WeeklyPlanItem(BaseModel):
    week: int
    goal: str


class PlannerOutput(BaseModel):
    plan: list[DailyPlanItem]
    weekly_plan: list[WeeklyPlanItem] = []
    difficulty: str
    warning: str


class CoachInput(BaseModel):
    user_id: str = "demo"
    study_time: int
    task_completed: float
    completed_tasks: list[str] = []


class CoachOutput(BaseModel):
    status: str
    feedback: str
    suggestion: str


class CompanionInput(BaseModel):
    user_id: str = "demo"
    message: str


class CompanionOutput(BaseModel):
    emotion: str
    reply: str
    support_action: str


class GrowthInput(BaseModel):
    user_id: str = "demo"
    study_time: int = 0
    completed: bool = False
    scope: str = "session"


class GrowthOutput(BaseModel):
    exp: int
    level_up: bool
    growth_summary: str
    level: int | None = None
    mood: int | None = None
    focus: int | None = None


class RadarInput(BaseModel):
    user_id: str = "demo"
    study_days: int
    avg_time: int
    negative_words: int


class RadarOutput(BaseModel):
    risk_level: str
    signal: str
    action: str
