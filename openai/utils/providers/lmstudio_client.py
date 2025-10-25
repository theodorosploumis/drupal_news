from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import ProviderSettings


class LMStudioClient:
    def __init__(self, settings: ProviderSettings) -> None:
        base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
        self._endpoint = base_url.rstrip("/") + "/v1/chat/completions"
        self._client = httpx.Client(timeout=60)
        self.settings = settings

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self._client.post(
            self._endpoint,
            json={
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": "You summarize Drupal news into Markdown."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.settings.temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()


def create(settings: ProviderSettings):
    return LMStudioClient(settings)
