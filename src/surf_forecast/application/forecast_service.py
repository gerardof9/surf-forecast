"""Orchestrate acquisition, evaluation, and snapshot persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from surf_forecast import __version__
from surf_forecast.application.profile_service import list_profiles
from surf_forecast.domain.evaluation import evaluate_forecast
from surf_forecast.domain.models import (
    ForecastResult,
    OverallStatus,
    QueryMode,
    QueryRequest,
    FetchStatus,
)
from surf_forecast.domain.presentation import ForecastPresentation, build_presentation
from surf_forecast.hashing import sha256_json
from surf_forecast.sources.base import AcquisitionResult
from surf_forecast.sources.open_meteo import OpenMeteoAdapter
from surf_forecast.storage.config import load_criteria
from surf_forecast.storage.snapshots import (
    SCHEMA_VERSION,
    canonical_result_hash,
    latest_snapshot,
    read_snapshot,
    snapshot_id,
    write_snapshot,
)


class ForecastUnavailable(RuntimeError):
    pass


class PersistenceError(RuntimeError):
    pass


def run_forecast(request: QueryRequest, fixture: dict[str, Any] | None = None) -> tuple[ForecastResult, ForecastPresentation, int]:
    criteria = load_criteria()
    profiles = list_profiles()
    adapter = OpenMeteoAdapter(fixture)
    acquisition = adapter.acquire(
        request.reference_time,
        force_refresh=request.mode is QueryMode.FORCE_REFRESH,
        stored_only=request.mode is QueryMode.STORED_ONLY,
    )
    if not acquisition.marine_hours and not acquisition.wind_hours:
        raise ForecastUnavailable("forecast_unavailable")
    groups = {item.independence_group for item in acquisition.descriptors}
    days = evaluate_forecast(
        request=request,
        criteria=criteria,
        profiles=profiles,
        marine_hours=acquisition.marine_hours,
        wind_hours=acquisition.wind_hours,
        fetches=acquisition.fetches,
        independence_groups=groups,
    )
    overall = OverallStatus.COMPLETE
    if any(fetch.status in {FetchStatus.FAILED, FetchStatus.STALE_CACHE} for fetch in acquisition.fetches):
        overall = OverallStatus.DEGRADED
    if any(day.state.value == "incomplete_forecast" for day in days):
        overall = OverallStatus.DEGRADED
    created = datetime.now(timezone.utc)
    result = ForecastResult(
        overall_status=overall,
        snapshot_id="pending",
        request=request,
        criteria=criteria,
        days=days,
        profiles=profiles,
        sources=acquisition.fetches,
        descriptors=acquisition.descriptors,
        incidents=acquisition.incidents,
        marine_hours=acquisition.marine_hours,
        wind_hours=acquisition.wind_hours,
        attribution={},
    )
    presentation = build_presentation(result)
    digest = canonical_result_hash(presentation.payload)
    identifier = snapshot_id(created, digest)
    result.snapshot_id = identifier
    presentation.payload["snapshot_id"] = identifier
    snapshot = _snapshot_document(result, presentation.payload, created, digest, acquisition)
    try:
        write_snapshot(snapshot, created)
    except Exception as exc:  # noqa: BLE001
        raise PersistenceError("snapshot_write_failed") from exc
    exit_code = 0 if overall is OverallStatus.COMPLETE else 1
    return result, presentation, exit_code


def load_detail(date: str, peak_id: str, snapshot_identifier: str | None = None) -> dict[str, Any]:
    document = read_snapshot(snapshot_identifier) if snapshot_identifier else latest_snapshot()
    if document is None:
        raise ForecastUnavailable("snapshot_not_found")
    for day in document.get("presentation", {}).get("days", []):
        if day.get("local_date") != date:
            continue
        for peak in day.get("peaks", []):
            if peak.get("peak_id") == peak_id:
                return {
                    "schema_version": SCHEMA_VERSION,
                    "snapshot_id": document.get("snapshot_id"),
                    "day": day,
                    "peak": peak,
                }
    raise ForecastUnavailable("peak_day_not_found")


def _snapshot_document(result: ForecastResult, presentation: dict[str, Any], created, digest: str, acquisition: AcquisitionResult) -> dict[str, Any]:
    fetches = []
    for fetch, descriptor in zip(result.sources, result.descriptors):
        payload = fetch.to_dict()
        payload["provider"] = descriptor.provider
        payload["service"] = descriptor.service
        payload["dataset"] = descriptor.dataset
        payload["model"] = descriptor.model
        payload["independence_group"] = descriptor.independence_group
        fetches.append(payload)
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_id": result.snapshot_id,
        "created_at": created.isoformat().replace("+00:00", "Z"),
        "application_version": __version__,
        "request": {
            "mode": result.request.mode.value,
            "reference_time": presentation["query"]["reference_time"],
            "timezone": "America/Montevideo",
            "horizon_start": presentation["query"]["horizon_start"],
            "horizon_end": presentation["query"]["horizon_end"],
            "fixture_id": result.request.fixture_path,
        },
        "source_fetches": fetches,
        "normalized_inputs": {
            "marine_hours": [hour.to_dict() for hour in result.marine_hours],
            "wind_hours": [hour.to_dict() for hour in result.wind_hours],
        },
        "effective_configuration": {
            "criteria_version": result.criteria.criteria_version,
            "criteria_sha256": result.criteria.content_hash,
            "criteria": result.criteria.to_dict(),
            "profiles": [
                {
                    "peak_id": profile.peak_id,
                    "profile_version": profile.profile_version,
                    "profile_sha256": sha256_json(profile.to_dict()),
                    "profile": profile.to_dict(),
                }
                for profile in result.profiles
            ],
        },
        "presentation": presentation,
        "canonical_result_sha256": digest,
        "attribution": presentation["attribution"],
        "incidents": [incident.to_dict() for incident in result.incidents],
        "raw_payload_retained": False,
    }
