from __future__ import annotations

from typing import List, Sequence, TYPE_CHECKING
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from .cache_manager import CacheManager
from utils import timebox
from utils.dedupe import ItemDict
from utils.html_norm import extract_readable_html, strip_markdown_unfriendly_chars

if TYPE_CHECKING:  # pragma: no cover
    from .rss_reader import HTTPConfig

class PageFetchError(RuntimeError):
    pass


def _extract_entries(html: str, base_url: str) -> List[ItemDict]:
    soup = BeautifulSoup(html, "lxml")
    results: List[ItemDict] = []
    for article in soup.select("article"):
        link = article.find("a", href=True)
        if not link:
            continue
        url = urljoin(base_url, link["href"])
        title = strip_markdown_unfriendly_chars(link.get_text(strip=True)) or "Untitled"
        time_tag = article.find("time")
        published = None
        if time_tag:
            published = time_tag.get("datetime") or time_tag.get_text(strip=True)
        summary = extract_readable_html(str(article))
        results.append(
            ItemDict(
                title=title,
                url=url,
                summary=summary,
                published=published,
                source=base_url,
                guid=url,
                kind="page",
            )
        )
    return results


def fetch_pages(urls: Sequence[str], window: timebox.TimeWindow, http_cfg: "HTTPConfig", cache: CacheManager, timezone: str) -> List[ItemDict]:

    items: List[ItemDict] = []
    client = httpx.Client(timeout=http_cfg.timeout_sec, headers={"User-Agent": http_cfg.ua})
    for url in urls:
        logger.info("[webpage_reader] fetch url={}", url)
        cached = cache.get(url, timezone)
        if cached:
            html = cached.get("html", "")
            entries = cached.get("entries")
            if entries is None:
                entries = _extract_entries(html, url)
        else:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
            entries = _extract_entries(html, url)
            cache.set(url, {"html": html, "entries": entries}, timezone)
        for entry in entries:
            published = entry.get("published")
            if not published:
                continue
            try:
                dt = timebox.parse_datetime(published, timezone)
            except Exception:
                continue
            if window.contains(dt):
                items.append(entry)
    return items
