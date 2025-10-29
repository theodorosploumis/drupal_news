"""Webpage reader and scraper for Drupal Aggregator."""
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.timebox import parse_date, is_within_timeframe
from utils.html_norm import strip_html_tags, clean_text, truncate_text, extract_links
from cache_manager import CacheManager


def fetch_pages(
    page_urls: List[str],
    since: datetime,
    timezone: str,
    cache: Optional[CacheManager] = None,
    timeout: int = 20,
    retries: int = 2,
    user_agent: str = "DrupalWeeklyBot/1.0"
) -> List[Dict[str, Any]]:
    """
    Fetch and scrape web pages for news items.

    Args:
        page_urls: List of page URLs to scrape
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

    for url in page_urls:
        try:
            # Check cache first
            if cache:
                cached = cache.get(url)
                if cached:
                    items.extend(cached.get("items", []))
                    continue

            # Fetch page
            headers = {"User-Agent": user_agent}
            response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
            response.raise_for_status()

            # Parse based on URL pattern
            if "drupal.org/news" in url:
                page_items = parse_drupal_news(response.text, url, since, timezone)
            elif "drupal.org/planet" in url:
                page_items = parse_drupal_planet(response.text, url, since, timezone)
            elif "drupal.org/project/drupal/releases" in url:
                page_items = parse_drupal_releases(response.text, url, since, timezone)
            else:
                page_items = parse_generic_page(response.text, url, since, timezone)

            # Cache the results
            if cache and page_items:
                cache.set(url, {"items": page_items})

            items.extend(page_items)

        except httpx.HTTPError as e:
            print(f"HTTP error fetching page {url}: {e}")
        except Exception as e:
            print(f"Error processing page {url}: {e}")

    return items


def parse_drupal_news(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/news page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find news articles
    articles = soup.find_all("article") or soup.find_all("div", class_=["node", "view-content"])

    for article in articles[:20]:  # Limit to recent items
        # Extract title and link
        title_tag = article.find("h2") or article.find("h3")
        if not title_tag:
            continue

        link_tag = title_tag.find("a") or article.find("a")
        if not link_tag or not link_tag.get("href"):
            continue

        title = clean_text(title_tag.get_text())
        link = link_tag["href"]

        # Make absolute URL
        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract description
        description = ""
        desc_tag = article.find("div", class_="field--name-body") or article.find("p")
        if desc_tag:
            description = truncate_text(clean_text(desc_tag.get_text()), 500)

        # Extract date
        date_tag = article.find("time") or article.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["news"]
        })

    return items


def parse_drupal_planet(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/planet page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find planet entries
    entries = soup.find_all("article") or soup.find_all("div", class_="view-content")

    for entry in entries[:20]:
        title_tag = entry.find("h2") or entry.find("h3")
        if not title_tag:
            continue

        link_tag = title_tag.find("a")
        if not link_tag or not link_tag.get("href"):
            continue

        title = clean_text(title_tag.get_text())
        link = link_tag["href"]

        # Make absolute URL if needed
        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract description
        description = ""
        desc_tag = entry.find("div", class_="content") or entry.find("p")
        if desc_tag:
            description = truncate_text(clean_text(desc_tag.get_text()), 500)

        # Extract date
        date_tag = entry.find("time") or entry.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["planet"]
        })

    return items


def parse_drupal_releases(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Parse drupal.org/project/drupal/releases page."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Find release entries
    releases = soup.find_all("div", class_=["view-project-release-by-project", "views-row"])

    for release in releases[:15]:
        # Extract version
        version_tag = release.find("h2") or release.find("span", class_="field--name-field-release-version")
        if not version_tag:
            continue

        version = clean_text(version_tag.get_text())
        title = f"Drupal {version}"

        # Extract link
        link_tag = release.find("a", href=True)
        link = link_tag["href"] if link_tag else source_url

        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        # Extract date
        date_tag = release.find("time") or release.find("span", class_="date")
        date_str = date_tag.get("datetime", "") or date_tag.get_text() if date_tag else ""

        date_obj = parse_date(date_str, timezone) if date_str else None
        if date_obj and not is_within_timeframe(date_obj, since, timezone):
            continue

        # Description
        desc_tag = release.find("div", class_="field--name-body")
        description = truncate_text(clean_text(desc_tag.get_text()), 500) if desc_tag else f"Drupal {version} release"

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": date_obj.isoformat() if date_obj else "",
            "source_type": "page",
            "source_url": source_url,
            "tags": ["release", "core"]
        })

    return items


def parse_generic_page(html: str, source_url: str, since: datetime, timezone: str) -> List[Dict[str, Any]]:
    """Generic page parser."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    # Extract all article or content blocks
    articles = soup.find_all(["article", "div"], class_=lambda x: x and "content" in x.lower())

    for article in articles[:10]:
        title_tag = article.find(["h1", "h2", "h3"])
        if not title_tag:
            continue

        title = clean_text(title_tag.get_text())
        link_tag = article.find("a", href=True)
        link = link_tag["href"] if link_tag else source_url

        if link.startswith("/"):
            link = "https://www.drupal.org" + link

        description_tag = article.find("p")
        description = truncate_text(clean_text(description_tag.get_text()), 500) if description_tag else ""

        items.append({
            "title": title,
            "url": link,
            "description": description,
            "date": "",
            "source_type": "page",
            "source_url": source_url,
            "tags": []
        })

    return items
