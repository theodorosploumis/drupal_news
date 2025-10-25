from __future__ import annotations

from typing import Dict, List, Sequence
from urllib.parse import urlparse

from jsonschema import Draft7Validator
from loguru import logger

from utils.dedupe import ItemDict
from pathlib import Path

from utils.io_safe import write_json
from utils.schema import SOURCES_SCHEMA


class ValidationError(RuntimeError):
    pass


def validate_items(items: Sequence[ItemDict]) -> Dict[str, int | bool]:
    validator = Draft7Validator(SOURCES_SCHEMA)
    errors = list(validator.iter_errors(list(items)))
    invalid_urls = 0
    missing_links = 0

    for item in items:
        url = item.get("url") or ""
        parsed = urlparse(url)
        if not (parsed.scheme and parsed.netloc):
            invalid_urls += 1
        if not url:
            missing_links += 1

    if errors:
        for err in errors:
            logger.error("[validator] schema error: {}", err)

    report = {
        "rss_count": sum(1 for item in items if item.get("kind") == "rss"),
        "page_count": sum(1 for item in items if item.get("kind") != "rss"),
        "missing_links": missing_links,
        "invalid_urls": invalid_urls,
        "passed": not errors and invalid_urls == 0 and missing_links == 0,
    }

    if not report["passed"]:
        raise ValidationError(f"Validation failed: {report}")
    return report


def write_report(path: Path, report: Dict[str, int | bool]) -> None:
    write_json(path, report)
