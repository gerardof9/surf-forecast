"""Domain types for the first-delivery surf forecast."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class SurfGrade(StrEnum):
    NO_SURFABLE_WAVES = "no_surfable_waves"
    SMALL_BUT_SURFABLE = "small_but_surfable"
    FAIR = "fair"
    GOOD = "good"
    VERY_GOOD = "very_good"


GRADE_ORDER = [
    SurfGrade.NO_SURFABLE_WAVES,
    SurfGrade.SMALL_BUT_SURFABLE,
    SurfGrade.FAIR,
    SurfGrade.GOOD,
    SurfGrade.VERY_GOOD,
]


class ForecastState(StrEnum):
    RESOLVED = "resolved"
    UNCERTAIN = "uncertain"
    INCOMPLETE_FORECAST = "incomplete_forecast"
    ANALYSIS_WINDOW_COMPLETED = "analysis_window_completed"


class ProfileStatus(StrEnum):
    INCOMPLETE = "incomplete"
    PROVISIONAL = "provisional"
    CALIBRATED = "calibrated"


class QualityClass(StrEnum):
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"
    UNKNOWN = "unknown"


class WindRelative(StrEnum):
    OFFSHORE = "offshore"
    OFFSHORE_SIDE = "offshore_side"
    CROSS_SHORE = "cross_shore"
    ONSHORE_SIDE = "onshore_side"
    ONSHORE = "onshore"
    UNKNOWN = "unknown"


class WindIntensity(StrEnum):
    LIGHT = "light"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"
    UNKNOWN = "unknown"


class QueryMode(StrEnum):
    NORMAL = "normal"
    FORCE_REFRESH = "force_refresh"
    STORED_ONLY = "stored_only"
    FIXTURE_REPLAY = "fixture_replay"


class FetchStatus(StrEnum):
    SUCCESS = "success"
    FRESH_CACHE = "fresh_cache"
    STALE_CACHE = "stale_cache"
    FAILED = "failed"


class CacheState(StrEnum):
    MISS = "miss"
    FRESH = "fresh"
    STALE = "stale"
    FIXTURE = "fixture"


class QualityFlag(StrEnum):
    OBSERVED = "observed"
    DERIVED = "derived"
    MISSING = "missing"
    INVALID = "invalid"


class SwellTrendState(StrEnum):
    BUILDING = "building"
    PEAKING = "peaking"
    DROPPING = "dropping"
    STEADY = "steady"
    UNSUPPORTED = "unsupported"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OverallStatus(StrEnum):
    COMPLETE = "complete"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class GeoPoint:
    latitude: float
    longitude: float

    def to_dict(self) -> dict[str, float]:
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass(frozen=True)
class DirectionSector:
    start_deg: float
    end_deg: float
    label: str | None = None

    def contains(self, deg: float) -> bool:
        heading = deg % 360.0
        start = self.start_deg % 360.0
        end = self.end_deg % 360.0
        if start <= end:
            return start <= heading < end
        return heading >= start or heading < end

    def to_dict(self) -> dict[str, Any]:
        return {"start_deg": self.start_deg, "end_deg": self.end_deg, "label": self.label}


@dataclass(frozen=True)
class NumericRange:
    minimum: float
    maximum: float

    def contains(self, value: float) -> bool:
        return self.minimum <= value <= self.maximum

    def to_dict(self) -> dict[str, float]:
        return {"minimum": self.minimum, "maximum": self.maximum}


@dataclass(frozen=True)
class GradeBand:
    grade: SurfGrade
    minimum_m: float
    maximum_m: float | None

    def contains(self, value: float) -> bool:
        if value < self.minimum_m:
            return False
        if self.maximum_m is None:
            return True
        return value < self.maximum_m


@dataclass(frozen=True)
class WindBand:
    intensity: WindIntensity
    minimum_kmh: float
    maximum_kmh: float | None

    def contains(self, value: float) -> bool:
        if value < self.minimum_kmh:
            return False
        if self.maximum_kmh is None:
            return True
        return value < self.maximum_kmh


@dataclass
class PeakProfile:
    peak_id: str
    name: str
    zone_id: str
    latitude: float
    longitude: float
    orientation_deg: float
    ideal_swell_sectors: list[DirectionSector]
    ideal_period_s: NumericRange
    status: ProfileStatus
    profile_version: str
    schema_version: str
    updated_at: str
    aliases: list[str] = field(default_factory=list)
    acceptable_swell_sectors: list[DirectionSector] = field(default_factory=list)
    blocked_swell_sectors: list[DirectionSector] = field(default_factory=list)
    minimum_period_s: float | None = None
    offshore_wind_sectors: list[DirectionSector] = field(default_factory=list)
    bottom_types: list[str] = field(default_factory=list)
    estimated_fields: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = dict(self.raw) if self.raw else {}
        payload.update(
            {
                "peak_id": self.peak_id,
                "name": self.name,
                "aliases": self.aliases,
                "zone_id": self.zone_id,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "orientation_deg": self.orientation_deg,
                "status": self.status.value,
                "profile_version": self.profile_version,
                "schema_version": self.schema_version,
                "updated_at": self.updated_at,
                "estimated_fields": self.estimated_fields,
                "minimum_period_s": self.minimum_period_s,
                "bottom_types": self.bottom_types,
            }
        )
        return payload


@dataclass
class CriteriaSet:
    criteria_version: str
    schema_version: str
    effective_from: str
    point_k: float
    range_k_low: float
    range_k_high: float
    surfable_threshold_m: float
    size_bands: list[GradeBand]
    wind_speed_bands: list[WindBand]
    max_quality_downgrade_steps: int
    quality_downgrade_min_unfavorable_factors: int
    wind_unfavorable_classes: list[WindRelative]
    wind_unfavorable_intensities: list[WindIntensity]
    swell_trend_min_samples: int
    swell_trend_relative_change: float
    swell_trend_absolute_change_m: float
    minimum_surfable_grade: SurfGrade
    analysis_start_local: str
    analysis_end_local: str
    minimum_window_minutes: int
    cache_fresh_minutes: int
    content_hash: str
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


@dataclass(frozen=True)
class SourceDescriptor:
    source_id: str
    provider: str
    service: str
    dataset: str
    model: str
    model_family: str
    independence_group: str
    terms_url: str
    license: str
    attribution: str
    native_temporal_resolution_minutes: int
    spatial_resolution_km: float
    model_run_time_available: bool
    requested_coordinate: GeoPoint

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": self.provider,
            "service": self.service,
            "dataset": self.dataset,
            "model": self.model,
            "model_family": self.model_family,
            "independence_group": self.independence_group,
            "terms_url": self.terms_url,
            "license": self.license,
            "attribution": self.attribution,
            "native_temporal_resolution_minutes": self.native_temporal_resolution_minutes,
            "spatial_resolution_km": self.spatial_resolution_km,
            "model_run_time_available": self.model_run_time_available,
            "requested_coordinate": self.requested_coordinate.to_dict(),
        }


@dataclass
class SourceFetch:
    fetch_id: str
    source_id: str
    requested_at: datetime
    completed_at: datetime | None
    request_url: str
    requested_coordinate: GeoPoint
    resolved_coordinate: GeoPoint | None
    model_run_at: datetime | None
    model_run_availability: str
    valid_from: datetime | None
    valid_to: datetime | None
    status: FetchStatus
    cache_state: CacheState
    http_status: int | None = None
    payload_sha256: str | None = None
    error_code: str | None = None
    incident_ids: list[str] = field(default_factory=list)
    downloaded_at: datetime | None = None
    data_age_seconds: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": None,
            "request_url_redacted": self.request_url,
            "requested_at": _iso(self.requested_at),
            "completed_at": _iso(self.completed_at),
            "status": self.status.value,
            "cache_state": self.cache_state.value,
            "requested_coordinate": self.requested_coordinate.to_dict(),
            "resolved_coordinate": self.resolved_coordinate.to_dict() if self.resolved_coordinate else None,
            "valid_time_start": _iso(self.valid_from),
            "valid_time_end": _iso(self.valid_to),
            "model_run_at": _iso(self.model_run_at),
            "model_run_availability": self.model_run_availability,
            "downloaded_at": _iso(self.downloaded_at),
            "http_status": self.http_status,
            "error_code": self.error_code,
            "payload_sha256": self.payload_sha256,
            "incident_ids": self.incident_ids,
        }


@dataclass
class NormalizedMarineHour:
    source_id: str
    valid_at: datetime
    wave_height_m: float | None
    wave_direction_deg: float | None
    wave_period_s: float | None
    swell_height_m: float | None
    swell_direction_deg: float | None
    swell_period_s: float | None
    wind_wave_height_m: float | None
    wind_wave_direction_deg: float | None
    wind_wave_period_s: float | None
    quality: QualityFlag
    source_fetch_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "valid_at": _iso(self.valid_at),
            "wave_height_m": self.wave_height_m,
            "wave_direction_deg": self.wave_direction_deg,
            "wave_period_s": self.wave_period_s,
            "swell_height_m": self.swell_height_m,
            "swell_direction_deg": self.swell_direction_deg,
            "swell_period_s": self.swell_period_s,
            "wind_wave_height_m": self.wind_wave_height_m,
            "wind_wave_direction_deg": self.wind_wave_direction_deg,
            "wind_wave_period_s": self.wind_wave_period_s,
            "quality": self.quality.value,
        }


@dataclass
class NormalizedWindHour:
    source_id: str
    valid_at: datetime
    speed_kmh: float | None
    direction_deg: float | None
    gust_kmh: float | None
    quality: QualityFlag
    source_fetch_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "valid_at": _iso(self.valid_at),
            "speed_kmh": self.speed_kmh,
            "direction_deg": self.direction_deg,
            "gust_kmh": self.gust_kmh,
            "quality": self.quality.value,
        }


@dataclass
class Incident:
    incident_id: str
    code: str
    severity: str
    occurred_at: datetime
    details: dict[str, Any] = field(default_factory=dict)
    source_id: str | None = None
    variable: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "code": self.code,
            "severity": self.severity,
            "occurred_at": _iso(self.occurred_at),
            "details": self.details,
            "source_id": self.source_id,
            "variable": self.variable,
        }


@dataclass
class QueryRequest:
    mode: QueryMode
    reference_time: datetime
    timezone: str
    peak_ids: list[str] = field(default_factory=list)
    fixture_path: str | None = None
    output_mode: str = "human"


@dataclass
class SurfableSizeEstimate:
    raw_hs_m: float
    point_m: float
    minimum_m: float
    maximum_m: float
    point_k: float
    range_k_low: float
    range_k_high: float
    method: str = "provisional_k_times_hs"
    calibrated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WindAssessment:
    relative_class: WindRelative
    intensity: WindIntensity
    quality_class: QualityClass
    favorable: bool | None
    reasons: list[str] = field(default_factory=list)
    # Display pass-through only (presentation); not used by evaluation thresholds.
    speed_kmh: float | None = None
    direction_deg: float | None = None


@dataclass
class SlotEvaluation:
    peak_id: str
    valid_at: datetime
    size: SurfableSizeEstimate | None
    wind: WindAssessment | None
    swell_favorability: str
    period_favorability: str
    swell_quality_class: QualityClass
    period_quality_class: QualityClass
    ceiling_grade: SurfGrade | None
    unfavorable_factor_count: int
    quality_downgrade_steps: int
    condition_grade: SurfGrade | None
    state: ForecastState
    reason_codes: list[str] = field(default_factory=list)


@dataclass
class BestWindow:
    start_at: datetime
    end_at: datetime
    duration_minutes: int
    condition: SurfGrade
    support: str


@dataclass
class SwellTrend:
    state: SwellTrendState
    sample_count: int
    variable: str
    method: str = "hourly_tercile_means"

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "sample_count": self.sample_count,
            "variable": self.variable,
            "method": self.method,
        }


@dataclass
class ConfidenceAssessment:
    level: ConfidenceLevel
    caps: list[str]
    degradations: list[str]
    explanation_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "caps": self.caps,
            "degradations": self.degradations,
        }


@dataclass
class PeakDayForecast:
    peak_id: str
    local_date: str
    state: ForecastState
    condition: SurfGrade | None
    size: SurfableSizeEstimate | None
    best_window: BestWindow | None
    confidence: ConfidenceAssessment
    reason_codes: list[str]
    highlighted: bool = False
    reference_slots: list[SlotEvaluation] = field(default_factory=list)


@dataclass
class DaySummary:
    local_date: str
    state: ForecastState
    headline: str | None
    headline_code: str | None
    best_peak_ids: list[str]
    swell_trend: SwellTrend | None
    wind_rotation: dict[str, Any] | None
    peaks: list[PeakDayForecast]


@dataclass
class ForecastResult:
    overall_status: OverallStatus
    snapshot_id: str
    request: QueryRequest
    criteria: CriteriaSet
    days: list[DaySummary]
    profiles: list[PeakProfile]
    sources: list[SourceFetch]
    descriptors: list[SourceDescriptor]
    incidents: list[Incident]
    marine_hours: list[NormalizedMarineHour]
    wind_hours: list[NormalizedWindHour]
    attribution: dict[str, Any]


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.isoformat() + "Z"
    return value.astimezone().isoformat().replace("+00:00", "Z")


def isoformat_utc(value: datetime) -> str:
    return value.astimezone().isoformat().replace("+00:00", "Z")
