"""Template-based Spanish day brief (no LLM) — practical Lineup-style analysis."""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.evolution_samples import sample_evolution
from surf_forecast.domain.models import (
    DaySummary,
    ForecastState,
    PeakDayForecast,
    PeakProfile,
    ProfileStatus,
    SurfGrade,
)
from surf_forecast.domain.presentation_labels import (
    CONDITION_LABELS,
    STATE_LABELS,
    orientation_sector,
    swell_trend_predicate,
    wind_intensity_label,
)

METHOD = "template_v4"
METHOD_PEAK = "template_v1"

_BAND_ES = {
    "morning": "por la mañana",
    "midday": "al mediodía",
    "afternoon": "por la tarde",
}

_GRADE_RANK = {
    SurfGrade.NO_SURFABLE_WAVES: 0,
    SurfGrade.SMALL_BUT_SURFABLE: 1,
    SurfGrade.FAIR: 2,
    SurfGrade.GOOD: 3,
    SurfGrade.VERY_GOOD: 4,
}


def build_day_brief(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    worth_spots: list[dict[str, Any]],
    favorable_window: dict[str, Any] | None,
    height: dict[str, Any] | None,
    best_peak: PeakDayForecast | None = None,
    sources_ok: bool = True,
    incomplete: bool = False,
) -> dict[str, Any]:
    """Sectioned DayBrief content for home cards + practical analysis."""
    if incomplete:
        return {
            "condition_label": STATE_LABELS["incomplete_forecast"],
            "analysis": (
                "Todavía no hay datos suficientes para armar un análisis de este día; "
                "no se reutiliza el día anterior."
            ),
            "best_peak": None,
            "limitations": [
                "Pronóstico incompleto: faltan datos propios de esta fecha; no se reutiliza el día anterior."
            ],
            "headline": "Datos incompletos para este día.",
            "body": (
                "Todavía no hay datos suficientes para armar un análisis de este día; "
                "no se reutiliza el día anterior."
            ),
            "caution": "Pronóstico incompleto: faltan datos propios de esta fecha.",
        }

    profile_by_id = {p.peak_id: p for p in profiles}
    window_done = (
        day.state is ForecastState.ANALYSIS_WINDOW_COMPLETED
        or day.headline_code == "analysis_window_completed"
    )

    condition_label = _day_condition_label(day)
    analysis = _build_analysis(
        day,
        height=height,
        favorable_window=favorable_window,
        best_peak=best_peak,
        worth_spots=worth_spots,
        profile_by_id=profile_by_id,
        window_done=window_done,
    )
    best_block = _build_best_peak_block(worth_spots, best_peak, profile_by_id)
    limitations = _build_limitations(
        day,
        profiles=profiles,
        sources_ok=sources_ok,
        window_done=window_done,
        has_peaks=bool(day.peaks),
    )

    headline = condition_label or "Sin condición"
    body = analysis
    caution = limitations[0] if limitations else None

    return {
        "condition_label": condition_label,
        "analysis": analysis,
        "best_peak": best_block,
        "limitations": limitations,
        "headline": headline,
        "body": body,
        "caution": caution,
    }


def _build_analysis(
    day: DaySummary,
    *,
    height: dict[str, Any] | None,
    favorable_window: dict[str, Any] | None,
    best_peak: PeakDayForecast | None,
    worth_spots: list[dict[str, Any]],
    profile_by_id: dict[str, PeakProfile],
    window_done: bool,
) -> str:
    """Short labelled rows (brief §6) — max ~72 chars per line, no paragraphs."""
    rows: list[tuple[str, str]] = []

    oleaje = _swell_row(day, best_peak)
    if oleaje:
        rows.append(("Oleaje", oleaje))

    viento = _wind_row(day)
    if viento:
        rows.append(("Viento", viento))

    mejor = _timing_row(day, best_peak=best_peak, favorable_window=favorable_window, window_done=window_done)
    if mejor:
        rows.append(("Mejor", mejor))

    lectura = _form_sentence(day)
    if lectura:
        # Strip trailing period for row value consistency
        rows.append(("Lectura", lectura.rstrip(".")))

    if not rows:
        if day.state is ForecastState.INCOMPLETE_FORECAST or not day.peaks:
            return _fmt_rows([("Estado", "Pocos indicios claros de oleaje y viento.")])
        return _fmt_rows([("Estado", "Condiciones mezcladas; el viento marca la diferencia.")])

    return _fmt_rows(rows[:4])


