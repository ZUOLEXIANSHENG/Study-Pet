from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.settings import get_settings

OutputModel = TypeVar("OutputModel", bound=BaseModel)


class LLMUnavailable(RuntimeError):
    pass


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.llm_api_key)

    def complete_json(
        self,
        *,
        system_prompt: str,
        payload: dict[str, Any],
        output_model: type[OutputModel],
        temperature: float = 0.3,
    ) -> OutputModel:
        if not self.enabled:
            raise LLMUnavailable("LLM_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMUnavailable("openai package is not installed") from exc

        client = OpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            timeout=self.settings.llm_timeout_seconds,
        )
        response = client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
            return output_model.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMUnavailable("LLM response did not match the required schema") from exc
