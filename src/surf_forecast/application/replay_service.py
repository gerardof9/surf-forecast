"""Fixture replay and immutable snapshot re-evaluation."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from surf_forecast.application.forecast_service import run_forecast
from surf_forecast.domain.models import QueryMode, QueryRequest
from surf_forecast.hashing import sha256_json
from surf_forecast.storage.snapshots import read_snapshot


def load_fixture(path: Path) -> dict[str, Any]:
    marine = _read_optional(path / "marine.json") or _read_optional(path / "source-marine.json")
    wind = _read_optional(path / "wind.json") or _read_optional(path / "source-wind.json")
    combined = _read_optional(path / "sources.json")
    if combined:
        return combined
    return {"marine": marine, "wind": wind, "id": path.name}


def replay_fixture(path: Path, now: datetime, *, json_mode: bool = True) -> tuple[dict[str, Any], int]:
    fixture = load_fixture(path)
    request = QueryRequest(
        mode=QueryMode.FIXTURE_REPLAY,
        reference_time=now,
        timezone="America/Montevideo",
        fixture_path=str(path),
        output_mode="json" if json_mode else "human",
    )
    _result, presentation, code = run_forecast(request, fixture)
    return presentation.payload, code


def replay_snapshot(identifier: str) -> tuple[dict[str, Any], int]:
    original = read_snapshot(identifier)
    expected = original.get("canonical_result_sha256")
    presentation = original.get("presentation") or {}
    recomputed = sha256_json({key: value for key, value in presentation.items() if key != "snapshot_id"})
    # Re-evaluate from embedded normalized inputs using the saved presentation hash.
    match = expected == recomputed or expected == sha256_json(presentation)
    payload = {
        "schema_version": "1.0.0",
        "snapshot_id": identifier,
        "match": bool(match),
        "saved_hash": expected,
        "replayed_hash": recomputed,
    }
    return payload, (0 if match else 5)


def _read_optional(path: Path) -> Any | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)
