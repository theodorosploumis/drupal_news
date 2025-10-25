from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter

import pytz
from dotenv import load_dotenv
from loguru import logger

from . import ai_summarizer
from . import data_cleaner
from . import metrics_collector
from . import pipeline_integrity
from . import rss_reader
from . import validator
from . import webpage_reader
from .cache_manager import CacheConfig, CacheManager
from .email_sender import (
    EmailSettings,
    build_body,
    build_email_subject,
    discover_email_settings,
    send_email,
)
from .markdown_converter import write_parsed_markdown, write_summary_markdown, write_summary_pdf
from .process_logger import get_logger
from utils import timebox
from utils.dedupe import ItemDict, dedupe_items
from utils.io_safe import write_json, write_text

EXIT_SUCCESS = 0
EXIT_PARTIAL_FETCH = 10
EXIT_VALIDATION_FAILED = 20
EXIT_SUMMARIZER_FAILED = 30
EXIT_EMAIL_FAILED = 40
EXIT_INTEGRITY_FAILED = 50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drupal Weekly Aggregator")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--email", choices=["yes", "no"], default="yes")
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--providers", type=Path, default=Path("providers.yaml"))
    parser.add_argument("--env", type=Path, default=Path(".env"))
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def determine_provider(args: argparse.Namespace, providers_path: Path) -> tuple[str, str | None]:
    providers_cfg = ai_summarizer._load_config(providers_path)  # reuse loader
    default = providers_cfg.get("default_provider", "openai")
    provider = args.provider or default
    model_override = args.model
    return provider, model_override


def prepare_run_directory(root: Path, timezone: str) -> Path:
    tz = pytz.timezone(timezone)
    today = datetime.now(tz).strftime("%Y-%m-%d")
    run_dir = root / today
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def main() -> None:
    args = parse_args()
    load_dotenv(args.env)
    env = os.environ.copy()

    config = load_config(args.config)
    timezone = env.get("TIMEZONE", "Europe/Athens")
    provider_name, model_override = determine_provider(args, args.providers)
    days = args.days or config.get("timeframe_days", 7)

    run_root = (args.outdir or Path(config.get("run_root", "runs"))).resolve()
    run_dir = prepare_run_directory(run_root, timezone)
    get_logger(run_dir)
    logger.info("[index] start provider={} model={} days={}", provider_name, model_override, days)

    cache_cfg = CacheConfig(
        db_path=Path(env.get("CACHE_DB_PATH", "./cache/cache.db")),
        ttl_days=int(env.get("CACHE_TTL_DAYS", "21")),
    )
    cache = CacheManager(cache_cfg)

    http_cfg = rss_reader.HTTPConfig(**config.get("http", {}))

    window = timebox.get_time_window(days, timezone)

    items: list[ItemDict] = []
    exit_code = EXIT_SUCCESS
    start_time = perf_counter()

    try:
        rss_items = rss_reader.fetch_rss(config["sources"]["rss"], window, http_cfg, cache, timezone)
        page_items = webpage_reader.fetch_pages(config["sources"]["pages"], window, http_cfg, cache, timezone)
        items = dedupe_items(rss_items + page_items)
    except Exception as exc:
        logger.error("[index] fetch failure: {}", exc)
        exit_code = EXIT_PARTIAL_FETCH

    write_json(run_dir / "sources.json", items)

    try:
        validation_report = validator.validate_items(items)
        validator.write_report(run_dir / "validation_report.json", validation_report)
    except validator.ValidationError as exc:
        logger.error("[index] validation failed: {}", exc)
        exit_code = EXIT_VALIDATION_FAILED

    write_parsed_markdown(run_dir / "parsed.md", items, window.start, window.end, timezone)

    summary = ""
    summary_md_path = run_dir / "summary.md"
    summary_pdf_path: Path | None = run_dir / "summary.pdf"
    try:
        summary = ai_summarizer.summarize(
            items,
            provider_name,
            model_override=model_override,
            providers_config_path=args.providers,
            timezone=timezone,
            days=days,
            dry_run=args.dry_run,
        )
        write_summary_markdown(summary_md_path, summary)
        try:
            write_summary_pdf(summary_pdf_path, summary)
        except Exception as exc:
            logger.warning("[index] pdf generation failed: {}", exc)
            summary_pdf_path = None
    except Exception as exc:  # pragma: no cover - safety net
        logger.error("[index] summarizer failed: {}", exc)
        exit_code = EXIT_SUMMARIZER_FAILED

    tz = pytz.timezone(timezone)
    generated_at = datetime.now(tz)
    report_date = generated_at.strftime("%Y-%m-%d")

    email_settings = discover_email_settings(env, config.get("email", {}).get("attach_summary", True))
    subject_prefix = config.get("email", {}).get("subject_prefix", "[Drupal Weekly]")
    subject = build_email_subject(subject_prefix, report_date)
    body = build_body(report_date, generated_at.strftime("%H:%M (%Z)"))
    email_manifest = f"Subject: {subject}\nTo: {email_settings.mail_to}\nFrom: {email_settings.mail_from}\n\n{body}\n"
    write_text(run_dir / "email.txt", email_manifest)

    if args.email == "yes" and exit_code in (EXIT_SUCCESS, EXIT_PARTIAL_FETCH):
        try:
            if not email_settings.host or not email_settings.mail_to:
                raise RuntimeError("Email settings incomplete")
            send_email(
                email_settings,
                subject,
                body,
                summary_md_path,
                summary,
                summary_pdf_path,
            )
        except Exception as exc:
            logger.error("[index] email failed: {}", exc)
            exit_code = EXIT_EMAIL_FAILED

    duration = perf_counter() - start_time
    metrics_collector.record_metrics(
        run_dir / "metrics.json",
        provider=provider_name,
        model=model_override or "default",
        timezone=timezone,
        items=items,
        summary=summary,
        duration_seconds=duration,
        tokens_used=None,
        exit_code=exit_code,
    )

    try:
        data_cleaner.run_cleanup(
            run_root=run_root,
            log_dir=run_root,
            cache=cache,
            timezone=timezone,
            run_retention_days=int(env.get("RUN_RETENTION_DAYS", "90")),
            log_retention_days=int(env.get("LOG_RETENTION_DAYS", "45")),
            cache_ttl_days=cache_cfg.ttl_days,
            compress_after_days=max(7, cache_cfg.ttl_days // 2),
        )
    except Exception as exc:
        logger.warning("[index] cleanup issue: {}", exc)

    cache.close()

    if not pipeline_integrity.verify_run(run_dir):
        exit_code = EXIT_INTEGRITY_FAILED

    logger.info("[index] exit={} duration={:.2f}s items={}", exit_code, duration, len(items))
    sys.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover
    main()
