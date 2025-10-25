from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


def fallback_summary(headers: Iterable[str]) -> str:
    lines = "\n".join(f"- {title}" for title in headers)
    return (
        "Automated fallback summary (LLM unavailable).\n\n"
        "Key highlights:\n"
        f"{lines if lines else '- No qualifying items collected.'}"
    )
