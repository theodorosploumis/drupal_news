"""RSS reader for Drupal Aggregator."""
import feedparser
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.timebox import parse_date, is_within_timeframe
from utils.html_norm import strip_html_tags, clean_text, truncate_text
from cache_manager import CacheManager


def fetch_rss(
    rss_urls: List[str],
    since: datetime,
    timezone: str,
    cache: Optional[CacheManager] = None,
    timeout: int = 20,
    retries: int = 2,
    user_agent: str = "DrupalWeeklyBot/1.0"
) -> List[Dict[str, Any]]:
    """
    Fetch and normalize RSS feeds.

    Args:
        rss_urls: List of RSS feed URLs
        since: Datetime threshold for filtering items
        timezone: Timezone name
        cache: Optional cache manager
        timeout: HTTP timeout in seconds
        retries: Number of retry attempts
        user_agent: User agent string

    Returns:
        List of normalized items
    """
    items = []

    for url in rss_urls:
        try:
            # Check cache first
            if cache:
                cached = cache.get(url)
                if cached:
                    items.extend(cached.get("items", []))
                    continue

            # Fetch RSS feed
            headers = {"User-Agent": user_agent}
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.content)

            feed_items = []
            for entry in feed.entries:
                # Extract data
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                description = entry.get("description") or entry.get("summary", "")
                pub_date = entry.get("published") or entry.get("updated", "")

                if not title or not link:
                    continue

                # Parse and check date
                date_obj = parse_date(pub_date, timezone)
                if date_obj and not is_within_timeframe(date_obj, since, timezone):
                    continue

                # Clean description
                description = strip_html_tags(description)
                description = clean_text(description)
                description = truncate_text(description, 500)

                item = {
                    "title": title,
                    "url": link,
                    "description": description,
                    "date": date_obj.isoformat() if date_obj else pub_date,
                    "source_type": "rss",
                    "source_url": url,
                    "tags": [tag.get("term", "") for tag in entry.get("tags", [])]
                }

                feed_items.append(item)

            # Cache the results
            if cache and feed_items:
                cache.set(url, {"items": feed_items})

            items.extend(feed_items)

        except httpx.HTTPError as e:
            print(f"HTTP error fetching RSS {url}: {e}")
        except Exception as e:
            print(f"Error processing RSS {url}: {e}")

    return items


def parse_rss_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse RSS content directly (for testing).

    Args:
        content: Raw RSS XML content

    Returns:
        List of parsed items
    """
    feed = feedparser.parse(content)
    items = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        description = entry.get("description") or entry.get("summary", "")
        pub_date = entry.get("published") or entry.get("updated", "")

        if not title or not link:
            continue

        description = strip_html_tags(description)
        description = clean_text(description)

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": pub_date,
            "source_type": "rss"
        })

    return items
