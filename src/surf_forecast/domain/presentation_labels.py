"""Centralized Spanish presentation labels — never expose raw internal ids.

Unknown values MUST NOT be returned as the raw token; use a safe fallback
or None so callers can omit the phrase.

Vocabulary follows the active product scale (spec FR-019 / brief §7):
Muy buena · Buena · Razonable · Olas pequeñas pero surfeables · Sin olas surfeables.
"""

from __future__ import annotations

from typing import Any

# Full labels (prose / long form).
CONDITION_LABELS: dict[str, str] = {
    "no_surfable_waves": "Sin olas surfeables",
    "small_but_surfable": "Olas pequeñas pero surfeables",
    "fair": "Razonable",
    "good": "Buena",
    "very_good": "Muy buena",
}

# Compact chip text (UI badges).
CONDITION_CHIP_LABELS: dict[str, str] = {
    "no_surfable_waves": "Sin olas",
    "small_but_surfable": "Pequeñas",
    "fair": "Razonable",
    "good": "Buena",
    "very_good": "Muy buena",
}

# Full stars from grade only (brief §7) — never half stars.
GRADE_STARS: dict[str, int] = {
    "very_good": 5,
    "good": 4,
    "fair": 3,
    "small_but_surfable": 2,
    "no_surfable_waves": 0,
}

STATE_LABELS: dict[str, str] = {
    "resolved": "Resuelto",
    "uncertain": "Incierto",
    "incomplete_forecast": "Pronóstico incompleto",
    "analysis_window_completed": "Ventana de análisis finalizada",
}

STATE_CHIP_LABELS: dict[str, str] = {
    "uncertain": "Incierto",
    "incomplete_forecast": "Sin datos",
    "analysis_window_completed": "Cerrada",
}

WIND_INTENSITY_LABELS: dict[str, str] = {
    "light": "suave",
    "moderate": "moderado",
    "strong": "fuerte",
    "very_strong": "muy fuerte",
    "unknown": "indefinida",
}

SWELL_TREND_PREDICATES: dict[str, str] = {
    "building": "en aumento",
    "peaking": "en su pico",
    "dropping": "en descenso",
    "steady": "estable",
}

CONFIDENCE_LABELS: dict[str, str] = {
    "high": "alta",
    "medium": "media",
    "low": "baja",
}

UNKNOWN_LABEL = "no determinado"
ANALYSIS_WINDOW_BOUNDS = ("06:00", "20:00")
MISSING = "—"


def label_or_none(mapping: dict[str, str], value: str | None) -> str | None:
    """Return mapped Spanish label, or None if missing/unknown (never raw id)."""
    if value is None:
        return None
    key = str(value).strip().lower()
    if key not in mapping:
        return None
    return mapping[key]


def label_or_fallback(mapping: dict[str, str], value: str | None, *, fallback: str = UNKNOWN_LABEL) -> str:
    found = label_or_none(mapping, value)
    return found if found is not None else fallback


def condition_label(condition: str | None) -> str | None:
    return label_or_none(CONDITION_LABELS, condition)


def condition_chip(condition: str | None) -> str | None:
    return label_or_none(CONDITION_CHIP_LABELS, condition)


def stars_for_grade(condition: str | None) -> int | None:
    if condition is None:
        return None
    key = str(condition).strip().lower()
    if key not in GRADE_STARS:
        return None
    return GRADE_STARS[key]


def state_label(state: str | None) -> str | None:
    return label_or_none(STATE_LABELS, state)


def state_chip(state: str | None) -> str | None:
    return label_or_none(STATE_CHIP_LABELS, state) or state_label(state)


def wind_intensity_label(intensity: str | None) -> str | None:
    return label_or_none(WIND_INTENSITY_LABELS, intensity)


def swell_trend_predicate(trend: str | None) -> str | None:
    return label_or_none(SWELL_TREND_PREDICATES, trend)


def confidence_label(level: str | None) -> str | None:
    return label_or_none(CONFIDENCE_LABELS, level)


def is_analysis_band_window(start_local: str, end_local: str, duration_minutes: int) -> bool:
    """True when the window is (effectively) the full analysis band, not a tight favorable fringe."""
    if start_local == ANALYSIS_WINDOW_BOUNDS[0] and end_local == ANALYSIS_WINDOW_BOUNDS[1]:
        return True
    if duration_minutes >= 6 * 60:
        return True
    return False


def visible_text_has_internal_id(text: str) -> list[str]:
    """Return list of forbidden internal tokens found in visible text (for tests)."""
    forbidden = [
        "strong",
        "very_strong",
        "moderate",
        "light",
        "building",
        "peaking",
        "dropping",
        "steady",
        "unsupported",
        "no_surfable_waves",
        "small_but_surfable",
        "very_good",
        "analysis_window_completed",
        "incomplete_forecast",
        "Hs cruda",
        "template_v",
        "Buena oportunidad",
        "Surfeable",
    ]
    found: list[str] = []
    lower = text.lower()
    for token in forbidden:
        if token.lower() in lower:
            if token in {"good", "fair"}:
                continue
            found.append(token)
    return found


def orientation_sector(degrees: float) -> str:
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees % 360) / 45.0 + 0.5) % 8
    return sectors[idx]