def _fmt_rows(rows: list[tuple[str, str]]) -> str:
    label_w = 8
    lines: list[str] = []
    for label, value in rows:
        text = value.strip()
        if len(text) > 64:
            text = text[:61].rstrip() + "…"
        lines.append(f"{label:<{label_w}} {text}")
    return "\n".join(lines)


def _swell_row(day: DaySummary, best_peak: PeakDayForecast | None) -> str | None:
    bits: list[str] = []
    if best_peak is not None:
        for slot in best_peak.reference_slots:
            if slot.swell_direction_deg is not None:
                from surf_forecast.domain.evolution_samples import direction_label

                d = direction_label(slot.swell_direction_deg)
                if d:
                    bits.append(f"Del {d}")
                break
        for slot in best_peak.reference_slots:
            if slot.period_s is not None and float(slot.period_s) > 0:
                bits.append(f"{int(round(float(slot.period_s)))} s")
                break
    if day.swell_trend is not None and day.swell_trend.state.value != "unsupported":
        pred = swell_trend_predicate(day.swell_trend.state.value)
        if pred:
            bits.append(pred)
    return ", ".join(bits) if bits else None


def _wind_row(day: DaySummary) -> str | None:
    rotation = day.wind_rotation or {}
    start_i = wind_intensity_label(rotation.get("start_intensity"))
    end_i = wind_intensity_label(rotation.get("end_intensity"))
    start_d = _dir_label(rotation.get("start_direction_deg"))
    end_d = _dir_label(rotation.get("end_direction_deg"))
    direction = None
    if start_d and end_d and start_d != end_d:
        direction = f"{start_d}→{end_d}"
    else:
        direction = start_d or end_d
    if start_i and end_i and start_i != end_i:
        intensity = f"{start_i}→{end_i}"
    else:
        intensity = start_i or end_i
    if direction and intensity:
        return f"{direction} {intensity}."
    if intensity:
        return f"{intensity}."
    if direction:
        return f"{direction}."
    return None


def _timing_row(
    day: DaySummary,
    *,
    best_peak: PeakDayForecast | None,
    favorable_window: dict[str, Any] | None,
    window_done: bool,
) -> str | None:
    if window_done:
        return "Ventana de análisis cerrada; sin franja nueva."

    band = _best_band_from_peak(best_peak)
    if favorable_window and favorable_window.get("display"):
        display = favorable_window["display"]
        band_from_clock = _band_from_clock(favorable_window.get("start_local"))
        if band_from_clock:
            return f"{band_from_clock.capitalize()}, {display}."
        return f"Franja {display}."

    if band:
        return f"{_BAND_ES[band].capitalize()}."

    if best_peak is not None:
        samples = sample_evolution(best_peak)
        if len(samples) >= 2:
            ranked = sorted(
                (s for s in samples if s.get("size_point_m") is not None),
                key=lambda s: float(s["size_point_m"]),
                reverse=True,
            )
            if ranked:
                top = ranked[0].get("band")
                if top in _BAND_ES:
                    return f"Mayor tamaño {_BAND_ES[top]}."
    return None


def _best_band_from_peak(peak: PeakDayForecast | None) -> str | None:
    if peak is None:
        return None
    from surf_forecast.domain.windows import URUGUAY_TZ

    by_band: dict[str, int] = {}
    for slot in peak.reference_slots:
        if slot.condition_grade is None:
            continue
        local = slot.valid_at.astimezone(URUGUAY_TZ)
        hour = local.hour
        for name, start, end in (("morning", 6, 11), ("midday", 11, 15), ("afternoon", 15, 21)):
            if start <= hour < end:
                by_band[name] = max(by_band.get(name, -1), _GRADE_RANK.get(slot.condition_grade, 0))
                break
    if by_band:
        return max(by_band.items(), key=lambda item: item[1])[0]
    return None


