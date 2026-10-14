"""Open-Meteo marine GFS Wave and atmospheric GFS adapters."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from surf_forecast.domain.models import (
    CacheState,
    FetchStatus,
    GeoPoint,
    Incident,
    NormalizedMarineHour,
    NormalizedWindHour,
    QualityFlag,
    SourceFetch,
)
from surf_forecast.hashing import sha256_json
from surf_forecast.sources.base import (
    MARINE_COORDINATE,
    MARINE_DESCRIPTOR,
    WIND_COORDINATE,
    WIND_DESCRIPTOR,
    AcquisitionResult,
)
from surf_forecast.storage.cache import cache_key, classify_age, parse_utc, read_entry, write_entry

TIMEOUT_SECONDS = 10
RETRY_DELAY_SECONDS = 0.5
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
WIND_URL = "https://api.open-meteo.com/v1/gfs"


class OpenMeteoAdapter:
    def __init__(self, fixture: dict[str, Any] | None = None) -> None:
        self.fixture = fixture

    def acquire(self, now: datetime, *, force_refresh: bool, stored_only: bool) -> AcquisitionResult:
        utc_now = now.astimezone(timezone.utc)
        marine = self._fetch(
            descriptor=MARINE_DESCRIPTOR,
            url=MARINE_URL,
            params=_marine_params(),
            now=utc_now,
            force_refresh=force_refresh,
            stored_only=stored_only,
            kind="marine",
        )
        wind = self._fetch(
            descriptor=WIND_DESCRIPTOR,
            url=WIND_URL,
            params=_wind_params(),
            now=utc_now,
            force_refresh=force_refresh,
            stored_only=stored_only,
            kind="wind",
        )
        incidents: list[Incident] = []
        incidents.extend(marine[3])
        incidents.extend(wind[3])
        return AcquisitionResult(
            fetches=[marine[0], wind[0]],
            descriptors=[MARINE_DESCRIPTOR, WIND_DESCRIPTOR],
            marine_hours=marine[1],
            wind_hours=wind[2],
            incidents=incidents,
            raw_payloads={"marine": marine[4], "wind": wind[4]},
        )

    def _fetch(
        self,
        *,
        descriptor,
        url: str,
        params: dict[str, str],
        now: datetime,
        force_refresh: bool,
        stored_only: bool,
        kind: str,
    ) -> tuple[SourceFetch, list[NormalizedMarineHour], list[NormalizedWindHour], list[Incident], dict[str, Any] | None]:
        key = cache_key(descriptor.source_id, params)
        request_url = f"{url}?{urlencode(params)}"
        fetch = SourceFetch(
            fetch_id=str(uuid.uuid4()),
            source_id=descriptor.source_id,
            requested_at=now,
            completed_at=None,
            request_url=request_url,
            requested_coordinate=descriptor.requested_coordinate,
            resolved_coordinate=None,
            model_run_at=None,
            model_run_availability="unavailable",
            valid_from=None,
            valid_to=None,
            status=FetchStatus.FAILED,
            cache_state=CacheState.MISS,
        )
        incidents: list[Incident] = []
        payload: dict[str, Any] | None = None
        cached = read_entry(key) if self.fixture is None else None
        if self.fixture is not None:
            payload = self.fixture.get(kind)
            fetch.cache_state = CacheState.FIXTURE
            if payload is None:
                fetch.status = FetchStatus.FAILED
                fetch.error_code = "fixture_missing_source"
                incidents.append(_incident("source_failed", now, descriptor.source_id, fetch.error_code))
                return fetch, [], [], incidents, None
            fetch.status = FetchStatus.SUCCESS
        elif stored_only:
            if cached is None:
                fetch.error_code = "stored_only_unavailable"
                incidents.append(_incident("source_failed", now, descriptor.source_id, fetch.error_code))
                return fetch, [], [], incidents, None
            payload = cached["response"]
            fetched_at = parse_utc(cached["fetched_at"])
            age_state = classify_age(fetched_at, now)
            fetch.cache_state = age_state
            fetch.status = FetchStatus.FRESH_CACHE if age_state is CacheState.FRESH else FetchStatus.STALE_CACHE
            fetch.downloaded_at = fetched_at
            fetch.data_age_seconds = int((now - fetched_at).total_seconds())
        else:
            if cached is not None and not force_refresh:
                fetched_at = parse_utc(cached["fetched_at"])
                if classify_age(fetched_at, now) is CacheState.FRESH:
                    payload = cached["response"]
                    fetch.cache_state = CacheState.FRESH
                    fetch.status = FetchStatus.FRESH_CACHE
                    fetch.downloaded_at = fetched_at
                    fetch.data_age_seconds = int((now - fetched_at).total_seconds())
                    fetch.completed_at = now
                    fetch.payload_sha256 = sha256_json(payload)
                    fetch.resolved_coordinate = GeoPoint(
                        float(payload.get("latitude", descriptor.requested_coordinate.latitude)),
                        float(payload.get("longitude", descriptor.requested_coordinate.longitude)),
                    )
                    marine_hours, wind_hours = _hours_from_payload(kind, descriptor.source_id, fetch.fetch_id, payload)
                    times = (payload.get("hourly") or {}).get("time") or []
                    if times:
                        fetch.valid_from = _parse_time(times[0], payload)
                        fetch.valid_to = _parse_time(times[-1], payload)
                    return fetch, marine_hours, wind_hours, incidents, payload
            live = _http_get(request_url)
            if live is not None:
                payload, status_code = live
                fetch.http_status = status_code
                fetch.status = FetchStatus.SUCCESS
                fetch.downloaded_at = now
                fetch.data_age_seconds = 0
                write_entry(
                    key,
                    {
                        "fetched_at": now.isoformat().replace("+00:00", "Z"),
                        "request": params,
                        "response": payload,
                        "payload_sha256": sha256_json(payload),
                    },
                )
            elif cached is not None:
                payload = cached["response"]
                fetched_at = parse_utc(cached["fetched_at"])
                age_state = classify_age(fetched_at, now)
                fetch.cache_state = age_state
                fetch.status = FetchStatus.FRESH_CACHE if age_state is CacheState.FRESH else FetchStatus.STALE_CACHE
                fetch.downloaded_at = fetched_at
                fetch.data_age_seconds = int((now - fetched_at).total_seconds())
                if age_state is CacheState.STALE:
                    incidents.append(_incident("stale_cache", now, descriptor.source_id, "stale_cache"))
            else:
                fetch.error_code = "source_unavailable"
                incidents.append(_incident("source_failed", now, descriptor.source_id, fetch.error_code))
                return fetch, [], [], incidents, None
        fetch.completed_at = now
        fetch.payload_sha256 = sha256_json(payload) if payload else None
        fetch.resolved_coordinate = GeoPoint(
            float(payload.get("latitude", descriptor.requested_coordinate.latitude)),
            float(payload.get("longitude", descriptor.requested_coordinate.longitude)),
        )
        marine_hours: list[NormalizedMarineHour] = []
        wind_hours: list[NormalizedWindHour] = []
        hourly = payload.get("hourly") or {}
        times = hourly.get("time") or []
        if times:
            first = _parse_time(times[0], payload)
            last = _parse_time(times[-1], payload)
            fetch.valid_from = first
            fetch.valid_to = last
        marine_hours, wind_hours = _hours_from_payload(kind, descriptor.source_id, fetch.fetch_id, payload)
        return fetch, marine_hours, wind_hours, incidents, payload


def _hours_from_payload(kind: str, source_id: str, fetch_id: str, payload: dict[str, Any]):
    if kind == "marine":
        return _normalize_marine(source_id, fetch_id, payload), []
    return [], _normalize_wind(source_id, fetch_id, payload)


def _marine_params() -> dict[str, str]:
    return {
        "latitude": str(MARINE_COORDINATE.latitude),
        "longitude": str(MARINE_COORDINATE.longitude),
        "hourly": ",".join(
            [
                "wave_height",
                "wave_direction",
                "wave_period",
                "swell_wave_height",
                "swell_wave_direction",
                "swell_wave_period",
                "wind_wave_height",
                "wind_wave_direction",
                "wind_wave_period",
            ]
        ),
        "models": "ncep_gfswave025",
        "cell_selection": "sea",
        "forecast_days": "5",
        "timezone": "UTC",
        "timeformat": "iso8601",
    }


def _wind_params() -> dict[str, str]:
    return {
        "latitude": str(WIND_COORDINATE.latitude),
        "longitude": str(WIND_COORDINATE.longitude),
        "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "forecast_days": "5",
        "timezone": "UTC",
        "timeformat": "iso8601",
        "wind_speed_unit": "kmh",
    }


def _http_get(url: str) -> tuple[dict[str, Any], int] | None:
    last_error: Exception | None = None
    for _attempt in range(2):
        try:
            request = Request(url, headers={"User-Agent": "surf-forecast/0.1 personal-use"})
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body, int(getattr(response, "status", 200))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if _attempt == 0:
                import time

                time.sleep(RETRY_DELAY_SECONDS)
    return None if last_error else None


def _parse_time(value: str, payload: dict[str, Any]) -> datetime:
    if value.endswith("Z") or "+" in value[10:]:
        return parse_utc(value if "Z" in value or "+" in value else value + "Z")
    utc_offset = payload.get("utc_offset_seconds", 0) or 0
    naive = datetime.fromisoformat(value)
    return naive.replace(tzinfo=timezone(timedelta(seconds=int(utc_offset)))).astimezone(timezone.utc)


def _normalize_marine(source_id: str, fetch_id: str, payload: dict[str, Any]) -> list[NormalizedMarineHour]:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    rows: list[NormalizedMarineHour] = []
    for index, stamp in enumerate(times):
        valid_at = _parse_time(stamp, payload)
        height = _num(hourly.get("wave_height"), index)
        quality = QualityFlag.OBSERVED if height is not None else QualityFlag.MISSING
        rows.append(
            NormalizedMarineHour(
                source_id=source_id,
                valid_at=valid_at,
                wave_height_m=height,
                wave_direction_deg=_num(hourly.get("wave_direction"), index),
                wave_period_s=_num(hourly.get("wave_period"), index),
                swell_height_m=_num(hourly.get("swell_wave_height"), index),
                swell_direction_deg=_num(hourly.get("swell_wave_direction"), index),
                swell_period_s=_num(hourly.get("swell_wave_period"), index),
                wind_wave_height_m=_num(hourly.get("wind_wave_height"), index),
                wind_wave_direction_deg=_num(hourly.get("wind_wave_direction"), index),
                wind_wave_period_s=_num(hourly.get("wind_wave_period"), index),
                quality=quality,
                source_fetch_id=fetch_id,
            )
        )
    return rows


def _normalize_wind(source_id: str, fetch_id: str, payload: dict[str, Any]) -> list[NormalizedWindHour]:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    rows: list[NormalizedWindHour] = []
    for index, stamp in enumerate(times):
        speed = _num(hourly.get("wind_speed_10m"), index)
        rows.append(
            NormalizedWindHour(
                source_id=source_id,
                valid_at=_parse_time(stamp, payload),
                speed_kmh=speed,
                direction_deg=_num(hourly.get("wind_direction_10m"), index),
                gust_kmh=_num(hourly.get("wind_gusts_10m"), index),
                quality=QualityFlag.OBSERVED if speed is not None else QualityFlag.MISSING,
                source_fetch_id=fetch_id,
            )
        )
    return rows


def _num(series: list[Any] | None, index: int) -> float | None:
    if not series or index >= len(series):
        return None
    value = series[index]
    if value is None:
        return None
    return float(value)


def _incident(code: str, when: datetime, source_id: str, detail: str) -> Incident:
    return Incident(
        incident_id=str(uuid.uuid4()),
        code=code,
        severity="error" if code == "source_failed" else "warning",
        occurred_at=when,
        source_id=source_id,
        details={"detail": detail},
    )
