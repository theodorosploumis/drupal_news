from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import ProviderSettings


class OllamaClient:
    def __init__(self, settings: ProviderSettings) -> None:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._endpoint = base_url.rstrip("/") + "/api/generate"
        self._client = httpx.Client(timeout=60)
        self.settings = settings

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self._client.post(
            self._endpoint,
            json={
                "model": self.settings.model,
                "prompt": prompt,
                "options": {"temperature": self.settings.temperature},
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()


def create(settings: ProviderSettings):
    return OllamaClient(settings)
