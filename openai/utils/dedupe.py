from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple, TypedDict


class ItemDict(TypedDict, total=False):
    url: str
    guid: str
    title: str
    summary: str
    category: str
    kind: str


def dedupe_items(items: Sequence[ItemDict]) -> List[ItemDict]:
    seen: set[Tuple[str, str]] = set()
    deduped: List[ItemDict] = []
    for item in items:
        key = (item.get("guid") or "", item.get("url") or "")
        if key[1] == "":
            key = (key[0], item.get("title", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
