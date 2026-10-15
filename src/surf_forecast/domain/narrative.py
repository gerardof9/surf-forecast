"""Template-based Spanish day brief and legacy peak analysis (no LLM)."""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.models import DaySummary, ForecastState, PeakDayForecast, PeakProfile, ProfileStatus

METHOD = "template_v2"
METHOD_PEAK = "template_v1"

_TREND_ES = {
    "building": "oleaje en aumento",
    "peaking": "oleaje cerca del pico",
    "dropping": "oleaje en descenso",
    "steady": "oleaje relativamente estable",
    "unsupported": "tendencia de oleaje no determinada",
}

_DISCLAIMER = "Son estimaciones, no una garantía de olas ni de seguridad en el agua."


def build_day_brief(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    worth_spots: list[dict[str, Any]],
    go_window: dict[str, Any] | None,
    height: dict[str, Any] | None,
    sources_ok: bool = True,
    incomplete: bool = False,
) -> dict[str, str | None]:
    """Plain-Spanish DayBrief narrative (headline + body + optional caution)."""
    if incomplete:
        return {
            "headline": "Datos incompletos para este día.",
            "body": (
                "Aún no hay un brief usable para mañana con la información disponible. "
                f"{_DISCLAIMER}"
            ),
            "caution": "No se copió el día de hoy: faltan datos propios de esta fecha.",
        }

    profile_by_id = {p.peak_id: p for p in profiles}
    window_done = (
        day.state is ForecastState.ANALYSIS_WINDOW_COMPLETED
        or day.headline_code == "analysis_window_completed"
    )

    cond_label = _day_condition_label(day)
    if worth_spots:
        names = [s["display_name"] for s in worth_spots]
        best_name = names[0]
        if len(names) == 1:
            where = f"Conviene priorizar {best_name}"
        else:
            where = f"Conviene priorizar {best_name}" + (
                f" (también mirar {', '.join(names[1:])})" if len(names) > 1 else ""
            )
        if go_window and go_window.get("display"):
            when = go_window["display"]
            if go_window.get("wide"):
                headline = f"{cond_label}: {best_name}; ventana amplia."
            else:
                headline = f"{cond_label}: mejor en {best_name}."
            timing_sentence = f"{where}. {when}."
        else:
            headline = f"{cond_label}: priorizar {best_name}."
            timing_sentence = f"{where}; no hay una hora clara de entrada."
    else:
        headline = f"{cond_label}: ningún pico claro para ir."
        timing_sentence = "Ningún pico pasa el umbral para recomendar una playa hoy."

    parts: list[str] = []
    if day.swell_trend is not None and day.swell_trend.state.value != "unsupported":
        trend = _TREND_ES.get(day.swell_trend.state.value, day.swell_trend.state.value)
        parts.append(f"El oleaje viene {trend}.")

    rotation = day.wind_rotation or {}
    start_i = rotation.get("start_intensity")
    end_i = rotation.get("end_intensity")
    if start_i and end_i:
        if start_i == end_i:
            parts.append(f"Viento estimado {start_i} durante el día.")
        else:
            parts.append(f"Viento de {start_i} al inicio hacia {end_i} más tarde.")

    if height and height.get("display"):
        parts.append(f"Altura surfeable estimada en el mejor pico: {height['display']}.")

    parts.append(timing_sentence)

    if worth_spots:
        best = worth_spots[0]
        profile = profile_by_id.get(best["peak_id"])
        if profile is not None:
            parts.append(f"{profile.name} encaja mejor con el oleaje/viento de la evaluación.")

    parts.append(_DISCLAIMER)
    body = " ".join(parts)

    caution: str | None = None
    if window_done:
        caution = "La ventana de análisis de hoy ya cerró; tomá el brief como referencia, no como hora nueva."
    elif any(p.status is ProfileStatus.PROVISIONAL for p in profiles):
        caution = "Hay perfiles provisionales: tratá la lectura como orientativa."
    elif not sources_ok:
        caution = "Fuentes incompletas: el brief usa solo lo disponible."

    return {"headline": headline, "body": body, "caution": caution}


def build_day_analysis(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    sources_ok: bool = True,
) -> dict[str, Any]:
    """Legacy bag kept for transitional checks; prefer build_day_brief for presentation."""
    brief = build_day_brief(
        day,
        profiles=profiles,
        worth_spots=[],
        go_window=None,
        height=None,
        sources_ok=sources_ok,
    )
    sentences: list[dict[str, str]] = [
        {"kind": "interpretation", "text": brief["headline"] or ""},
        {"kind": "interpretation", "text": brief["body"] or ""},
    ]
    if brief.get("caution"):
        sentences.append({"kind": "limitation", "text": str(brief["caution"])})
    if not day.peaks:
        sentences.append(
            {"kind": "limitation", "text": "No hay picos evaluables para este día con los datos actuales."}
        )
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
        from surf_forecast.domain.presentation import CONDITION_LABELS

        label = CONDITION_LABELS.get(peak.condition.value, peak.condition.value)
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
        orient = _orientation_phrase(profile.orientation_deg)
        interpretations.append(
            {
                "kind": "interpretation",
                "text": f"Perfil {profile.name}: orientación ~{orient}.",
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
                "text": "Ventana de análisis del día finalizada: no hay nueva mejor hora propuesta.",
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


def _day_condition_label(day: DaySummary) -> str:
    from surf_forecast.domain.presentation import CONDITION_LABELS, STATE_LABELS

    resolved = [
        p.condition
        for p in day.peaks
        if p.condition is not None and p.state is ForecastState.RESOLVED
    ]
    if resolved:
        from surf_forecast.domain.models import GRADE_ORDER

        best = max(resolved, key=lambda g: GRADE_ORDER.index(g))
        return CONDITION_LABELS.get(best.value, best.value)
    return STATE_LABELS.get(day.state.value, day.state.value)


def _orientation_phrase(degrees: float) -> str:
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees % 360) / 45.0 + 0.5) % 8
    return f"{sectors[idx]} ({degrees:.0f}°)"
