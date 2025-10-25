from __future__ import annotations

import os
from typing import Optional

from .base import ProviderSettings


class QwenClient:
    def __init__(self, settings: ProviderSettings) -> None:
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            raise RuntimeError("QWEN_API_KEY not configured")
        try:  # pragma: no cover - optional dependency
            from dashscope import Generation
            from dashscope.api_entities import TextGenerationRequest
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("dashscope package not installed") from exc
        self.Generation = Generation
        self.TextGenerationRequest = TextGenerationRequest
        self.settings = settings
        os.environ.setdefault("DASHSCOPE_API_KEY", api_key)

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self.Generation.call(  # pragma: no cover - network call
            model=self.settings.model,
            prompt=prompt,
            temperature=self.settings.temperature,
            max_output_tokens=max_tokens,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Qwen summarization failed: {response}")
        return response.output.get("text", "").strip()


def create(settings: ProviderSettings):
    return QwenClient(settings)
