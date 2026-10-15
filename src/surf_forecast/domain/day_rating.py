"""Ordinal SurfGrade → 1–5 display encoding (presentation only)."""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.models import DaySummary, ForecastState, GRADE_ORDER, PeakDayForecast, SurfGrade

METHOD = "best_resolved_grade_map_v1"

GRADE_TO_SCORE: dict[SurfGrade, float] = {
    SurfGrade.NO_SURFABLE_WAVES: 1.0,
    SurfGrade.SMALL_BUT_SURFABLE: 2.0,
    SurfGrade.FAIR: 3.0,
    SurfGrade.GOOD: 4.0,
    SurfGrade.VERY_GOOD: 5.0,
}

SCORE_CAPTIONS: dict[float, str] = {
    5.0: "Condiciones muy favorables en el mejor pico evaluado",
    4.0: "Buenas condiciones en el mejor pico evaluado",
    3.0: "Condiciones surfeables, con limitaciones",
    2.0: "Oportunidad limitada / variable",
    1.0: "Pocas olas en el mejor pico evaluado",
}

_RESOLVED_OK = ForecastState.RESOLVED


def score_for_grade(grade: SurfGrade | None) -> float | None:
    if grade is None:
        return None
    return GRADE_TO_SCORE.get(grade)


def _is_resolved_rated(peak: PeakDayForecast) -> bool:
    return peak.state is _RESOLVED_OK and peak.condition is not None


def build_peak_rating(peak: PeakDayForecast) -> dict[str, Any] | None:
    if not _is_resolved_rated(peak):
        return None
    score = score_for_grade(peak.condition)
    if score is None:
        return None
    return {
        "score": score,
        "source_peak_id": peak.peak_id,
        "caption": SCORE_CAPTIONS.get(score),
        "method": METHOD,
        "glyph_steps": score,
    }


def build_day_rating(day: DaySummary) -> tuple[dict[str, Any] | None, str | None]:
    """Return (rating, absent_reason). Rating from best resolved peak only."""
    resolved = [peak for peak in day.peaks if _is_resolved_rated(peak)]
    if not resolved:
        return None, "Sin valoración: ningún pico con grado resuelto para este día."

    def _rank(peak: PeakDayForecast) -> tuple[int, int]:
        grade = peak.condition or SurfGrade.NO_SURFABLE_WAVES
        # Prefer engine best_peak_ids / highlighted, then GRADE_ORDER.
        highlight = 1 if (peak.highlighted or peak.peak_id in day.best_peak_ids) else 0
        return (GRADE_ORDER.index(grade), highlight)

    best = max(resolved, key=_rank)
    rating = build_peak_rating(best)
    return rating, None
