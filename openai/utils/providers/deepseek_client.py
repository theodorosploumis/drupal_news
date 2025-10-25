from __future__ import annotations

import os
from typing import Optional

import httpx

from .base import ProviderSettings


class DeepSeekClient:
    def __init__(self, settings: ProviderSettings) -> None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not configured")
        self._client = httpx.Client(
            base_url="https://api.deepseek.com",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        self.settings = settings

    def summarize(self, prompt: str, *, max_tokens: Optional[int] = None) -> str:
        response = self._client.post(
            "/chat/completions",
            json={
                "model": self.settings.model,
                "messages": [
                    {"role": "system", "content": "You produce concise Drupal news markdown summaries with references."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": self.settings.temperature,
                "max_tokens": max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()


def create(settings: ProviderSettings):
    return DeepSeekClient(settings)
