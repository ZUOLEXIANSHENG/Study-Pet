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


class ImageGenerateRequest(BaseUserRequest):
    prompt: str
    style: str = "premium cute ai companion"
    aspect_ratio: str = "1:1"
    provider: str | None = None


class ImageGenerateResponse(BaseModel):
    image_url: str | None = None
    b64_json: str | None = None
    provider: str
    status: str


class TTSRequest(BaseUserRequest):
    text: str
    voice: str | None = None
    provider: str | None = None


class TTSResponse(BaseModel):
    audio_base64: str
    provider: str
    status: str


class ASRResponse(BaseModel):
    text: str
    provider: str
    status: str


class DocumentParseResponse(BaseModel):
    filename: str
    content_type: str
    text: str
    word_count: int
    status: str = "success"


class InteractiveGenerateRequest(BaseUserRequest):
    type: str = "mindmap"
    topic: str = ""
    source_text: str = ""
    plan_items: list[dict] = []


class InteractiveCompleteRequest(BaseUserRequest):
    activity_id: str
    type: str = "mindmap"
    completed_steps: list[str] = []
