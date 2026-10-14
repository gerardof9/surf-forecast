"""Append-only immutable query snapshots."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from surf_forecast.hashing import sha256_json
from surf_forecast.paths import snapshots_dir
from surf_forecast.storage.atomic import write_json_atomic

SCHEMA_VERSION = "1.0.0"


class SnapshotError(RuntimeError):
    pass


def snapshot_id(created_at: datetime, canonical_hash: str) -> str:
    stamp = created_at.astimezone().strftime("%Y%m%dT%H%M%SZ")
    if created_at.utcoffset() is not None and created_at.utcoffset().total_seconds() != 0:
        stamp = created_at.astimezone().replace(tzinfo=None).strftime("%Y%m%dT%H%M%S") + "Z"
        from datetime import timezone

        stamp = created_at.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"q_{stamp}_{canonical_hash[:8]}"


def snapshot_path(identifier: str, created_at: datetime) -> Path:
    utc = created_at
    from datetime import timezone

    utc = created_at.astimezone(timezone.utc)
    return snapshots_dir() / utc.strftime("%Y") / utc.strftime("%m") / f"{identifier}.json"


def write_snapshot(payload: dict[str, Any], created_at: datetime) -> Path:
    identifier = payload["snapshot_id"]
    path = snapshot_path(identifier, created_at)
    try:
        write_json_atomic(path, payload, exclusive=True)
    except FileExistsError as exc:
        raise SnapshotError(f"snapshot already exists: {path}") from exc
    return path


def read_snapshot(identifier: str) -> dict[str, Any]:
    matches = list(snapshots_dir().glob(f"**/{identifier}.json"))
    if not matches:
        raise SnapshotError(f"snapshot not found: {identifier}")
    with matches[0].open(encoding="utf-8") as handle:
        return json.load(handle)


def latest_snapshot() -> dict[str, Any] | None:
    files = sorted(snapshots_dir().glob("**/*.json"))
    if not files:
        return None
    with files[-1].open(encoding="utf-8") as handle:
        return json.load(handle)


def canonical_result_hash(presentation: dict[str, Any]) -> str:
    body = {key: value for key, value in presentation.items() if key != "snapshot_id"}
    return sha256_json(body)
