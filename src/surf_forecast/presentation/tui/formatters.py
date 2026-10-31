"""Pure display hygiene formatters (no Textual, no domain evaluation)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

_CONFIDENCE_ES = {
    "high": "alta",
    "medium": "media",
    "low": "baja",
    "alta": "alta",
    "media": "media",
    "baja": "baja",
}


def format_score_num(score: float) -> str:
    return f"{float(score):.1f}".replace(".", ",")


def format_stars(score: float | None) -> str:
    """Legacy score path — rounds down to whole stars (no half glyphs)."""
    if score is None:
        return ""
    full = max(0, min(5, int(float(score))))
    return "★" * full + "☆" * (5 - full)


def format_stars_from_grade(condition: str | None) -> str:
    """Stars derived only from grade (brief §7)."""
    from surf_forecast.domain.presentation_labels import stars_for_grade

    n = stars_for_grade(condition)
    if n is None:
        return "—"
    return "★" * n + "☆" * (5 - n)


def format_meters_range(minimum_m: float | None, maximum_m: float | None) -> str:
    if minimum_m is not None and maximum_m is not None:
        lo = float(minimum_m)
        hi = float(maximum_m)
        lo_s = f"{lo:.1f}".replace(".", ",")
        hi_s = f"{hi:.1f}".replace(".", ",")
        if lo_s == hi_s:
            return f"{lo_s} m"
        return f"{lo_s}–{hi_s} m"
    return "—"


def format_meters_point(point_m: float | None, *, approx: bool = False) -> str:
    if point_m is None:
        return "—"
    prefix = "~" if approx else ""
    return f"{prefix}{float(point_m):.1f} m".replace(".", ",")


def format_size_dict(size: dict[str, Any] | None) -> str:
    size = size or {}
    if size.get("minimum_m") is not None and size.get("maximum_m") is not None:
        return format_meters_range(size.get("minimum_m"), size.get("maximum_m"))
    if size.get("point_m") is not None:
        return format_meters_point(size.get("point_m"), approx=True)
    return "—"


def format_period_s(period: float | None) -> str:
    if period is None:
        return "—"
    value = int(round(float(period)))
    if value <= 0:
        return "—"
    return f"{value} s"


def format_wind(
    *,
    dir_label: str | None = None,
    intensity: str | None = None,
    speed_kmh: float | None = None,
) -> str:
    parts: list[str] = []
    if dir_label:
        parts.append(str(dir_label))
    if intensity:
        parts.append(str(intensity))
    if speed_kmh is not None:
        parts.append(f"{int(round(float(speed_kmh)))} km/h")
    return " ".join(parts) if parts else "Viento n/d"


def format_hhmm_local(value: str | datetime | None) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    text = str(value).strip()
    if not text:
        return "—"
    # ISO-like: 2026-10-16T06:00:00-03:00 or ...06:00:00
    if "T" in text:
        try:
            # Prefer fromisoformat after trimming timezone colon quirks
            cleaned = text.replace("Z", "+00:00")
            dt = datetime.fromisoformat(cleaned)
            return dt.strftime("%H:%M")
        except ValueError:
            # Fallback: take HH:MM after T
            after = text.split("T", 1)[1]
            if len(after) >= 5 and after[2] == ":":
                return after[:5]
    if len(text) >= 5 and text[2] == ":":
        return text[:5]
    return text


def format_confidence(level: str | None) -> str:
    if not level:
        return "—"
    key = str(level).strip().lower()
    return _CONFIDENCE_ES.get(key, str(level))


def format_best_window(window: dict[str, Any] | None) -> str:
    """Primary best-window line for View B (never ISO-first / minute-led when wide)."""
    if not window:
        return "No hay una ventana clara respaldada por el motor para este pico."
    start = format_hhmm_local(window.get("start_at"))
    end = format_hhmm_local(window.get("end_at"))
    duration = window.get("duration_minutes")
    wide = False
    try:
        mins = int(duration) if duration is not None else 0
    except (TypeError, ValueError):
        mins = 0
    if mins >= 6 * 60:
        wide = True
    # Full analysis band heuristic: 06:00–20:00 → 14h = 840 min
    if start == "06:00" and end in {"20:00", "20:00"}:
        wide = True
    if wide:
        return f"Ventana amplia (día completo)  {start}–{end}"
    if mins > 0:
        human = f"{mins // 60} h" if mins % 60 == 0 and mins >= 60 else f"{mins} min"
        return f"★ {start}–{end}  ({human})"
    return f"★ {start}–{end}"


def format_rating_block(rating: dict[str, Any] | None, absent: str | None = None) -> str:
    if not rating:
        reason = absent or "sin grado evaluable"
        reason = reason.replace("Sin valoración:", "").replace("Sin valoración —", "").strip(" —:")
        return f"Sin valoración\n{reason}"
    score = float(rating["score"])
    lines = [format_stars(score), f"{format_score_num(score)} / 5"]
    caption = rating.get("caption") or ""
    if caption:
        lines.append(str(caption))
    return "\n".join(lines)


def format_analysis_block(analysis: dict[str, Any] | None) -> str:
    if not analysis:
        return ""
    sentences = analysis.get("sentences") or []
    if not sentences:
        return analysis.get("text") or ""
    order = {"fact": 0, "interpretation": 1, "limitation": 2}
    sorted_sentences = sorted(sentences, key=lambda s: order.get(s.get("kind", "fact"), 9))
    prefixes = {"fact": "≈", "interpretation": "◇", "limitation": "!"}
    lines = []
    for sentence in sorted_sentences:
        kind = sentence.get("kind", "fact")
        prefix = prefixes.get(kind, "·")
        lines.append(f"{prefix} {sentence.get('text', '')}")
    return "\n".join(lines)


def format_header(
    *,
    data_updated: str | None,
    query_local: str | None,
    status: str,
    horizon: str,
) -> str:
    data = data_updated or "n/d"
    query = query_local or "—"
    # Compact single-purpose header (app title lives in the window chrome).
    return f"Pronóstico {horizon}   ·   Datos: {data}   ·   Consulta: {query}   ·   {status}"


def format_day_chip(day: dict[str, Any]) -> str:
    title = day.get("display_title") or day.get("local_date") or ""
    short = title
    for full, abbr in (
        ("Lunes", "Lun"),
        ("Martes", "Mar"),
        ("Miércoles", "Mié"),
        ("Jueves", "Jue"),
        ("Viernes", "Vie"),
        ("Sábado", "Sáb"),
        ("Domingo", "Dom"),
    ):
        if title.startswith(full):
            short = abbr + title[len(full) :]
            break
    rating = day.get("day_rating")
    if rating:
        return f"{short}  {format_score_num(float(rating['score']))}"
    return f"{short}  —"


def condition_role(label: str | None) -> str:
    """Map visible label / chip text → CSS role class."""
    text = (label or "").lower()
    if "muy buena" in text:
        return "cond-muy-buena"
    if text == "buena" or text.startswith("buena"):
        return "cond-buena"
    if "razonable" in text:
        return "cond-razonable"
    if "pequeñ" in text:
        return "cond-pequenas"
    if "sin olas" in text or "sin datos" in text:
        return "cond-sin-olas"
    if "incierto" in text:
        return "cond-uncertain"
    if "incompleto" in text or "cerrada" in text:
        return "cond-incomplete"
    # Legacy mockup labels (transitional)
    if "oportunidad" in text:
        return "cond-buena"
    if "surfeable" in text:
        return "cond-razonable"
    if "variable" in text:
        return "cond-pequenas"
    if "pocas" in text:
        return "cond-sin-olas"
    return "cond-neutral"


def condition_role_from_id(condition: str | None) -> str:
    mapping = {
        "very_good": "cond-muy-buena",
        "good": "cond-buena",
        "fair": "cond-razonable",
        "small_but_surfable": "cond-pequenas",
        "no_surfable_waves": "cond-sin-olas",
    }
    if not condition:
        return "cond-neutral"
    return mapping.get(str(condition).strip().lower(), "cond-neutral")
