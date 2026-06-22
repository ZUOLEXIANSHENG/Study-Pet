from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from app.providers.manager import ProviderManager


class ImageProviderUnavailable(RuntimeError):
    pass


class ImageGenerationError(RuntimeError):
    pass


class ImageGenerationService:
    def __init__(self, provider_manager: ProviderManager | None = None) -> None:
        self.provider_manager = provider_manager or ProviderManager()

    def generate(
        self,
        *,
        prompt: str,
        style: str = "premium cute ai companion",
        aspect_ratio: str = "1:1",
        provider_id: str | None = None,
    ) -> dict[str, Any]:
        provider = self.provider_manager.get_image_provider(provider_id)
        if not provider.enabled:
            raise ImageProviderUnavailable(f"Image provider {provider.id} is not configured")

        body = {
            "model": provider.model,
            "prompt": self._compose_prompt(prompt, style),
            "size": self._size_for(aspect_ratio, provider.default_size),
            "quality": provider.default_quality,
            "n": 1,
        }
        response = self._post_json(
            url=f"{provider.base_url.rstrip('/')}/images/generations",
            api_key=provider.api_key or "",
            body=body,
            timeout=provider.timeout_seconds,
        )
        data = response.get("data") or []
        if not data:
            raise ImageGenerationError("Image provider returned no image data")
        first = data[0]
        image_url = first.get("url")
        b64_json = first.get("b64_json")
        return {
            "image_url": image_url,
            "b64_json": b64_json,
            "provider": provider.id,
            "status": "success",
        }

    def _post_json(self, *, url: str, api_key: str, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ImageGenerationError(detail) from exc
        except urllib.error.URLError as exc:
            raise ImageGenerationError(str(exc)) from exc

    def _compose_prompt(self, prompt: str, style: str) -> str:
        return (
            f"{prompt}\n\n"
            f"Style: {style}. Premium StudyPet visual system, calm, warm, intelligent, minimal, polished. "
            "Avoid clutter, watermarks, childish game UI, and unreadable dense text."
        )

    def _size_for(self, aspect_ratio: str, default_size: str) -> str:
        mapping = {
            "1:1": "1024x1024",
            "16:9": "1536x864",
            "9:16": "864x1536",
            "4:3": "1024x768",
            "3:4": "768x1024",
        }
        return mapping.get(aspect_ratio, default_size)
