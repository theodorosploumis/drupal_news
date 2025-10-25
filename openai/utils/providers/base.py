from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class SummaryProvider(Protocol):
    def summarize(self, prompt: str, *, max_tokens: int | None = None) -> str:
        ...


@dataclass
class ProviderSettings:
    name: str
    model: str
    temperature: float = 0.2
    max_output_tokens: int | None = None
