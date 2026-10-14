"""Replaceable raw JSON cache with a 3-hour freshness TTL."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from surf_forecast.domain.models import CacheState
from surf_forecast.hashing import sha256_json
from surf_forecast.paths import cache_dir
from surf_forecast.storage.atomic import write_json_atomic

FRESH_MINUTES = 180


def cache_key(source_id: str, extra: dict[str, Any]) -> str:
    return sha256_json({"source_id": source_id, **extra})[:24]


def cache_path(key: str) -> Path:
    return cache_dir() / f"{key}.json"


def read_entry(key: str) -> dict[str, Any] | None:
    path = cache_path(key)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_entry(key: str, payload: dict[str, Any]) -> None:
    write_json_atomic(cache_path(key), payload)


def classify_age(fetched_at: datetime, now: datetime, fresh_minutes: int = FRESH_MINUTES) -> CacheState:
    age = now - fetched_at
    if age < timedelta(minutes=fresh_minutes):
        return CacheState.FRESH
    return CacheState.STALE


def parse_utc(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
