from __future__ import annotations

from pathlib import Path

from loguru import logger


REQUIRED_FILES = [
    "parsed.md",
    "summary.md",
    "summary.pdf",
    "sources.json",
    "validation_report.json",
    "metrics.json",
    "run.log",
]


def verify_run(run_dir: Path) -> bool:
    ok = True
    for filename in REQUIRED_FILES:
        path = run_dir / filename
        if not path.exists() or path.stat().st_size == 0:
            logger.error("[pipeline_integrity] missing file {}", path)
            ok = False
    return ok
