from __future__ import annotations

import json
import mimetypes
import uuid
import urllib.error
import urllib.request
from typing import Any

from app.providers.manager import ProviderManager


class AudioProviderUnavailable(RuntimeError):
    pass


class AudioGenerationError(RuntimeError):
    pass


class AudioService:
    def __init__(self, provider_manager: ProviderManager | None = None) -> None:
        self.provider_manager = provider_manager or ProviderManager()

    def synthesize(
        self,
        *,
        text: str,
        voice: str | None = None,
        provider_id: str | None = None,
    ) -> dict[str, Any]:
        provider = self.provider_manager.get_audio_provider(provider_id)
        if not provider.enabled:
            raise AudioProviderUnavailable(f"Audio provider {provider.id} is not configured")
        body = {
            "model": provider.tts_model,
            "input": text,
            "voice": voice or provider.voice,
            "format": "mp3",
        }
        audio = self._post_binary(
            url=f"{provider.base_url.rstrip('/')}/audio/speech",
            api_key=provider.api_key or "",
            body=body,
            timeout=provider.timeout_seconds,
        )
        return {
            "audio_base64": self._to_base64(audio),
            "provider": provider.id,
            "status": "success",
        }

    def transcribe(
        self,
        *,
        filename: str,
        content: bytes,
        provider_id: str | None = None,
    ) -> dict[str, Any]:
        provider = self.provider_manager.get_audio_provider(provider_id)
        if not provider.enabled:
            raise AudioProviderUnavailable(f"Audio provider {provider.id} is not configured")
        body, content_type = self._multipart_body(
            fields={"model": provider.asr_model},
            files={"file": (filename, content, mimetypes.guess_type(filename)[0] or "application/octet-stream")},
        )
        response = self._post_multipart(
            url=f"{provider.base_url.rstrip('/')}/audio/transcriptions",
            api_key=provider.api_key or "",
            body=body,
            content_type=content_type,
            timeout=provider.timeout_seconds,
        )
        return {
            "text": str(response.get("text", "")),
            "provider": provider.id,
            "status": "success",
        }

    def _post_binary(self, *, url: str, api_key: str, body: dict[str, Any], timeout: float) -> bytes:
        request = urllib.request.Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            raise AudioGenerationError(exc.read().decode("utf-8", errors="replace")) from exc
        except urllib.error.URLError as exc:
            raise AudioGenerationError(str(exc)) from exc

    def _post_multipart(
        self,
        *,
        url: str,
        api_key: str,
        body: bytes,
        content_type: str,
        timeout: float,
    ) -> dict[str, Any]:
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": content_type},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise AudioGenerationError(exc.read().decode("utf-8", errors="replace")) from exc
        except urllib.error.URLError as exc:
            raise AudioGenerationError(str(exc)) from exc

    def _multipart_body(
        self,
        *,
        fields: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
    ) -> tuple[bytes, str]:
        boundary = f"----StudyPetBoundary{uuid.uuid4().hex}"
        chunks: list[bytes] = []
        for name, value in fields.items():
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode(),
                    f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
                    value.encode(),
                    b"\r\n",
                ]
            )
        for name, (filename, content, mime) in files.items():
            chunks.extend(
                [
                    f"--{boundary}\r\n".encode(),
                    f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode(),
                    f"Content-Type: {mime}\r\n\r\n".encode(),
                    content,
                    b"\r\n",
                ]
            )
        chunks.append(f"--{boundary}--\r\n".encode())
        return b"".join(chunks), f"multipart/form-data; boundary={boundary}"

    def _to_base64(self, data: bytes) -> str:
        import base64

        return base64.b64encode(data).decode("ascii")
