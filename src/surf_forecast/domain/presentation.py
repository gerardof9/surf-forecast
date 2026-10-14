"""Immutable presentation model shared by TUI and JSON adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from surf_forecast.domain.models import (
    DaySummary,
    ForecastResult,
    ForecastState,
    PeakDayForecast,
    PeakProfile,
    SourceDescriptor,
    SourceFetch,
    isoformat_utc,
)
from surf_forecast.domain.windows import URUGUAY_TZ

CONDITION_LABELS = {
    "no_surfable_waves": "Sin olas surfeables",
    "small_but_surfable": "Olas pequeñas pero surfeables",
    "fair": "Aceptable",
    "good": "Buena",
    "very_good": "Muy buena",
}

STATE_LABELS = {
    "resolved": "Resuelto",
    "uncertain": "Incierto",
    "incomplete_forecast": "Pronóstico incompleto",
    "analysis_window_completed": "Ventana de análisis finalizada",
}

REASON_LABELS = {
    "range_crosses_threshold": "El rango estimado cruza 0,5 m",
    "two_factor_quality_downgrade": "Dos o más factores desfavorables",
    "single_unfavorable_factor": "Un factor desfavorable (no baja el grado)",
    "size_below_threshold": "Tamaño estimado por debajo de 0,5 m",
    "missing_required_input": "Faltan datos de oleaje o viento",
    "analysis_window_completed": "La ventana de análisis de hoy ya terminó",
    "unsupported_temporal_resolution": "Resolución temporal insuficiente para una ventana de 2 h",
    "fewer_than_two_valid_hours": "Menos de dos horas válidas",
    "shared_regional_grid": "Los cinco picos comparten la misma celda regional del modelo",
    "single_model_family": "Un solo grupo de modelos",
    "provisional_profile": "Perfil provisional",
    "stale_data": "Datos almacenados no frescos",
}

SHARED_NOTICE = {
    "same_model_cell": True,
    "notice_code": "shared_regional_grid",
    "notice_label": "Los picos cercanos comparten la misma celda marina y de viento del modelo; las diferencias salen de los perfiles.",
}

ATTRIBUTION = {
    "text": "Datos: Open-Meteo (CC BY 4.0)",
    "provider_url": "https://open-meteo.com/",
    "license": "CC-BY-4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "modified": True,
}


@dataclass(frozen=True)
class ForecastPresentation:
    payload: dict[str, Any]


def build_presentation(result: ForecastResult) -> ForecastPresentation:
    request = result.request
    payload = {
        "schema_version": "1.0.0",
        "overall_status": result.overall_status.value,
        "snapshot_id": result.snapshot_id,
        "query": {
            "mode": request.mode.value,
            "reference_time": isoformat_utc(request.reference_time),
            "timezone": "America/Montevideo",
            "horizon_start": result.days[0].local_date if result.days else None,
            "horizon_end": result.days[-1].local_date if result.days else None,
        },
        "criteria": {
            "criteria_version": result.criteria.criteria_version,
            "point_k": result.criteria.point_k,
            "range_k_low": result.criteria.range_k_low,
            "range_k_high": result.criteria.range_k_high,
            "surfable_threshold_m": result.criteria.surfable_threshold_m,
        },
        "sources": [_source_out(fetch, result.descriptors) for fetch in result.sources],
        "days": [_day_out(day) for day in result.days],
        "profiles": [_profile_out(profile) for profile in result.profiles],
        "incidents": [incident.to_dict() for incident in result.incidents],
        "attribution": ATTRIBUTION,
        "shared_regional_input": SHARED_NOTICE,
    }
    return ForecastPresentation(payload)


def _day_out(day: DaySummary) -> dict[str, Any]:
    return {
        "local_date": day.local_date,
        "state": day.state.value,
        "headline": day.headline,
        "headline_code": day.headline_code,
        "best_peak_ids": day.best_peak_ids,
        "swell_trend": day.swell_trend.to_dict() if day.swell_trend else None,
        "wind_rotation": day.wind_rotation,
        "peaks": [_peak_out(peak) for peak in day.peaks],
    }


def _peak_out(peak: PeakDayForecast) -> dict[str, Any]:
    condition = peak.condition.value if peak.condition else None
    window = None
    if peak.best_window:
        window = {
            "start_at": isoformat_utc(peak.best_window.start_at),
            "end_at": isoformat_utc(peak.best_window.end_at),
            "duration_minutes": peak.best_window.duration_minutes,
            "condition": peak.best_window.condition.value,
            "support": peak.best_window.support,
        }
    return {
        "peak_id": peak.peak_id,
        "state": peak.state.value,
        "condition": condition,
        "condition_label": CONDITION_LABELS.get(condition) if condition else STATE_LABELS.get(peak.state.value),
        "size": peak.size.to_dict() if peak.size else None,
        "best_window": window,
        "confidence": peak.confidence.to_dict(),
        "reason_codes": peak.reason_codes,
        "highlighted": peak.highlighted,
        "reference_slots": [
            {
                "valid_at": isoformat_utc(slot.valid_at),
                "local_hour": slot.valid_at.astimezone(URUGUAY_TZ).strftime("%H:%M"),
                "state": slot.state.value,
                "condition": slot.condition_grade.value if slot.condition_grade else None,
                "size_point_m": slot.size.point_m if slot.size else None,
                "wind_intensity": slot.wind.intensity.value if slot.wind else None,
                "wind_class": slot.wind.relative_class.value if slot.wind else None,
                "swell_favorability": slot.swell_favorability,
                "period_favorability": slot.period_favorability,
            }
            for slot in peak.reference_slots
        ],
    }


def _profile_out(profile: PeakProfile) -> dict[str, Any]:
    return {
        "peak_id": profile.peak_id,
        "name": profile.name,
        "status": profile.status.value,
        "profile_version": profile.profile_version,
        "validation_errors": profile.validation_errors,
    }


def _source_out(fetch: SourceFetch, descriptors: list[SourceDescriptor]) -> dict[str, Any]:
    descriptor = next((item for item in descriptors if item.source_id == fetch.source_id), None)
    return {
        "source_id": fetch.source_id,
        "provider": descriptor.provider if descriptor else "Open-Meteo",
        "service": descriptor.service if descriptor else "",
        "dataset": descriptor.dataset if descriptor else "",
        "model": descriptor.model if descriptor else "",
        "independence_group": descriptor.independence_group if descriptor else "noaa_ncep_gfs",
        "status": fetch.status.value,
        "downloaded_at": isoformat_utc(fetch.downloaded_at) if fetch.downloaded_at else None,
        "data_age_seconds": fetch.data_age_seconds,
        "requested_coordinate": fetch.requested_coordinate.to_dict(),
        "resolved_coordinate": fetch.resolved_coordinate.to_dict() if fetch.resolved_coordinate else None,
        "model_run_at": isoformat_utc(fetch.model_run_at) if fetch.model_run_at else None,
        "model_run_availability": fetch.model_run_availability,
    }


def spanish_reasons(codes: list[str]) -> list[str]:
    return [REASON_LABELS.get(code, code) for code in codes]
