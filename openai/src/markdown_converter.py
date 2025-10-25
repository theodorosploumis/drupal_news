from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from markdown import markdown
from weasyprint import HTML

from utils.dedupe import ItemDict
from utils.io_safe import ensure_parent, write_text


def _format_rss_table(items: Iterable[ItemDict]) -> str:
    lines = ["| URL | Name | Short description |", "| --- | --- | --- |"]
    for item in items:
        url = item.get("url", "")
        title = item.get("title", "")
        summary = item.get("summary", "")[:180]
        lines.append(f"| [{title}]({url}) | {title} | {summary} |")
    return "\n".join(lines)


def _format_page_section(items: Iterable[ItemDict]) -> str:
    lines = []
    for item in items:
        title = item.get("title", "")
        url = item.get("url", "")
        summary = item.get("summary", "")
        lines.append(f"- [{title}]({url}) — {summary}")
    return "\n".join(lines)


def build_parsed_markdown(items: List[ItemDict], window_start: datetime, window_end: datetime, timezone: str) -> str:
    rss_items = [item for item in items if item.get("kind") == "rss"]
    page_items = [item for item in items if item.get("kind") != "rss"]
    lines = [
        "# Drupal Weekly Raw Collection",
        "",
        f"Timeframe: {window_start.isoformat()} to {window_end.isoformat()} ({timezone})",
        f"Total items: {len(items)}",
        "",
        "## RSS Feeds",
    ]
    if rss_items:
        lines.append(_format_rss_table(rss_items))
    else:
        lines.append("No RSS items collected.")
    lines.append("")
    lines.append("## Site Crawls")
    if page_items:
        lines.append(_format_page_section(page_items))
    else:
        lines.append("No on-site articles collected.")
    lines.append("")
    return "\n".join(lines)


def write_parsed_markdown(path: Path, items: List[ItemDict], window_start: datetime, window_end: datetime, timezone: str) -> None:
    content = build_parsed_markdown(items, window_start, window_end, timezone)
    write_text(path, content)


def write_summary_markdown(path: Path, summary: str) -> None:
    write_text(path, summary)


def write_summary_pdf(path: Path, summary: str) -> None:
    ensure_parent(path)
    html = markdown(summary, extensions=["tables"])  # type: ignore[arg-type]
    HTML(string=html).write_pdf(path)