def _band_from_clock(start_local: str | None) -> str | None:
    if not start_local or ":" not in str(start_local):
        return None
    try:
        hour = int(str(start_local).split(":", 1)[0])
    except ValueError:
        return None
    if 6 <= hour < 11:
        return _BAND_ES["morning"]
    if 11 <= hour < 15:
        return _BAND_ES["midday"]
    if 15 <= hour < 21:
        return _BAND_ES["afternoon"]
    return None


def _size_sentence(height: dict[str, Any] | None) -> str | None:
    if not height:
        return None
    lo = height.get("minimum_m")
    hi = height.get("maximum_m")
    if lo is None or hi is None:
        return None
    lo_f, hi_f = float(lo), float(hi)
    mid = (lo_f + hi_f) / 2.0
    body = _body_height_phrase(mid)
    lo_s = f"{lo_f:.1f}".replace(".", ",")
    hi_s = f"{hi_f:.1f}".replace(".", ",")
    if body:
        return f"Tamaño estimado {lo_s}–{hi_s} m ({body})."
    return f"Tamaño estimado {lo_s}–{hi_s} m."


def _body_height_phrase(meters: float) -> str | None:
    """Approximate body-height reading used in local surf reports."""
    if meters < 0.4:
        return "alrededor de la rodilla o menos"
    if meters < 0.7:
        return "entre cadera y hombro aprox."
    if meters < 1.0:
        return "alrededor del pecho aprox."
    if meters < 1.3:
        return "entre pecho y algo por encima de la cabeza aprox."
    return "por encima de la cabeza en las mejores series aprox."


def _form_sentence(day: DaySummary) -> str | None:
    rotation = day.wind_rotation or {}
    start_i = wind_intensity_label(rotation.get("start_intensity"))
    end_i = wind_intensity_label(rotation.get("end_intensity"))
    intensities = [i for i in (start_i, end_i) if i]
    if not intensities:
        return None
    if any(i in {"fuerte", "muy fuerte"} for i in intensities):
        return "Con ese viento la forma tiende a verse más picada o irregular."
    if all(i == "suave" for i in intensities):
        return "Con viento suave la forma podría verse relativamente más ordenada."
    if all(i in {"suave", "moderado"} for i in intensities):
        return "Con viento moderado la forma podría verse relativamente más ordenada."
    return None


def _spot_orientation_sentence(
    worth_spots: list[dict[str, Any]],
    profile_by_id: dict[str, PeakProfile],
) -> str | None:
    if not worth_spots:
        return "No hay un pico claro por encima del umbral surfeable para recomendar."
    top = worth_spots[0]
    profile = profile_by_id.get(top["peak_id"])
    name = top.get("display_name") or top["peak_id"]
    if profile is None:
        return f"Mejor opción estimada: {name}."
    sector = orientation_sector(profile.orientation_deg)
    extras = [s.get("display_name") for s in worth_spots[1:] if s.get("display_name")]
    if extras:
        also = ", ".join(extras)
        return (
            f"Mejor lectura en playas orientadas al {sector} "
            f"({name}; también {also})."
        )
    return f"Mejor lectura en playas orientadas al {sector} ({name})."


def _dir_label(degrees: Any) -> str | None:
    if degrees is None:
        return None
    try:
        value = float(degrees)
    except (TypeError, ValueError):
        return None
    from surf_forecast.domain.evolution_samples import direction_label

    return direction_label(value)


def _build_best_peak_block(
    worth_spots: list[dict[str, Any]],
    best_peak: PeakDayForecast | None,
    profile_by_id: dict[str, PeakProfile],
) -> dict[str, Any] | None:
    if not worth_spots:
        return None
    top = worth_spots[0]
    peak_id = top["peak_id"]
    name = top.get("display_name") or peak_id
    profile = profile_by_id.get(peak_id)
    reason = _evidence_based_reason(profile)
    return {
        "peak_id": peak_id,
        "display_name": name,
        "condition": top.get("condition"),
        "condition_label": top.get("condition_label"),
        "reason": reason,
    }


def _evidence_based_reason(profile: PeakProfile | None) -> str | None:
    """Only orientation from profile — never invent wind shelter claims."""
    if profile is None:
        return None
    sector = orientation_sector(profile.orientation_deg)
    return f"Orientación ~{sector}"


