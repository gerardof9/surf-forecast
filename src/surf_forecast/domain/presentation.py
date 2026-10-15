"""Immutable presentation model shared by TUI, CLI, and JSON adapters (schema 1.2.0)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from surf_forecast.domain.day_rating import build_day_rating, build_peak_rating
from surf_forecast.domain.evolution_samples import direction_label, representative_wind, sample_evolution
from surf_forecast.domain.models import (
    GRADE_ORDER,
    DaySummary,
    ForecastResult,
    ForecastState,
    PeakDayForecast,
    PeakProfile,
    SourceDescriptor,
    SourceFetch,
    SurfGrade,
    isoformat_utc,
)
from surf_forecast.domain.narrative import build_day_brief, build_peak_analysis
from surf_forecast.domain.windows import URUGUAY_TZ

SCHEMA_VERSION = "1.2.0"

WORTH_MIN_GRADE = SurfGrade.FAIR
WORTH_MAX = 3
EMPTY_SPOTS_MESSAGE = "Ningún pico claro para ir."

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

_LABELS = ("Hoy", "Mañana")


@dataclass(frozen=True)
class ForecastPresentation:
    payload: dict[str, Any]


def condition_or_state_label(condition: str | None, state: ForecastState | str) -> str:
    if condition:
        return CONDITION_LABELS.get(condition, condition)
    state_value = state.value if isinstance(state, ForecastState) else state
    return STATE_LABELS.get(state_value, state_value)


def rank_worth_spots(
    peaks: list[PeakDayForecast],
    *,
    profile_by_id: dict[str, PeakProfile],
) -> list[dict[str, Any]]:
    """Fair+ peaks only, best-first, max WORTH_MAX."""
    candidates: list[tuple[int, float, str, PeakDayForecast]] = []
    min_rank = GRADE_ORDER.index(WORTH_MIN_GRADE)
    for peak in peaks:
        if peak.condition is None:
            continue
        if peak.state is not ForecastState.RESOLVED:
            continue
        rank = GRADE_ORDER.index(peak.condition)
        if rank < min_rank:
            continue
        rating = build_peak_rating(peak)
        score = float(rating["score"]) if rating else float(rank)
        candidates.append((rank, score, peak.peak_id, peak))
    candidates.sort(key=lambda item: (-item[0], -item[1], item[2]))
    out: list[dict[str, Any]] = []
    for _, _, _, peak in candidates[:WORTH_MAX]:
        profile = profile_by_id.get(peak.peak_id)
        name = profile.name if profile else peak.peak_id.replace("_", " ").title()
        cond = peak.condition.value if peak.condition else None
        out.append(
            {
                "peak_id": peak.peak_id,
                "display_name": name,
                "condition": cond,
                "condition_label": condition_or_state_label(cond, peak.state),
                "reason_short": "Mejor ventana" if not out else None,
            }
        )
    if out:
        out[0]["reason_short"] = "Mejor opción del día"
    return out


def height_summary_from_peak(peak: PeakDayForecast | None) -> dict[str, Any] | None:
    if peak is None or peak.size is None:
        return None
    size = peak.size
    display = f"{size.minimum_m:.1f}–{size.maximum_m:.1f} m".replace(".", ",")
    return {
        "minimum_m": size.minimum_m,
        "maximum_m": size.maximum_m,
        "display": display,
        "kind": "derived",
    }


def go_window_from_peak(peak: PeakDayForecast | None) -> dict[str, Any] | None:
    if peak is None or peak.best_window is None:
        return None
    window = peak.best_window
    start = window.start_at.astimezone(URUGUAY_TZ).strftime("%H:%M")
    end = window.end_at.astimezone(URUGUAY_TZ).strftime("%H:%M")
    mins = int(window.duration_minutes or 0)
    wide = mins >= 6 * 60 or (start == "06:00" and end == "20:00")
    if wide:
        display = f"Ventana amplia (día completo) {start}–{end}"
    else:
        display = f"Mejor entre {start}–{end}"
    return {
        "start_local": start,
        "end_local": end,
        "wide": wide,
        "display": display,
        "source_peak_id": peak.peak_id,
        "duration_minutes": mins,
        "start_at": isoformat_utc(window.start_at),
        "end_at": isoformat_utc(window.end_at),
    }


def build_presentation(result: ForecastResult) -> ForecastPresentation:
    request = result.request
    profiles = result.profiles
    profile_by_id = {p.peak_id: p for p in profiles}
    sources_ok = result.overall_status.value == "complete"
    query_local = request.reference_time.astimezone(URUGUAY_TZ)
    data_updated = _best_data_updated_local(result.sources)

    presented = _select_two_days(result.days, reference_local=query_local)
    days_out = [
        _day_brief_out(
            day,
            label=label,
            fallback_date=fallback_date,
            profile_by_id=profile_by_id,
            profiles=profiles,
            sources_ok=sources_ok,
            incomplete=incomplete,
        )
        for day, label, incomplete, fallback_date in presented
    ]

    horizon_start = days_out[0]["local_date"] if days_out else None
    horizon_end = days_out[-1]["local_date"] if days_out else None

    payload = {
        "schema_version": SCHEMA_VERSION,
        "overall_status": result.overall_status.value,
        "snapshot_id": result.snapshot_id,
        "query": {
            "mode": request.mode.value,
            "reference_time": isoformat_utc(request.reference_time),
            "timezone": "America/Montevideo",
            "horizon_start": horizon_start,
            "horizon_end": horizon_end,
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
        "days": days_out,
        "profiles": [_profile_out(profile) for profile in result.profiles],
        "incidents": [incident.to_dict() for incident in result.incidents],
        "attribution": ATTRIBUTION,
        "shared_regional_input": SHARED_NOTICE,
    }
    return ForecastPresentation(payload)


def _select_two_days(
    days: list[DaySummary],
    *,
    reference_local: datetime,
) -> list[tuple[DaySummary | None, str, bool, str]]:
    """Return exactly two (day|None, label, incomplete, fallback_date) slots: Hoy, Mañana."""
    by_date = {d.local_date: d for d in days}
    hoy = reference_local.date().isoformat()
    manana = (reference_local.date() + timedelta(days=1)).isoformat()

    d0 = by_date.get(hoy)
    if d0 is None and days:
        d0 = days[0]

    d1 = by_date.get(manana)
    if d1 is None:
        for candidate in days:
            if d0 is None or candidate.local_date != d0.local_date:
                d1 = candidate
                break

    return [
        (d0, "Hoy", d0 is None, hoy),
        (d1, "Mañana", d1 is None, manana),
    ]


def _day_brief_out(
    day: DaySummary | None,
    *,
    label: str,
    fallback_date: str,
    profile_by_id: dict[str, PeakProfile],
    profiles: list[PeakProfile],
    sources_ok: bool,
    incomplete: bool,
) -> dict[str, Any]:
    if day is None or incomplete:
        stub = DaySummary(
            local_date=fallback_date,
            state=ForecastState.INCOMPLETE_FORECAST,
            headline=None,
            headline_code="incomplete_forecast",
            best_peak_ids=[],
            swell_trend=None,
            wind_rotation=None,
            peaks=[],
        )
        narrative = build_day_brief(
            stub,
            profiles=profiles,
            worth_spots=[],
            go_window=None,
            height=None,
            sources_ok=sources_ok,
            incomplete=True,
        )
        return {
            "local_date": stub.local_date,
            "display_title": _display_title(stub.local_date),
            "state": stub.state.value,
            "brief": {
                "label": label,
                "condition": None,
                "condition_label": STATE_LABELS["incomplete_forecast"],
                "headline": narrative["headline"],
                "body": narrative["body"],
                "caution": narrative["caution"],
                "height": None,
                "go_window": None,
                "worth_spots": [],
                "empty_spots_message": EMPTY_SPOTS_MESSAGE,
            },
        }

    worth = rank_worth_spots(day.peaks, profile_by_id=profile_by_id)
    best_peak = None
    if worth:
        best_id = worth[0]["peak_id"]
        best_peak = next((p for p in day.peaks if p.peak_id == best_id), None)
    height = height_summary_from_peak(best_peak)
    go_window = go_window_from_peak(best_peak)
    narrative = build_day_brief(
        day,
        profiles=profiles,
        worth_spots=worth,
        go_window=go_window,
        height=height,
        sources_ok=sources_ok,
        incomplete=False,
    )
    rating, absent = build_day_rating(day)
    condition = None
    if rating and rating.get("source_peak_id"):
        src = next((p for p in day.peaks if p.peak_id == rating["source_peak_id"]), None)
        if src and src.condition:
            condition = src.condition.value
    elif worth:
        condition = worth[0]["condition"]

    return {
        "local_date": day.local_date,
        "display_title": _display_title(day.local_date),
        "state": day.state.value,
        "day_rating": rating,
        "day_rating_absent_reason": absent,
        "brief": {
            "label": label,
            "condition": condition,
            "condition_label": condition_or_state_label(condition, day.state),
            "headline": narrative["headline"],
            "body": narrative["body"],
            "caution": narrative["caution"],
            "height": height,
            "go_window": go_window,
            "worth_spots": worth,
            "empty_spots_message": None if worth else EMPTY_SPOTS_MESSAGE,
        },
    }


def _peak_out(
    peak: PeakDayForecast,
    *,
    profile: PeakProfile | None,
    best_of_day: bool,
) -> dict[str, Any]:
    """Optional debug peak payload (not required by 1.2.0 home)."""
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
