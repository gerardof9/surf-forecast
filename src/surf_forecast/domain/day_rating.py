"""Ordinal SurfGrade → 1–5 display encoding (presentation only).

Scale admits 0.5 steps. Method `best_resolved_grade_map_v2`:
- Base score from resolved SurfGrade (1/2/3/4/5).
- Subtract 0.5 when the source peak has low confidence or a provisional_profile
  confidence cap (deterministic reliability adjustment; does not re-score meteorology).
"""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.models import (
    ConfidenceLevel,
    DaySummary,
    ForecastState,
    GRADE_ORDER,
    PeakDayForecast,
    SurfGrade,
)

METHOD = "best_resolved_grade_map_v2"

GRADE_TO_SCORE: dict[SurfGrade, float] = {
    SurfGrade.NO_SURFABLE_WAVES: 1.0,
    SurfGrade.SMALL_BUT_SURFABLE: 2.0,
    SurfGrade.FAIR: 3.0,
    SurfGrade.GOOD: 4.0,
    SurfGrade.VERY_GOOD: 5.0,
}

SCORE_CAPTIONS: dict[float, str] = {
    5.0: "Condiciones muy favorables en el mejor pico evaluado",
    4.5: "Buenas condiciones, con alguna reserva de confianza",
    4.0: "Buenas condiciones en el mejor pico evaluado",
    3.5: "Condiciones surfeables, con limitaciones",
    3.0: "Condiciones surfeables, con limitaciones",
    2.5: "Oportunidad limitada / variable",
    2.0: "Oportunidad limitada / variable",
    1.5: "Pocas olas en el mejor pico evaluado",
    1.0: "Pocas olas en el mejor pico evaluado",
}


def score_for_grade(grade: SurfGrade | None) -> float | None:
    if grade is None:
        return None
    return GRADE_TO_SCORE.get(grade)


def _is_rated_peak(peak: PeakDayForecast) -> bool:
    """Resolved grade available — window-completed must not block a day score."""
    if peak.condition is None:
        return False
    if peak.state is ForecastState.RESOLVED:
        return True
    # Keep rating when slots were evaluated but day banner is window-completed.
    if peak.state is ForecastState.ANALYSIS_WINDOW_COMPLETED:
        return True
    return False


def _apply_reliability_half_step(score: float, peak: PeakDayForecast) -> float:
    caps = list(peak.confidence.caps) if peak.confidence else []
    low = peak.confidence is not None and peak.confidence.level is ConfidenceLevel.LOW
    provisional = "provisional_profile" in caps
    if low or provisional:
        return max(1.0, score - 0.5)
    return score


def build_peak_rating(peak: PeakDayForecast) -> dict[str, Any] | None:
    if not _is_rated_peak(peak):
        return None
    base = score_for_grade(peak.condition)
    if base is None:
        return None
    score = _apply_reliability_half_step(base, peak)
    return {
        "score": score,
        "source_peak_id": peak.peak_id,
        "caption": SCORE_CAPTIONS.get(score) or SCORE_CAPTIONS.get(base),
        "method": METHOD,
        "glyph_steps": score,
    }


def build_day_rating(day: DaySummary) -> tuple[dict[str, Any] | None, str | None]:
    """Return (rating, absent_reason). Rating from best resolved-grade peak only."""
    resolved = [peak for peak in day.peaks if _is_rated_peak(peak)]
    if not resolved:
        return None, "Ningún pico con grado evaluable para este día."

    def _rank(peak: PeakDayForecast) -> tuple[int, int]:
        grade = peak.condition or SurfGrade.NO_SURFABLE_WAVES
        highlight = 1 if (peak.highlighted or peak.peak_id in day.best_peak_ids) else 0
        return (GRADE_ORDER.index(grade), highlight)

    best = max(resolved, key=_rank)
    rating = build_peak_rating(best)
    return rating, None
