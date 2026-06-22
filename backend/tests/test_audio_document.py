from typing import Any

from fastapi.testclient import TestClient

from app.core.settings import Settings
from app.documents.parser import DocumentParser
from app.main import app
from app.providers.audio import AudioService
from app.providers.manager import ProviderManager


class FakeAudioService(AudioService):
    def __init__(self, provider_manager: ProviderManager) -> None:
        super().__init__(provider_manager)
        self.last_body: dict[str, Any] | None = None

    def _post_binary(self, *, url: str, api_key: str, body: dict[str, Any], timeout: float) -> bytes:
        self.last_body = body
        return b"mp3-bytes"


def test_audio_provider_config_uses_openai_audio() -> None:
    settings = Settings(AUDIO_API_KEY="audio-key", AUDIO_BASE_URL="https://audio.example/v1")
    provider = ProviderManager(settings).get_audio_provider()
    assert provider.id == "openai-audio"
    assert provider.api_key == "audio-key"
    assert provider.base_url == "https://audio.example/v1"


def test_tts_service_returns_base64_without_network() -> None:
    settings = Settings(AUDIO_API_KEY="audio-key", AUDIO_BASE_URL="https://audio.example/v1")
    service = FakeAudioService(ProviderManager(settings))
    result = service.synthesize(text="Keep going")
    assert result == {"audio_base64": "bXAzLWJ5dGVz", "provider": "openai-audio", "status": "success"}
    assert service.last_body is not None
    assert service.last_body["input"] == "Keep going"


def test_tts_endpoint_returns_503_when_provider_is_not_configured() -> None:
    client = TestClient(app)
    response = client.post("/api/audio/tts", json={"text": "Keep going"})
    assert response.status_code == 503


def test_document_parser_reads_txt() -> None:
    parsed = DocumentParser().parse(
        filename="outline.txt",
        content="数学第一章\n函数与导数".encode("utf-8"),
        content_type="text/plain",
    )
    assert parsed.filename == "outline.txt"
    assert "函数与导数" in parsed.text
    assert parsed.word_count >= 1


def test_document_parse_endpoint_reads_txt_upload() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/document/parse",
        files={"file": ("outline.txt", "数学第一章\n函数与导数".encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "函数与导数" in data["text"]


def test_generate_plan_from_document_uses_planner() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/plan/generate-from-document",
        data={"exam_type": "高考数学", "target_score": "120", "days_left": "30", "current_level": "中等"},
        files={"file": ("outline.txt", "函数、导数、三角函数".encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["agent"] == "planner"
    assert "plan" in data["result"]
