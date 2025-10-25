from __future__ import annotations

from bs4 import BeautifulSoup
from readability import Document


def extract_readable_html(content: str) -> str:
    doc = Document(content)
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def strip_markdown_unfriendly_chars(text: str) -> str:
    return text.replace("|", "-")
