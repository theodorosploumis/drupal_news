from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Sequence

import pytz

from utils.dedupe import ItemDict
from utils.io_safe import write_json


def record_metrics(
    path: Path,
    *,
    provider: str,
    model: str,
    timezone: str,
    items: Sequence[ItemDict],
    summary: str,
    duration_seconds: float,
    tokens_used: int | None,
    exit_code: int,
) -> None:
    tz = pytz.timezone(timezone)
    payload = {
        "timestamp": datetime.now(tz).isoformat(),
        "provider": provider,
        "model": model,
        "duration_s": duration_seconds,
        "items_total": len(items),
        "rss_count": sum(1 for item in items if item.get("kind") == "rss"),
        "page_count": sum(1 for item in items if item.get("kind") != "rss"),
        "summary_length": len(summary.split()),
        "tokens_used": tokens_used,
        "exit_code": exit_code,
    }
    write_json(path, payload)
