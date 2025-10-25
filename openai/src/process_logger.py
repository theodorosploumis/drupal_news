from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger


class ProcessLogger:
    """Configures loguru logger to emit both console and run scoped logs."""

    def __init__(self, run_dir: Path, level: str = "INFO") -> None:
        self._run_dir = run_dir
        self._log_path = run_dir / "run.log"
        self._configured = False
        self._level = level

    def configure(self) -> None:
        if self._configured:
            return
        self._run_dir.mkdir(parents=True, exist_ok=True)
        logger.remove()
        logger.add(lambda msg: print(msg, end=""), level=self._level)
        logger.add(self._log_path, level=self._level, enqueue=True, backtrace=False, diagnose=False)
        self._configured = True

    @property
    def path(self) -> Path:
        return self._log_path

    def get(self):  # pragma: no cover - thin wrapper
        self.configure()
        return logger


def get_logger(run_dir: Path, level: str = "INFO"):
    plogger = ProcessLogger(run_dir, level)
    plogger.configure()
    return logger
