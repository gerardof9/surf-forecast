"""Immutable presentation model shared by TUI, CLI, and JSON adapters (schema 1.2.0)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from surf_forecast.domain.day_rating import build_day_rating, build_peak_rating
from surf_forecast.domain.evaluation import circular_delta
from surf_forecast.domain.evolution_samples import (
    direction_label,
    direction_label_16,
    representative_wind,
    sample_evolution,
)
from surf_forecast.domain.models import (
    GRADE_ORDER,
    DaySummary,
    ForecastResult,
    ForecastState,
    NormalizedWindHour,
    PeakDayForecast,
    PeakProfile,
    SourceDescriptor,
    SourceFetch,
    SurfGrade,
    isoformat_utc,
)
from surf_forecast.domain.narrative import build_day_brief, build_peak_analysis
from surf_forecast.domain.presentation_labels import (
    CONDITION_LABELS,
    STATE_LABELS,
    is_analysis_band_window,
    wind_intensity_label,
)
from surf_forecast.domain.windows import URUGUAY_TZ, slot_in_calendar_analysis_window

SCHEMA_VERSION = "1.2.0"

WORTH_MIN_GRADE = SurfGrade.FAIR
WORTH_MAX = 3
# Same facing family only (e.g. S with S; never E with S).
ORIENTATION_COMPAT_MAX_DEG = 45.0
EMPTY_SPOTS_MESSAGE = "Ningún pico claro para ir."

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
        return CONDITION_LABELS.get(condition) or STATE_LABELS.get(
            state.value if isinstance(state, ForecastState) else str(state),
            "Sin condición",
        )
    state_value = state.value if isinstance(state, ForecastState) else state
    return STATE_LABELS.get(state_value, "Sin condición")


def orientations_compatible(left_deg: float, right_deg: float) -> bool:
    """True when two peaks face the same swell family (not contrapuestas)."""
    return circular_delta(left_deg, right_deg) <= ORIENTATION_COMPAT_MAX_DEG


def rank_worth_spots(
    peaks: list[PeakDayForecast],
    *,
    profile_by_id: dict[str, PeakProfile],
) -> list[dict[str, Any]]:
    """Fair+ peaks only, best-first, max WORTH_MAX, same orientation family."""
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
    if not candidates:
        return []

    def _spot(peak: PeakDayForecast) -> dict[str, Any]:
        profile = profile_by_id.get(peak.peak_id)
        name = profile.name if profile else peak.peak_id.replace("_", " ").title()
        cond = peak.condition.value if peak.condition else None
        return {
            "peak_id": peak.peak_id,
            "display_name": name,
            "condition": cond,
            "condition_label": condition_or_state_label(cond, peak.state),
            "reason_short": None,
        }

    best_peak = candidates[0][3]
    best_profile = profile_by_id.get(best_peak.peak_id)
    best_orient = best_profile.orientation_deg if best_profile is not None else None
    out: list[dict[str, Any]] = [_spot(best_peak)]
    if best_orient is None:
        # Without orientation we cannot vouch for extras.
        return out

    for _, _, _, peak in candidates[1:]:
        if len(out) >= WORTH_MAX:
            break
        profile = profile_by_id.get(peak.peak_id)
        if profile is None:
            continue
        if not orientations_compatible(best_orient, profile.orientation_deg):
            continue
        out.append(_spot(peak))
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
        "caption": "Rango estimado de ola surfeable",
    }


def favorable_window_from_peak(peak: PeakDayForecast | None) -> dict[str, Any] | None:
    """Franja favorable backed by the engine — never the full analysis band 06:00–20:00."""
    if peak is None or peak.best_window is None:
        return None
    window = peak.best_window
    start = window.start_at.astimezone(URUGUAY_TZ).strftime("%H:%M")
    end = window.end_at.astimezone(URUGUAY_TZ).strftime("%H:%M")
    mins = int(window.duration_minutes or 0)
    if is_analysis_band_window(start, end, mins):
        # Analysis band ≠ favorable fringe — omit the block.
        return None
    display = f"{start}–{end}"
    return {
        "start_local": start,
        "end_local": end,
        "wide": False,
        "display": display,
        "source_peak_id": peak.peak_id,
        "duration_minutes": mins,
        "start_at": isoformat_utc(window.start_at),
        "end_at": isoformat_utc(window.end_at),
    }


def go_window_from_peak(peak: PeakDayForecast | None) -> dict[str, Any] | None:
    """Alias kept for older callers — same as favorable_window_from_peak."""
    return favorable_window_from_peak(peak)


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
            wind_hours=result.wind_hours,
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
    wind_hours: list[NormalizedWindHour] | None = None,
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
            favorable_window=None,
            height=None,
            sources_ok=sources_ok,
            incomplete=True,
        )
        return {
            "local_date": stub.local_date,
            "display_title": _display_title(stub.local_date),
            "state": stub.state.value,
            "day_rating": None,
            "day_rating_absent_reason": "incomplete_forecast",
            "brief": _assemble_brief(
                label=label,
                condition=None,
                condition_label=STATE_LABELS["incomplete_forecast"],
                height=None,
                favorable_window=None,
                worth_spots=[],
                narrative=narrative,
                metrics=None,
                rating=None,
            ),
        }

    worth = rank_worth_spots(day.peaks, profile_by_id=profile_by_id)
    best_peak = None
    if worth:
        best_id = worth[0]["peak_id"]
        best_peak = next((p for p in day.peaks if p.peak_id == best_id), None)
    if best_peak is None and day.peaks:
        # Metrics may still come from the best resolved peak even without worth spots.
        resolved = [p for p in day.peaks if p.state is ForecastState.RESOLVED and p.condition]
        if resolved:
            best_peak = max(resolved, key=lambda p: GRADE_ORDER.index(p.condition))  # type: ignore[arg-type]
    height = height_summary_from_peak(best_peak if worth else None)
    window_done = (
        day.state is ForecastState.ANALYSIS_WINDOW_COMPLETED
        or day.headline_code == "analysis_window_completed"
    )
    # Closed analysis day: do not invent/show a new favorable fringe.
    favorable = None if window_done else favorable_window_from_peak(best_peak if worth else None)
    narrative = build_day_brief(
        day,
        profiles=profiles,
        worth_spots=worth,
        favorable_window=favorable,
        height=height,
        best_peak=best_peak if worth else None,
        sources_ok=sources_ok,
        incomplete=False,
    )
    rating, absent = build_day_rating(day)
    metrics = day_meteo_metrics(day, peak=best_peak, wind_hours=wind_hours or [])
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
        "brief": _assemble_brief(
            label=label,
            condition=condition,
            condition_label=condition_or_state_label(condition, day.state),
            height=height,
            favorable_window=favorable,
            worth_spots=worth,
            narrative=narrative,
            metrics=metrics,
            rating=rating,
        ),
    }


def day_meteo_metrics(
    day: DaySummary,
    *,
    peak: PeakDayForecast | None,
    wind_hours: list[NormalizedWindHour] | None = None,
) -> dict[str, Any] | None:
    """Structured swell/wind rows for day cards — only from real samples."""
    swell_rows: list[dict[str, Any]] = []
    if peak is not None:
        seen_dirs: set[str] = set()
        for slot in peak.reference_slots:
            dir_label = direction_label(slot.swell_direction_deg)
            period = slot.period_s
            if dir_label is None and period is None:
                continue
            key = dir_label or "?"
            if key in seen_dirs:
                continue
            seen_dirs.add(key)
            swell_rows.append(
                {
                    "dir_label": dir_label,
                    "period_s": period,
                    "period_display": f"{int(round(period))} s" if period is not None else None,
                }
            )
            if len(swell_rows) >= 2:
                break

    wind_block = _wind_metrics_for_day(day, wind_hours=wind_hours or [])

    if not swell_rows and wind_block is None:
        return None
    return {"swell": swell_rows, "wind": wind_block}


def _wind_metrics_for_day(
    day: DaySummary,
    *,
    wind_hours: list[NormalizedWindHour],
) -> dict[str, Any] | None:
    """Direction + speed range for the day (Lineup-style), backed by hourly wind."""
    day_hours = [
        hour
        for hour in wind_hours
        if hour.speed_kmh is not None
        and slot_in_calendar_analysis_window(hour.valid_at, day.local_date)
    ]
    day_hours.sort(key=lambda hour: hour.valid_at)

    rotation = day.wind_rotation or {}
    start_i = wind_intensity_label(rotation.get("start_intensity"))
    end_i = wind_intensity_label(rotation.get("end_intensity"))

    if len(day_hours) >= 2:
        mid = max(1, len(day_hours) // 2)
        early, late = day_hours[:mid], day_hours[mid:]
        early_seg = _wind_segment(early)
        late_seg = _wind_segment(late)
        if early_seg is None and late_seg is None:
            return None
        display = _format_wind_evolution(early_seg, late_seg)
        return {
            "display": display,
            "dir_display": display,  # primary card line includes km/h
            "intensity_display": _intensity_pair(start_i, end_i),
            "start_dir": early_seg["dir"] if early_seg else None,
            "end_dir": late_seg["dir"] if late_seg else None,
            "start_speed_min_kmh": early_seg["min_kmh"] if early_seg else None,
            "start_speed_max_kmh": early_seg["max_kmh"] if early_seg else None,
            "end_speed_min_kmh": late_seg["min_kmh"] if late_seg else None,
            "end_speed_max_kmh": late_seg["max_kmh"] if late_seg else None,
            "start_intensity": start_i,
            "end_intensity": end_i,
        }

    # Fallback: rotation dirs only (no speeds available)
    start_d = direction_label_16(rotation.get("start_direction_deg")) or direction_label(
        rotation.get("start_direction_deg")
    )
    end_d = direction_label_16(rotation.get("end_direction_deg")) or direction_label(
        rotation.get("end_direction_deg")
    )
    if not (start_d or end_d or start_i or end_i):
        return None
    if start_d and end_d and start_d != end_d:
        dir_display = f"{start_d} → {end_d}"
    else:
        dir_display = start_d or end_d
    return {
        "display": dir_display,
        "dir_display": dir_display,
        "intensity_display": _intensity_pair(start_i, end_i),
        "start_dir": start_d,
        "end_dir": end_d,
        "start_intensity": start_i,
        "end_intensity": end_i,
    }


def _wind_segment(hours: list[NormalizedWindHour]) -> dict[str, Any] | None:
    if not hours:
        return None
    speeds = [float(h.speed_kmh) for h in hours if h.speed_kmh is not None]
    if not speeds:
        return None
    # Representative direction: mean of degrees via unit vectors would be nicer;
    # for display use the mid sample's 16-point label.
    mid = hours[len(hours) // 2]
    dir_lab = direction_label_16(mid.direction_deg) or direction_label(mid.direction_deg)
    lo = int(round(min(speeds)))
    hi = int(round(max(speeds)))
    if hi < lo:
        lo, hi = hi, lo
    return {"dir": dir_lab, "min_kmh": lo, "max_kmh": hi}


def _format_wind_evolution(
    early: dict[str, Any] | None,
    late: dict[str, Any] | None,
) -> str:
    def _seg(seg: dict[str, Any]) -> str:
        direction = seg.get("dir") or "—"
        lo, hi = seg["min_kmh"], seg["max_kmh"]
        if lo == hi:
            return f"{direction} {lo} km/h"
        return f"{direction} {lo}–{hi} km/h"

    if early and late:
        left, right = _seg(early), _seg(late)
        if left == right:
            return left
        # Same dir: collapse to full-day range when labels match
        if early.get("dir") and early.get("dir") == late.get("dir"):
            lo = min(early["min_kmh"], late["min_kmh"])
            hi = max(early["max_kmh"], late["max_kmh"])
            direction = early["dir"]
            if lo == hi:
                return f"{direction} {lo} km/h"
            return f"{direction} {lo}–{hi} km/h"
        return f"{left} → {right}"
    if early:
        return _seg(early)
    if late:
        return _seg(late)
    return "n/d"


def _intensity_pair(start_i: str | None, end_i: str | None) -> str | None:
    if start_i and end_i and start_i != end_i:
        return f"{start_i.capitalize()} → {end_i}"
    if start_i or end_i:
        return (start_i or end_i or "").capitalize()
    return None


def _assemble_brief(
    *,
    label: str,
    condition: str | None,
    condition_label: str,
    height: dict[str, Any] | None,
    favorable_window: dict[str, Any] | None,
    worth_spots: list[dict[str, Any]],
    narrative: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    rating: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "label": label,
        "condition": condition,
        "condition_label": narrative.get("condition_label") or condition_label,
        "height": height,
        "metrics": metrics,
        "rating": rating,
        "analysis": narrative.get("analysis") or narrative.get("body"),
        "best_peak": narrative.get("best_peak"),
        "favorable_window": favorable_window,
        "limitations": narrative.get("limitations") or [],
        # legacy aliases (consumers / smoke)
        "headline": narrative.get("headline"),
        "body": narrative.get("analysis") or narrative.get("body"),
        "caution": (narrative.get("limitations") or [None])[0],
        "go_window": favorable_window,
        "worth_spots": worth_spots,
        "empty_spots_message": None if worth_spots else EMPTY_SPOTS_MESSAGE,
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
