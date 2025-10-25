from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import pytz


@dataclass
class CacheConfig:
    db_path: Path
    ttl_days: int


class CacheManager:
    def __init__(self, config: CacheConfig) -> None:
        self.config = config
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.config.db_path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                fetched_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def get(self, url: str, timezone: str) -> Optional[dict[str, Any]]:
        cursor = self._conn.execute("SELECT fetched_at, payload FROM cache WHERE url = ?", (url,))
        row = cursor.fetchone()
        if not row:
            return None
        fetched_at = datetime.fromisoformat(row[0])
        cutoff = datetime.now(pytz.timezone(timezone)) - timedelta(days=self.config.ttl_days)
        if fetched_at < cutoff:
            self.delete(url)
            return None
        return json.loads(row[1])

    def set(self, url: str, payload: dict[str, Any], timezone: str) -> None:
        timestamp = datetime.now(pytz.timezone(timezone)).isoformat()
        self._conn.execute(
            "REPLACE INTO cache (url, fetched_at, payload) VALUES (?, ?, ?)",
            (url, timestamp, json.dumps(payload)),
        )
        self._conn.commit()

    def delete(self, url: str) -> None:
        self._conn.execute("DELETE FROM cache WHERE url = ?", (url,))
        self._conn.commit()

    def purge_older_than(self, days: int, timezone: str) -> int:
        cutoff = datetime.now(pytz.timezone(timezone)) - timedelta(days=days)
        cur = self._conn.execute("DELETE FROM cache WHERE fetched_at < ?", (cutoff.isoformat(),))
        self._conn.commit()
        return cur.rowcount
