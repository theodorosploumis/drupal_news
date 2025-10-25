from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drupal Weekly scheduler")
    parser.add_argument("--every", default="friday", help="Weekday to run (e.g. friday)")
    parser.add_argument("--hour", type=int, default=9)
    parser.add_argument("--minute", type=int, default=5)
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default=None)
    parser.add_argument("--email", choices=["yes", "no"], default="yes")
    parser.add_argument("--days", type=int, default=7)
    return parser.parse_args()


def _launch_job(provider: str, model: str | None, email: str, days: int) -> None:
    cmd = [
        sys.executable,
        "-m",
        "src.index",
        "--provider",
        provider,
        "--email",
        email,
        "--days",
        str(days),
    ]
    if model:
        cmd.extend(["--model", model])
    logger.info("[scheduler] running {}", " ".join(cmd))
    subprocess.run(cmd, check=False)


def main() -> None:
    args = _parse_args()
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        _launch_job,
        "cron",
        day_of_week=args.every,
        hour=args.hour,
        minute=args.minute,
        args=[args.provider, args.model, args.email, args.days],
        id="drupal-weekly-job",
        replace_existing=True,
    )
    logger.info(
        "[scheduler] scheduled for {} at {:02d}:{:02d} (UTC)",
        args.every,
        args.hour,
        args.minute,
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):  # pragma: no cover
        logger.info("[scheduler] stopped at {}", datetime.utcnow().isoformat())


if __name__ == "__main__":  # pragma: no cover
    main()
