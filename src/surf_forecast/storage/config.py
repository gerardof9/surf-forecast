"""Load and validate versioned peak and criteria JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from surf_forecast.domain.models import (
    CriteriaSet,
    DirectionSector,
    GradeBand,
    NumericRange,
    PeakProfile,
    ProfileStatus,
    SurfGrade,
    WindBand,
    WindIntensity,
    WindRelative,
)
from surf_forecast.hashing import sha256_json
from surf_forecast.paths import config_dir


class ConfigError(ValueError):
    pass


def load_criteria(path: Path | None = None) -> CriteriaSet:
    file_path = path or (config_dir() / "criteria.json")
    raw = _read_json(file_path)
    bands = [
        GradeBand(SurfGrade(item["grade"]), float(item["minimum_m"]), item.get("maximum_m"))
        for item in raw["size_bands"]
    ]
    winds = [
        WindBand(WindIntensity(item["intensity"]), float(item["minimum_kmh"]), item.get("maximum_kmh"))
        for item in raw["wind_speed_bands"]
    ]
    hashed = {key: value for key, value in raw.items() if key != "content_hash"}
    return CriteriaSet(
        criteria_version=str(raw["criteria_version"]),
        schema_version=str(raw["schema_version"]),
        effective_from=str(raw["effective_from"]),
        point_k=float(raw["point_k"]),
        range_k_low=float(raw["range_k_low"]),
        range_k_high=float(raw["range_k_high"]),
        surfable_threshold_m=float(raw["surfable_threshold_m"]),
        size_bands=bands,
        wind_speed_bands=winds,
        max_quality_downgrade_steps=int(raw.get("max_quality_downgrade_steps", 1)),
        quality_downgrade_min_unfavorable_factors=int(
            raw.get("quality_downgrade_min_unfavorable_factors", 2)
        ),
        wind_unfavorable_classes=[WindRelative(item) for item in raw.get("wind_unfavorable_classes", [])],
        wind_unfavorable_intensities=[
            WindIntensity(item) for item in raw.get("wind_unfavorable_intensities", [])
        ],
        swell_trend_min_samples=int(raw.get("swell_trend_min_samples", 3)),
        swell_trend_relative_change=float(raw.get("swell_trend_relative_change", 0.10)),
        swell_trend_absolute_change_m=float(raw.get("swell_trend_absolute_change_m", 0.1)),
        minimum_surfable_grade=SurfGrade(raw.get("minimum_surfable_grade", "small_but_surfable")),
        analysis_start_local=str(raw.get("analysis_start_local", "06:00")),
        analysis_end_local=str(raw.get("analysis_end_local", "20:00")),
        minimum_window_minutes=int(raw.get("minimum_window_minutes", 120)),
        cache_fresh_minutes=int(raw.get("cache_fresh_minutes", 180)),
        content_hash=sha256_json(hashed),
        raw=raw,
    )


def load_peaks(path: Path | None = None) -> list[PeakProfile]:
    file_path = path or (config_dir() / "peaks.json")
    raw = _read_json(file_path)
    peaks = [_parse_peak(item) for item in raw.get("peaks", [])]
    ids = [peak.peak_id for peak in peaks]
    if len(ids) != len(set(ids)):
        raise ConfigError("peak_id values must be unique")
    return peaks


def _parse_peak(item: dict[str, Any]) -> PeakProfile:
    period = item.get("ideal_period_s") or {}
    return PeakProfile(
        peak_id=str(item.get("peak_id", "")),
        name=str(item.get("name", "")),
        zone_id=str(item.get("zone_id", "")),
        latitude=float(item["latitude"]) if item.get("latitude") is not None else float("nan"),
        longitude=float(item["longitude"]) if item.get("longitude") is not None else float("nan"),
        orientation_deg=float(item["orientation_deg"]) if item.get("orientation_deg") is not None else float("nan"),
        ideal_swell_sectors=_sectors(item.get("ideal_swell_sectors")),
        ideal_period_s=NumericRange(float(period.get("minimum", 0)), float(period.get("maximum", 0))),
        status=ProfileStatus(item.get("status", "provisional")),
        profile_version=str(item.get("profile_version", "0.0.0")),
        schema_version=str(item.get("schema_version", "1.0.0")),
        updated_at=str(item.get("updated_at", "")),
        aliases=list(item.get("aliases") or []),
        acceptable_swell_sectors=_sectors(item.get("acceptable_swell_sectors")),
        blocked_swell_sectors=_sectors(item.get("blocked_swell_sectors")),
        minimum_period_s=item.get("minimum_period_s"),
        offshore_wind_sectors=_sectors(item.get("offshore_wind_sectors")),
        bottom_types=list(item.get("bottom_types") or []),
        estimated_fields=list(item.get("estimated_fields") or []),
        raw=item,
    )


def _sectors(value: Any) -> list[DirectionSector]:
    result: list[DirectionSector] = []
    for item in value or []:
        result.append(
            DirectionSector(
                start_deg=float(item["start_deg"]),
                end_deg=float(item["end_deg"]),
                label=item.get("label"),
            )
        )
    return result


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"missing configuration file: {path}")
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ConfigError(f"configuration must be a JSON object: {path}")
    return payload
