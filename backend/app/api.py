from collections.abc import Iterable

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.orchestrator import Orchestrator
from app.db import list_events, record_event
from app.documents.parser import DocumentParseError, DocumentParser
from app.interactive import complete_activity, generate_activity
from app.providers.audio import AudioGenerationError, AudioProviderUnavailable, AudioService
from app.providers.image import ImageGenerationError, ImageGenerationService, ImageProviderUnavailable
from app.schemas.api import (
    ASRResponse,
    ChatRequest,
    DocumentParseResponse,
    ImageGenerateRequest,
    ImageGenerateResponse,
    InteractiveCompleteRequest,
    InteractiveGenerateRequest,
    MoodCheckRequest,
    PlanGenerateRequest,
    StudyEndRequest,
    StudyStartRequest,
    TTSRequest,
    TTSResponse,
)
from app.streaming import build_chat_stream_events, encode_sse

router = APIRouter(prefix="/api")
orchestrator = Orchestrator()
image_service = ImageGenerationService()
audio_service = AudioService()
document_parser = DocumentParser()


@router.post("/plan/generate")
def generate_plan(payload: PlanGenerateRequest) -> dict:
    data = payload.model_dump()
    result = orchestrator.route("planner", data)
    record_event(event_type="plan.generate", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/study/start")
def study_start(payload: StudyStartRequest) -> dict:
    data = payload.model_dump()
    result = orchestrator.route("coach", data)
    record_event(event_type="study.start", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/study/end")
def study_end(payload: StudyEndRequest) -> dict:
    data = payload.model_dump()
    result = orchestrator.route("coach", data)
    record_event(event_type="study.end", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/growth/update")
def growth_update(payload: StudyEndRequest) -> dict:
    data = payload.model_dump() | {"completed": payload.task_completed >= 0.8}
    result = orchestrator.route("growth", data)
    record_event(event_type="growth.update", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/mood/check")
def mood_check(payload: MoodCheckRequest) -> dict:
    data = payload.model_dump()
    result = orchestrator.route("companion", data)
    record_event(event_type="mood.check", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/chat")
def chat(payload: ChatRequest) -> dict:
    data = payload.model_dump()
    result = orchestrator.route_from_text(payload.message, data)
    record_event(event_type="chat.message", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    def event_stream() -> Iterable[str]:
        data = payload.model_dump()
        envelope = orchestrator.route_from_text(payload.message, data)
        record_event(event_type="chat.stream", user_id=payload.user_id, payload=data, result=envelope)
        for event in build_chat_stream_events(envelope):
            yield encode_sse(event)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/media/image/generate", response_model=ImageGenerateResponse)
def generate_image(payload: ImageGenerateRequest) -> dict:
    data = payload.model_dump()
    try:
        result = image_service.generate(
            prompt=payload.prompt,
            style=payload.style,
            aspect_ratio=payload.aspect_ratio,
            provider_id=payload.provider,
        )
        record_event(event_type="media.image.generate", user_id=payload.user_id, payload=data, result=result)
        return result
    except ImageProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ImageGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/audio/tts", response_model=TTSResponse)
def text_to_speech(payload: TTSRequest) -> dict:
    data = payload.model_dump()
    try:
        result = audio_service.synthesize(text=payload.text, voice=payload.voice, provider_id=payload.provider)
        record_event(event_type="audio.tts", user_id=payload.user_id, payload=data, result={"provider": result["provider"], "status": result["status"]})
        return result
    except AudioProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AudioGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/audio/asr", response_model=ASRResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    provider: str | None = Form(default=None),
    user_id: str = Form(default="demo"),
) -> dict:
    try:
        content = await file.read()
        result = audio_service.transcribe(filename=file.filename or "audio.wav", content=content, provider_id=provider)
        record_event(
            event_type="audio.asr",
            user_id=user_id,
            payload={"filename": file.filename, "provider": provider},
            result=result,
        )
        return result
    except AudioProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AudioGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/document/parse", response_model=DocumentParseResponse)
async def parse_document(file: UploadFile = File(...), user_id: str = Form(default="demo")) -> dict:
    try:
        content = await file.read()
        parsed = document_parser.parse(
            filename=file.filename or "document.txt",
            content=content,
            content_type=file.content_type,
        )
        result = parsed.__dict__ | {"status": "success"}
        record_event(
            event_type="document.parse",
            user_id=user_id,
            payload={"filename": file.filename, "content_type": file.content_type},
            result=result,
        )
        return result
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/plan/generate-from-document")
async def generate_plan_from_document(
    file: UploadFile = File(...),
    exam_type: str = Form(default="学习资料"),
    target_score: int = Form(default=100),
    days_left: int = Form(default=30),
    current_level: str = Form(default="unknown"),
    user_id: str = Form(default="demo"),
) -> dict:
    try:
        content = await file.read()
        parsed = document_parser.parse(
            filename=file.filename or "document.txt",
            content=content,
            content_type=file.content_type,
        )
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    payload = {
        "user_id": user_id,
        "goal": f"根据资料生成学习计划：{parsed.text[:1200]}",
        "exam_type": exam_type,
        "target_score": target_score,
        "days_left": days_left,
        "current_level": current_level,
    }
    result = orchestrator.route("planner", payload)
    record_event(
        event_type="plan.generate_from_document",
        user_id=user_id,
        payload=payload | {"filename": parsed.filename},
        result=result,
    )
    return result


@router.get("/events")
def events(user_id: str = "demo", limit: int = 50) -> dict:
    return {"events": list_events(user_id=user_id, limit=limit)}


@router.post("/interactive/generate")
def interactive_generate(payload: InteractiveGenerateRequest) -> dict:
    data = payload.model_dump()
    result = generate_activity(data)
    record_event(event_type="interactive.generate", user_id=payload.user_id, payload=data, result=result)
    return result


@router.post("/interactive/complete")
def interactive_complete(payload: InteractiveCompleteRequest) -> dict:
    data = payload.model_dump()
    result = complete_activity(data)
    record_event(event_type="interactive.complete", user_id=payload.user_id, payload=data, result=result)
    return result


@router.get("/report/daily")
def report_daily(user_id: str = "demo") -> dict:
    result = orchestrator.route("growth", {"user_id": user_id, "scope": "daily"})
    record_event(event_type="report.daily", user_id=user_id, payload={"scope": "daily"}, result=result)
    return result


@router.get("/report/weekly")
def report_weekly(user_id: str = "demo") -> dict:
    result = orchestrator.route("growth", {"user_id": user_id, "scope": "weekly"})
    record_event(event_type="report.weekly", user_id=user_id, payload={"scope": "weekly"}, result=result)
    return result


@router.get("/companion")
def companion(user_id: str = "demo") -> dict:
    result = orchestrator.route("companion", {"user_id": user_id, "message": "我想学习，但有点焦虑"})
    record_event(event_type="companion.get", user_id=user_id, payload={"message": "我想学习，但有点焦虑"}, result=result)
    return result
