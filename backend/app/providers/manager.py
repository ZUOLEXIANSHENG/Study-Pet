from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.core.settings import Settings, get_settings


ProviderKind = Literal["llm", "image", "tts", "asr", "search"]


@dataclass(frozen=True)
class LLMProviderConfig:
    id: str
    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: float
    kind: ProviderKind = "llm"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class ImageProviderConfig:
    id: str
    api_key: str | None
    base_url: str
    model: str
    timeout_seconds: float
    default_size: str = "1024x1024"
    default_quality: str = "medium"
    kind: ProviderKind = "image"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class AudioProviderConfig:
    id: str
    api_key: str | None
    base_url: str
    tts_model: str
    asr_model: str
    voice: str
    timeout_seconds: float
    kind: ProviderKind = "tts"

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)


class ProviderManager:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def get_llm_provider(self, provider_id: str | None = None) -> LLMProviderConfig:
        selected = (provider_id or self.settings.default_llm_provider).lower()
        providers = self._llm_providers()
        if selected not in providers:
            available = ", ".join(sorted(providers))
            raise ValueError(f"Unknown LLM provider: {selected}. Available providers: {available}")
        provider = providers[selected]
        if provider.enabled:
            return provider

        legacy = providers["legacy"]
        if selected != "legacy" and legacy.enabled:
            return legacy
        return provider

    def get_image_provider(self, provider_id: str | None = None) -> ImageProviderConfig:
        selected = (provider_id or self.settings.default_image_provider).lower()
        providers = self._image_providers()
        if selected not in providers:
            available = ", ".join(sorted(providers))
            raise ValueError(f"Unknown image provider: {selected}. Available providers: {available}")
        provider = providers[selected]
        if provider.enabled:
            return provider

        fallback = providers["openai-image"]
        if selected != "openai-image" and fallback.enabled:
            return fallback
        return provider

    def get_audio_provider(self, provider_id: str | None = None) -> AudioProviderConfig:
        selected = (provider_id or self.settings.default_audio_provider).lower()
        providers = self._audio_providers()
        if selected not in providers:
            available = ", ".join(sorted(providers))
            raise ValueError(f"Unknown audio provider: {selected}. Available providers: {available}")
        provider = providers[selected]
        if provider.enabled:
            return provider
        fallback = providers["openai-audio"]
        if selected != "openai-audio" and fallback.enabled:
            return fallback
        return provider

    def _llm_providers(self) -> dict[str, LLMProviderConfig]:
        timeout = self.settings.llm_timeout_seconds
        return {
            "legacy": LLMProviderConfig(
                id="legacy",
                api_key=self.settings.llm_api_key,
                base_url=self.settings.llm_base_url,
                model=self.settings.llm_model,
                timeout_seconds=timeout,
            ),
            "openai": LLMProviderConfig(
                id="openai",
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                model=self.settings.openai_model,
                timeout_seconds=timeout,
            ),
            "qwen": LLMProviderConfig(
                id="qwen",
                api_key=self.settings.qwen_api_key,
                base_url=self.settings.qwen_base_url,
                model=self.settings.qwen_model,
                timeout_seconds=timeout,
            ),
            "deepseek": LLMProviderConfig(
                id="deepseek",
                api_key=self.settings.deepseek_api_key,
                base_url=self.settings.deepseek_base_url,
                model=self.settings.deepseek_model,
                timeout_seconds=timeout,
            ),
        }

    def _image_providers(self) -> dict[str, ImageProviderConfig]:
        timeout = self.settings.image_timeout_seconds
        return {
            "openai-image": ImageProviderConfig(
                id="openai-image",
                api_key=self.settings.image_api_key or self.settings.openai_image_api_key,
                base_url=self.settings.image_base_url or self.settings.openai_image_base_url,
                model=self.settings.image_model or self.settings.openai_image_model,
                timeout_seconds=timeout,
                default_size=self.settings.image_default_size,
                default_quality=self.settings.image_default_quality,
            ),
            "image2": ImageProviderConfig(
                id="image2",
                api_key=self.settings.image2_api_key,
                base_url=self.settings.image2_base_url,
                model=self.settings.image2_model,
                timeout_seconds=timeout,
                default_size=self.settings.image_default_size,
                default_quality=self.settings.image_default_quality,
            ),
        }

    def _audio_providers(self) -> dict[str, AudioProviderConfig]:
        timeout = self.settings.audio_timeout_seconds
        return {
            "openai-audio": AudioProviderConfig(
                id="openai-audio",
                api_key=self.settings.audio_api_key or self.settings.openai_api_key,
                base_url=self.settings.audio_base_url or self.settings.openai_base_url,
                tts_model=self.settings.tts_model,
                asr_model=self.settings.asr_model,
                voice=self.settings.tts_voice,
                timeout_seconds=timeout,
            )
        }
