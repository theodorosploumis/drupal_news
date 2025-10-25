from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import feedparser
import httpx
from loguru import logger

from .cache_manager import CacheManager
from utils import timebox
from utils.dedupe import ItemDict
from utils.html_norm import strip_markdown_unfriendly_chars


@dataclass
class HTTPConfig:
    timeout_sec: int = 20
    retries: int = 2
    ua: str = "DrupalWeeklyBot/1.0"


def _normalize_entry(entry: feedparser.FeedParserDict, source_url: str) -> ItemDict:
    tags = [t["term"] for t in entry.get("tags", []) if "term" in t]
    authors = [author.get("name") for author in entry.get("authors", []) if author.get("name")]
    summary = entry.get("summary", "")
    item: ItemDict = ItemDict(
        title=strip_markdown_unfriendly_chars(entry.get("title", "Untitled")),
        url=entry.get("link", source_url),
        summary=strip_markdown_unfriendly_chars(summary),
        published=entry.get("published", entry.get("updated", "")),
        guid=entry.get("id", entry.get("guid", entry.get("link", ""))),
        source=source_url,
        kind="rss",
    )
    if tags:
        item["category"] = ", ".join(tags)
    if authors:
        item["authors"] = authors
    return item


def fetch_rss(urls: Sequence[str], window: timebox.TimeWindow, http_cfg: HTTPConfig, cache: CacheManager, timezone: str) -> List[ItemDict]:
    collected: List[ItemDict] = []
    client = httpx.Client(timeout=http_cfg.timeout_sec, headers={"User-Agent": http_cfg.ua})
    for url in urls:
        logger.info("[rss_reader] fetch url={}", url)
        cached = cache.get(url, timezone)
        if cached:
            entries_data = cached.get("entries", [])
        else:
            response = client.get(url)
            response.raise_for_status()
            parsed = feedparser.parse(response.text)
            entries_data = [dict(entry) for entry in parsed.entries]
            cache.set(url, {"entries": entries_data}, timezone)
        for entry_dict in entries_data:
            entry = feedparser.FeedParserDict(entry_dict)
            normalized = _normalize_entry(entry, url)
            published = normalized.get("published")
            if not published:
                continue
            try:
                dt = timebox.parse_datetime(published, timezone)
            except Exception:
                continue
            if window.contains(dt) and normalized.get("url"):
                collected.append(normalized)
    return collected
