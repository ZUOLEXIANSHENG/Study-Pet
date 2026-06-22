from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./studypet.db", validation_alias="DATABASE_URL")

    default_llm_provider: str = Field(default="legacy", validation_alias="DEFAULT_LLM_PROVIDER")

    llm_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"),
    )
    llm_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias=AliasChoices("LLM_BASE_URL", "DEEPSEEK_BASE_URL", "OPENAI_BASE_URL"),
    )
    llm_model: str = Field(default="deepseek-v4-flash", validation_alias=AliasChoices("LLM_MODEL", "DEEPSEEK_MODEL"))
    llm_timeout_seconds: float = 20.0

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")

    qwen_api_key: str | None = Field(default=None, validation_alias="QWEN_API_KEY")
    qwen_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", validation_alias="QWEN_BASE_URL")
    qwen_model: str = Field(default="qwen-plus", validation_alias="QWEN_MODEL")

    deepseek_api_key: str | None = Field(default=None, validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", validation_alias="DEEPSEEK_BASE_URL")
    deepseek_model: str = Field(default="deepseek-v4-flash", validation_alias="DEEPSEEK_MODEL")

    planner_llm_provider: str | None = Field(default=None, validation_alias="PLANNER_LLM_PROVIDER")
    coach_llm_provider: str | None = Field(default=None, validation_alias="COACH_LLM_PROVIDER")
    companion_llm_provider: str | None = Field(default=None, validation_alias="COMPANION_LLM_PROVIDER")
    growth_llm_provider: str | None = Field(default=None, validation_alias="GROWTH_LLM_PROVIDER")
    radar_llm_provider: str | None = Field(default=None, validation_alias="RADAR_LLM_PROVIDER")

    default_image_provider: str = Field(default="openai-image", validation_alias="DEFAULT_IMAGE_PROVIDER")
    image_api_key: str | None = Field(default=None, validation_alias="IMAGE_API_KEY")
    image_base_url: str | None = Field(default=None, validation_alias="IMAGE_BASE_URL")
    image_model: str | None = Field(default=None, validation_alias="IMAGE_MODEL")
    image_timeout_seconds: float = Field(default=60.0, validation_alias="IMAGE_TIMEOUT_SECONDS")
    image_default_size: str = Field(default="1024x1024", validation_alias="IMAGE_DEFAULT_SIZE")
    image_default_quality: str = Field(default="medium", validation_alias="IMAGE_DEFAULT_QUALITY")

    openai_image_api_key: str | None = Field(default=None, validation_alias="OPENAI_IMAGE_API_KEY")
    openai_image_base_url: str = Field(default="https://api.openai.com/v1", validation_alias="OPENAI_IMAGE_BASE_URL")
    openai_image_model: str = Field(default="gpt-image-2", validation_alias="OPENAI_IMAGE_MODEL")

    image2_api_key: str | None = Field(default=None, validation_alias="IMAGE2_API_KEY")
    image2_base_url: str = Field(default="https://imgapi.zjapi.com/v1", validation_alias="IMAGE2_BASE_URL")
    image2_model: str = Field(default="gpt-image-2", validation_alias="IMAGE2_MODEL")

    default_audio_provider: str = Field(default="openai-audio", validation_alias="DEFAULT_AUDIO_PROVIDER")
    audio_api_key: str | None = Field(default=None, validation_alias="AUDIO_API_KEY")
    audio_base_url: str | None = Field(default=None, validation_alias="AUDIO_BASE_URL")
    audio_timeout_seconds: float = Field(default=60.0, validation_alias="AUDIO_TIMEOUT_SECONDS")
    tts_model: str = Field(default="gpt-4o-mini-tts", validation_alias="TTS_MODEL")
    tts_voice: str = Field(default="alloy", validation_alias="TTS_VOICE")
    asr_model: str = Field(default="whisper-1", validation_alias="ASR_MODEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
