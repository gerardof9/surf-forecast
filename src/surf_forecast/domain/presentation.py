"""Immutable presentation model shared by TUI and JSON adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from surf_forecast.domain.day_rating import build_day_rating, build_peak_rating
from surf_forecast.domain.evolution_samples import direction_label, representative_wind, sample_evolution
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
from surf_forecast.domain.narrative import build_day_analysis, build_peak_analysis
from surf_forecast.domain.windows import URUGUAY_TZ

# FR-017 compact vocabulary (engine ids unchanged).
CONDITION_LABELS = {
    "no_surfable_waves": "Pocas olas",
    "small_but_surfable": "Variable",
    "fair": "Surfeable",
    "good": "Buena oportunidad",
    "very_good": "Buena oportunidad",
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

_WEEKDAYS = (
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
)


@dataclass(frozen=True)
class ForecastPresentation:
    payload: dict[str, Any]


def condition_or_state_label(condition: str | None, state: ForecastState | str) -> str:
    if condition:
        return CONDITION_LABELS.get(condition, condition)
    state_value = state.value if isinstance(state, ForecastState) else state
    return STATE_LABELS.get(state_value, state_value)


def build_presentation(result: ForecastResult) -> ForecastPresentation:
    request = result.request
    profiles = result.profiles
    profile_by_id = {p.peak_id: p for p in profiles}
    sources_ok = result.overall_status.value == "complete"
    query_local = request.reference_time.astimezone(URUGUAY_TZ)
    data_updated = _best_data_updated_local(result.sources)

    payload = {
        "schema_version": "1.1.0",
        "overall_status": result.overall_status.value,
        "snapshot_id": result.snapshot_id,
        "query": {
            "mode": request.mode.value,
            "reference_time": isoformat_utc(request.reference_time),
            "timezone": "America/Montevideo",
            "horizon_start": result.days[0].local_date if result.days else None,
            "horizon_end": result.days[-1].local_date if result.days else None,
        },
        "query_times": {
            "executed_at_local": query_local.strftime("%Y-%m-%d %H:%M UYT"),
        },
        "data_times": {
            "meteorological_updated_at_local": data_updated,
            "label": "Actualización de datos (no es la hora de consulta)",
        },
        "criteria": {
            "criteria_version": result.criteria.criteria_version,
            "point_k": result.criteria.point_k,
            "range_k_low": result.criteria.range_k_low,
            "range_k_high": result.criteria.range_k_high,
            "surfable_threshold_m": result.criteria.surfable_threshold_m,
        },
        "sources": [_source_out(fetch, result.descriptors) for fetch in result.sources],
        "days": [
            _day_out(day, profile_by_id=profile_by_id, profiles=profiles, sources_ok=sources_ok)
            for day in result.days
        ],
        "profiles": [_profile_out(profile) for profile in result.profiles],
        "incidents": [incident.to_dict() for incident in result.incidents],
        "attribution": ATTRIBUTION,
        "shared_regional_input": SHARED_NOTICE,
    }
    return ForecastPresentation(payload)


def _day_out(
    day: DaySummary,
    *,
    profile_by_id: dict[str, PeakProfile],
    profiles: list[PeakProfile],
    sources_ok: bool,
) -> dict[str, Any]:
    rating, absent = build_day_rating(day)
    source_id = rating["source_peak_id"] if rating else None
    peaks_out = [
        _peak_out(
            peak,
            profile=profile_by_id.get(peak.peak_id),
            best_of_day=(source_id is not None and peak.peak_id == source_id),
        )
        for peak in day.peaks
    ]
    return {
        "local_date": day.local_date,
        "display_title": _display_title(day.local_date),
        "state": day.state.value,
        "headline": day.headline,
        "headline_code": day.headline_code,
        "best_peak_ids": day.best_peak_ids,
        "swell_trend": day.swell_trend.to_dict() if day.swell_trend else None,
        "wind_rotation": day.wind_rotation,
        "day_rating": rating,
        "day_rating_absent_reason": absent,
        "day_analysis": build_day_analysis(day, profiles=profiles, sources_ok=sources_ok),
        "peaks": peaks_out,
    }


def _peak_out(
    peak: PeakDayForecast,
    *,
    profile: PeakProfile | None,
    best_of_day: bool,
) -> dict[str, Any]:
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
    wind_dir, wind_speed, wind_intensity = representative_wind(peak)
    period_s = _representative_period(peak)
    peak_analysis, peak_absent = build_peak_analysis(peak, profile=profile)
    display_name = profile.name if profile else peak.peak_id.replace("_", " ").title()
    window_done = "analysis_window_completed" in (peak.reason_codes or []) or peak.state is ForecastState.ANALYSIS_WINDOW_COMPLETED
    return {
        "peak_id": peak.peak_id,
        "display_name": display_name,
        "state": peak.state.value,
        "condition": condition,
        "condition_label": condition_or_state_label(condition, peak.state),
        "size": peak.size.to_dict() if peak.size else None,
        "period_s": period_s,
        "best_window": window,
        "confidence": peak.confidence.to_dict(),
        "reason_codes": peak.reason_codes,
        "highlighted": peak.highlighted,
        "best_of_day": best_of_day,
        "peak_rating": build_peak_rating(peak),
        "peak_analysis": peak_analysis,
        "peak_analysis_absent_reason": peak_absent,
        "wind_dir_label": wind_dir,
        "wind_speed_kmh": wind_speed,
        "wind_intensity": wind_intensity,
        "window_completed": window_done,
        "evolution_samples": sample_evolution(peak),
        "reference_slots": [
            {
                "valid_at": isoformat_utc(slot.valid_at),
                "local_hour": slot.valid_at.astimezone(URUGUAY_TZ).strftime("%H:%M"),
                "state": slot.state.value,
                "condition": slot.condition_grade.value if slot.condition_grade else None,
                "size_point_m": slot.size.point_m if slot.size else None,
                "period_s": slot.period_s,
                "wind_intensity": slot.wind.intensity.value if slot.wind else None,
                "wind_class": slot.wind.relative_class.value if slot.wind else None,
                "wind_speed_kmh": slot.wind.speed_kmh if slot.wind else None,
                "wind_dir_label": direction_label(slot.wind.direction_deg) if slot.wind else None,
                "swell_favorability": slot.swell_favorability,
                "period_favorability": slot.period_favorability,
            }
            for slot in peak.reference_slots
        ],
    }


def _representative_period(peak: PeakDayForecast) -> float | None:
    for slot in peak.reference_slots:
        if slot.period_s is not None:
            return slot.period_s
    return None


def _display_title(local_date: str) -> str:
    try:
        dt = datetime.strptime(local_date, "%Y-%m-%d").replace(tzinfo=URUGUAY_TZ)
    except ValueError:
        return local_date
    return f"{_WEEKDAYS[dt.weekday()]} {dt.strftime('%d/%m')}"


def _best_data_updated_local(sources: list[SourceFetch]) -> str | None:
    stamps = [s.downloaded_at for s in sources if s.downloaded_at is not None]
    if not stamps:
        return None
    latest = max(stamps)
    return latest.astimezone(URUGUAY_TZ).strftime("%Y-%m-%d %H:%M UYT")


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
