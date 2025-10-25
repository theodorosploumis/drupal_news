from __future__ import annotations

import os
from typing import Optional

from .base import ProviderSettings


class AnthropicClient:
    def __init__(self, settings: ProviderSettings) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not configured")
        try:  # pragma: no cover - optional dependency
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("anthropic package not installed") from exc
        self._client = anthropic.Anthropic(api_key=api_key)
        self.settings = settings

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self._client.messages.create(  # pragma: no cover - network call
            model=self.settings.model,
            max_tokens=max_tokens or 1024,
            temperature=self.settings.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text")).strip()


def create(settings: ProviderSettings):
    return AnthropicClient(settings)