def _build_limitations(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    sources_ok: bool,
    window_done: bool,
    has_peaks: bool,
) -> list[str]:
    notes: list[str] = []
    if window_done:
        notes.append(
            "Ventana de análisis finalizada (06:00–20:00): no se calcula una nueva franja favorable."
        )
    if any(p.status is ProfileStatus.PROVISIONAL for p in profiles):
        notes.append("Perfiles aún no calibrados en campo.")
    if not sources_ok:
        notes.append("Fuentes incompletas: el análisis usa solo los datos disponibles.")
    if not has_peaks and day.state is ForecastState.INCOMPLETE_FORECAST:
        notes.append("Faltan datos esenciales para valorar picos.")
    # Rain/weather deliberately omitted: no precipitation source in the engine yet.
    if not notes:
        notes.append("Estimación orientativa: no garantiza olas ni seguridad en el agua.")
    return notes


def _day_condition_label(day: DaySummary) -> str:
    from surf_forecast.domain.models import GRADE_ORDER

    resolved = [
        p.condition
        for p in day.peaks
        if p.condition is not None and p.state is ForecastState.RESOLVED
    ]
    if resolved:
        best = max(resolved, key=lambda g: GRADE_ORDER.index(g))
        return CONDITION_LABELS.get(best.value, STATE_LABELS.get(day.state.value, "Sin condición"))
    return STATE_LABELS.get(day.state.value, "Sin condición")


def build_day_analysis(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    sources_ok: bool = True,
) -> dict[str, Any]:
    """Legacy bag for transitional checks; prefer build_day_brief."""
    brief = build_day_brief(
        day,
        profiles=profiles,
        worth_spots=[],
        favorable_window=None,
        height=None,
        sources_ok=sources_ok,
    )
    sentences: list[dict[str, str]] = [
        {"kind": "interpretation", "text": brief.get("analysis") or ""},
    ]
    for lim in brief.get("limitations") or []:
        sentences.append({"kind": "limitation", "text": lim})
    supported = bool(day.peaks) and day.state is not ForecastState.INCOMPLETE_FORECAST
    text = " ".join(s["text"] for s in sentences if s["text"])
    return {"text": text, "sentences": sentences, "supported": supported, "method": METHOD}


def build_peak_analysis(
    peak: PeakDayForecast,
    *,
    profile: PeakProfile | None,
) -> tuple[dict[str, Any] | None, str | None]:
    facts: list[dict[str, str]] = []
    interpretations: list[dict[str, str]] = []
    limitations: list[dict[str, str]] = []

    if peak.state is ForecastState.INCOMPLETE_FORECAST and peak.condition is None and peak.size is None:
        return None, "Hechos del pico insuficientes para un análisis."

    if peak.condition is not None:
        label = CONDITION_LABELS.get(peak.condition.value)
        if label:
            facts.append({"kind": "fact", "text": f"Condición estimada del pico: {label}."})

    if peak.size is not None:
        facts.append(
            {
                "kind": "fact",
                "text": (
                    f"Tamaño surfeable estimado ~{peak.size.point_m:.1f} m "
                    f"(rango {peak.size.minimum_m:.1f}–{peak.size.maximum_m:.1f} m)."
                ),
            }
        )

    if profile is not None:
        sector = orientation_sector(profile.orientation_deg)
        interpretations.append(
            {
                "kind": "interpretation",
                "text": f"Perfil {profile.name}: orientación ~{sector}.",
            }
        )
        if profile.status is ProfileStatus.PROVISIONAL:
            limitations.append(
                {
                    "kind": "limitation",
                    "text": "Perfil provisional: no tratar la exposición como calibrada.",
                }
            )

    if peak.state is ForecastState.UNCERTAIN:
        limitations.append(
            {
                "kind": "limitation",
                "text": "Estado incierto: el rango estimado cruza umbrales o faltan certezas.",
            }
        )

    if "analysis_window_completed" in (peak.reason_codes or []):
        limitations.append(
            {
                "kind": "limitation",
                "text": "Ventana de análisis del día finalizada: no hay nueva franja favorable.",
            }
        )

    sentences = facts + interpretations + limitations
    if not facts and not interpretations:
        return None, "Hechos del pico insuficientes para un análisis."

    return {
        "text": " ".join(s["text"] for s in sentences),
        "sentences": sentences,
        "supported": True,
        "method": METHOD_PEAK,
    }, None
