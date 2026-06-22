from app.core.settings import Settings
from app.agents.registry import AgentRegistry
from app.providers.manager import ProviderManager


def test_provider_manager_uses_selected_deepseek_provider() -> None:
    settings = Settings(
        DEFAULT_LLM_PROVIDER="deepseek",
        DEEPSEEK_API_KEY="deepseek-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        DEEPSEEK_MODEL="deepseek-chat",
    )
    provider = ProviderManager(settings).get_llm_provider()
    assert provider.id == "deepseek"
    assert provider.api_key == "deepseek-key"
    assert provider.model == "deepseek-chat"


def test_provider_manager_keeps_legacy_fallback() -> None:
    settings = Settings(
        DEFAULT_LLM_PROVIDER="qwen",
        LLM_API_KEY="legacy-key",
        LLM_BASE_URL="https://legacy.example/v1",
        LLM_MODEL="legacy-model",
    )
    provider = ProviderManager(settings).get_llm_provider()
    assert provider.id == "legacy"
    assert provider.api_key == "legacy-key"
    assert provider.base_url == "https://legacy.example/v1"
    assert provider.model == "legacy-model"


def test_provider_manager_returns_disabled_selected_provider_without_legacy() -> None:
    settings = Settings(DEFAULT_LLM_PROVIDER="openai")
    provider = ProviderManager(settings).get_llm_provider()
    assert provider.id == "openai"
    assert provider.enabled is False


def test_agent_registry_injects_per_agent_provider() -> None:
    settings = Settings(
        DEFAULT_LLM_PROVIDER="deepseek",
        COMPANION_LLM_PROVIDER="qwen",
        PLANNER_LLM_PROVIDER="openai",
    )
    registry = AgentRegistry(settings)
    assert registry.get_config("companion").llm_provider == "qwen"
    assert registry.get_config("planner").llm_provider == "openai"
    assert registry.get_handler("companion").llm.provider_id == "qwen"
    assert registry.get_handler("planner").llm.provider_id == "openai"


def test_agent_registry_uses_default_provider_when_agent_override_is_empty() -> None:
    settings = Settings(DEFAULT_LLM_PROVIDER="deepseek")
    registry = AgentRegistry(settings)
    assert registry.get_config("radar").llm_provider is None
    assert registry.get_handler("radar").llm.provider_id is None
