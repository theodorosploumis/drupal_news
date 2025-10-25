from __future__ import annotations

import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import pytz
from loguru import logger

from .cache_manager import CacheManager


def _iter_run_dirs(run_root: Path) -> Iterable[Path]:
    if not run_root.exists():
        return []
    return [p for p in run_root.iterdir() if p.is_dir()]


def clean_runs(run_root: Path, timezone: str, retention_days: int, compress_after_days: int) -> None:
    tz = pytz.timezone(timezone)
    today = datetime.now(tz).date()
    for run_dir in _iter_run_dirs(run_root):
        try:
            run_date = datetime.strptime(run_dir.name, "%Y-%m-%d").date()
        except ValueError:
            logger.debug("[data_cleaner] skipping non-date directory {}", run_dir)
            continue
        age_days = (today - run_date).days
        if age_days > retention_days:
            shutil.rmtree(run_dir, ignore_errors=True)
            archive_path = run_dir.with_suffix(".tar.gz")
            if archive_path.exists():
                archive_path.unlink()
            logger.info("[data_cleaner] removed run {}", run_dir)
        elif age_days > compress_after_days:
            archive_path = run_dir.with_suffix(".tar.gz")
            if not archive_path.exists():
                shutil.make_archive(str(run_dir), "gztar", root_dir=run_dir)
                shutil.rmtree(run_dir, ignore_errors=True)
                logger.info("[data_cleaner] archived run {}", archive_path)


def clean_logs(log_dir: Path, retention_days: int) -> None:
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    for log_file in log_dir.rglob("*.log"):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
            log_file.unlink(missing_ok=True)
            logger.info("[data_cleaner] deleted log {}", log_file)


def purge_cache(cache: CacheManager, timezone: str, ttl_days: int) -> int:
    removed = cache.purge_older_than(ttl_days, timezone)
    logger.info("[data_cleaner] purged {} cache entries", removed)
    return removed


def run_cleanup(
    *,
    run_root: Path,
    log_dir: Path,
    cache: CacheManager,
    timezone: str,
    run_retention_days: int,
    log_retention_days: int,
    cache_ttl_days: int,
    compress_after_days: int,
) -> None:
    clean_runs(run_root, timezone, run_retention_days, compress_after_days)
    clean_logs(log_dir, log_retention_days)
    purge_cache(cache, timezone, cache_ttl_days)
