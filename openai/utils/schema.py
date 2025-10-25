from __future__ import annotations

ITEM_SCHEMA = {
    "type": "object",
    "required": ["title", "url", "published", "source"],
    "properties": {
        "title": {"type": "string", "minLength": 5},
        "url": {"type": "string", "format": "uri"},
        "published": {"type": "string"},
        "summary": {"type": "string"},
        "source": {"type": "string"},
        "category": {"type": "string"},
        "authors": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
}

SOURCES_SCHEMA = {
    "type": "array",
    "items": ITEM_SCHEMA,
}
