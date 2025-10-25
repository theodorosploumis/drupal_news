from __future__ import annotations

import os
from typing import Optional

from .base import ProviderSettings


class GeminiClient:
    def __init__(self, settings: ProviderSettings) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not configured")
        try:  # pragma: no cover - optional dependency
            import google.generativeai as genai
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("google-generativeai package not installed") from exc
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(settings.model)
        self.settings = settings

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        generation = self._model.generate_content(  # pragma: no cover - network call
            prompt,
            generation_config={
                "temperature": self.settings.temperature,
                "max_output_tokens": max_tokens,
            },
        )
        return generation.text.strip()


def create(settings: ProviderSettings):
    return GeminiClient(settings)
