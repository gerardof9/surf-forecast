"""Template-based Spanish day/peak analysis (no LLM)."""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.models import DaySummary, ForecastState, PeakDayForecast, PeakProfile, ProfileStatus

METHOD = "template_v1"

_TREND_ES = {
    "building": "oleaje en aumento",
    "peaking": "oleaje cerca del pico",
    "dropping": "oleaje en descenso",
    "steady": "oleaje relativamente estable",
    "unsupported": "tendencia de oleaje no determinada",
}


def build_day_analysis(
    day: DaySummary,
    *,
    profiles: list[PeakProfile],
    sources_ok: bool = True,
) -> dict[str, Any]:
    facts: list[dict[str, str]] = []
    interpretations: list[dict[str, str]] = []
    limitations: list[dict[str, str]] = []
    profile_by_id = {p.peak_id: p for p in profiles}

    window_done = day.state is ForecastState.ANALYSIS_WINDOW_COMPLETED or day.headline_code == "analysis_window_completed"

    if day.swell_trend is not None and day.swell_trend.state.value != "unsupported":
        trend = _TREND_ES.get(day.swell_trend.state.value, day.swell_trend.state.value)
        facts.append({"kind": "fact", "text": f"Tendencia del oleaje en la ventana: {trend}."})

    rotation = day.wind_rotation or {}
    if rotation:
        start_i = rotation.get("start_intensity")
        end_i = rotation.get("end_intensity")
        if start_i and end_i:
            if start_i == end_i:
                facts.append(
                    {
                        "kind": "fact",
                        "text": f"Viento estimado de intensidad {start_i} a lo largo de la ventana de análisis.",
                    }
                )
            else:
                facts.append(
                    {
                        "kind": "fact",
                        "text": f"Viento estimado de intensidad {start_i} al inicio hacia {end_i} al cierre de la ventana.",
                    }
                )

    sizes = [
        peak.size
        for peak in day.peaks
        if peak.size is not None and peak.condition is not None
    ]
    if sizes:
        lo = min(s.minimum_m for s in sizes)
        hi = max(s.maximum_m for s in sizes)
        facts.append(
            {
                "kind": "fact",
                "text": (
                    f"Tamaño surfeable estimado entre los picos evaluados: "
                    f"aprox. {lo:.1f}–{hi:.1f} m (derivado; no es Hs cruda)."
                ),
            }
        )

    best_ids = day.best_peak_ids or []
    for peak_id in best_ids[:2]:
        profile = profile_by_id.get(peak_id)
        if profile is None:
            continue
        orient = _orientation_phrase(profile.orientation_deg)
        interpretations.append(
            {
                "kind": "interpretation",
                "text": f"{profile.name}: exposición orientada ~{orient} según perfil (no es un dato del modelo).",
            }
        )

    if window_done:
        limitations.append(
            {
                "kind": "limitation",
                "text": "La ventana de análisis de hoy (06:00–20:00 UYT) ya finalizó; no se propone una nueva mejor hora de entrada.",
            }
        )

    if any(p.status is ProfileStatus.PROVISIONAL for p in profiles):
        limitations.append(
            {
                "kind": "limitation",
                "text": "Hay perfiles provisionales: la interpretación de exposición no está calibrada en campo.",
            }
        )

    if not sources_ok:
        limitations.append(
            {
                "kind": "limitation",
                "text": "Fuentes incompletas o degradadas: el análisis se basa solo en lo disponible.",
            }
        )

    if not day.peaks:
        limitations.append(
            {
                "kind": "limitation",
                "text": "No hay picos evaluables para este día con los datos actuales.",
            }
        )
    elif not facts and not interpretations:
        limitations.append(
            {
                "kind": "limitation",
                "text": "Datos insuficientes para un análisis del día con hechos respaldados.",
            }
        )

    # Facts and interpretations first; limitations last (secondary weight).
    sentences = facts + interpretations + limitations
    supported = bool(facts or interpretations)
    text = " ".join(s["text"] for s in sentences)
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
        "method": METHOD,
    }, None


def _orientation_phrase(degrees: float) -> str:
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees % 360) / 45.0 + 0.5) % 8
    return f"{sectors[idx]} ({degrees:.0f}°)"
