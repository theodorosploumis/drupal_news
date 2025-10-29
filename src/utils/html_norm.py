"""HTML normalization utilities for Drupal Aggregator."""
import re
from typing import Optional
from bs4 import BeautifulSoup, NavigableString
from readability import Document


def strip_html_tags(html: str) -> str:
    """Remove all HTML tags and return plain text."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator=" ", strip=True)


def extract_main_content(html: str) -> str:
    """Extract main content from HTML using readability."""
    try:
        doc = Document(html)
        content_html = doc.summary()
        return strip_html_tags(content_html)
    except Exception:
        return strip_html_tags(html)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with single newline
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = normalize_whitespace(text)
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text.strip()


def extract_links(html: str, base_url: Optional[str] = None) -> list:
    """Extract all links from HTML."""
    soup = BeautifulSoup(html, "lxml")
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        text = a_tag.get_text(strip=True)

        # Make absolute URLs if base_url provided
        if base_url and href.startswith("/"):
            href = base_url.rstrip("/") + href

        if href and not href.startswith("#"):
            links.append({"url": href, "text": text})

    return links


def html_to_markdown_simple(html: str) -> str:
    """Convert simple HTML to Markdown."""
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    # Replace common tags
    for tag in soup.find_all("strong"):
        tag.replace_with(f"**{tag.get_text()}**")

    for tag in soup.find_all("em"):
        tag.replace_with(f"*{tag.get_text()}*")

    for tag in soup.find_all("code"):
        tag.replace_with(f"`{tag.get_text()}`")

    for tag in soup.find_all("a", href=True):
        text = tag.get_text()
        href = tag["href"]
        tag.replace_with(f"[{text}]({href})")

    return clean_text(soup.get_text())


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rstrip() + suffix


def is_drupal_url(url: str) -> bool:
    """Check if URL is from drupal.org domain."""
    return "drupal.org" in url.lower()
