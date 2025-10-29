"""Deduplication utilities for Drupal Aggregator."""
from typing import List, Dict, Any, Set
import hashlib
import json


def compute_hash(item: Dict[str, Any]) -> str:
    """Compute hash for an item based on URL and title."""
    url = item.get("url", "")
    title = item.get("title", "")
    content = f"{url}|{title}".lower().strip()
    return hashlib.sha256(content.encode()).hexdigest()


def dedupe_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate items based on URL and title.
    Returns unique items, preserving first occurrence.
    """
    seen_hashes: Set[str] = set()
    unique_items: List[Dict[str, Any]] = []

    for item in items:
        item_hash = compute_hash(item)
        if item_hash not in seen_hashes:
            seen_hashes.add(item_hash)
            unique_items.append(item)

    return unique_items


def dedupe_by_url(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate items based on URL only."""
    seen_urls: Set[str] = set()
    unique_items: List[Dict[str, Any]] = []

    for item in items:
        url = item.get("url", "").strip().lower()
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_items.append(item)
        elif not url:
            # Keep items without URLs
            unique_items.append(item)

    return unique_items


def merge_duplicates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge duplicate items, combining their data.
    Items with same URL get merged, keeping the most complete data.
    """
    url_map: Dict[str, Dict[str, Any]] = {}

    for item in items:
        url = item.get("url", "").strip()
        if not url:
            continue

        if url not in url_map:
            url_map[url] = item.copy()
        else:
            # Merge: prefer non-empty values
            existing = url_map[url]
            for key, value in item.items():
                if value and (not existing.get(key) or len(str(value)) > len(str(existing.get(key, "")))):
                    existing[key] = value

    return list(url_map.values())
