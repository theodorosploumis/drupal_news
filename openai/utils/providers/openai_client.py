from __future__ import annotations

import os
from typing import Optional

from .base import ProviderSettings


class OpenAIClient:
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not configured")
        try:  # pragma: no cover - optional dependency
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("openai package not installed") from exc
        self._client = OpenAI(api_key=api_key)

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self._client.responses.create(  # pragma: no cover - network call
            model=self.settings.model,
            temperature=self.settings.temperature,
            max_output_tokens=max_tokens,
            input=prompt,
        )
        return response.output_text.strip()


def create(settings: ProviderSettings):
    return OpenAIClient(settings)
