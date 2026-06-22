from typing import Any

from fastapi.testclient import TestClient

from app.core.settings import Settings
from app.main import app
from app.providers.image import ImageGenerationService
from app.providers.manager import ProviderManager


class FakeImageGenerationService(ImageGenerationService):
    def __init__(self, provider_manager: ProviderManager) -> None:
        super().__init__(provider_manager)
        self.last_body: dict[str, Any] | None = None

    def _post_json(self, *, url: str, api_key: str, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        self.last_body = body
        return {"data": [{"url": "https://example.com/studypet.png"}]}


def test_provider_manager_selects_image2_provider() -> None:
    settings = Settings(
        DEFAULT_IMAGE_PROVIDER="image2",
        IMAGE2_API_KEY="image-key",
        IMAGE2_BASE_URL="https://imgapi.example/v1",
        IMAGE2_MODEL="gpt-image-2",
    )
    provider = ProviderManager(settings).get_image_provider()
    assert provider.id == "image2"
    assert provider.api_key == "image-key"
    assert provider.base_url == "https://imgapi.example/v1"
    assert provider.model == "gpt-image-2"


def test_image_generation_service_returns_url_without_network() -> None:
    settings = Settings(
        DEFAULT_IMAGE_PROVIDER="image2",
        IMAGE2_API_KEY="image-key",
        IMAGE2_BASE_URL="https://imgapi.example/v1",
        IMAGE2_MODEL="gpt-image-2",
    )
    service = FakeImageGenerationService(ProviderManager(settings))
    result = service.generate(prompt="A cute StudyPet avatar", aspect_ratio="16:9", provider_id="image2")
    assert result == {
        "image_url": "https://example.com/studypet.png",
        "b64_json": None,
        "provider": "image2",
        "status": "success",
    }
    assert service.last_body is not None
    assert service.last_body["size"] == "1536x864"
    assert service.last_body["model"] == "gpt-image-2"


def test_image_generate_endpoint_returns_503_when_provider_is_not_configured() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/media/image/generate",
        json={"prompt": "A cute StudyPet avatar", "provider": "image2"},
    )
    assert response.status_code == 503
