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
    if score is None:
        return ""
    value = max(0.0, min(5.0, float(score)))
    full = int(value)
    half = (value - full) >= 0.5
    empty = 5 - full - (1 if half else 0)
    return "★" * full + ("◐" if half else "") + "☆" * empty


def format_meters_range(minimum_m: float | None, maximum_m: float | None) -> str:
    if minimum_m is not None and maximum_m is not None:
        return f"{float(minimum_m):.1f}–{float(maximum_m):.1f} m".replace(".", ",")
    return "n/d"


def format_meters_point(point_m: float | None, *, approx: bool = False) -> str:
    if point_m is None:
        return "n/d"
    prefix = "~" if approx else ""
    return f"{prefix}{float(point_m):.1f} m".replace(".", ",")


def format_size_dict(size: dict[str, Any] | None) -> str:
    size = size or {}
    if size.get("minimum_m") is not None and size.get("maximum_m") is not None:
        return format_meters_range(size.get("minimum_m"), size.get("maximum_m"))
    if size.get("point_m") is not None:
        return format_meters_point(size.get("point_m"), approx=True)
    return "Tamaño n/d"


def format_period_s(period: float | None) -> str:
    if period is None:
        return "Período n/d"
    return f"{int(round(float(period)))} s"


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
    data = data_updated or "No disponible"
    query = query_local or "—"
    return (
        f"SURF · LA PALOMA   ·   Pronóstico {horizon}\n"
        f"Datos meteorológicos: {data}   ·   Consulta: {query}   ·   {status}"
    )


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
    text = (label or "").lower()
    if "buena" in text:
        return "cond-good"
    if "surfeable" in text:
        return "cond-fair"
    if "variable" in text:
        return "cond-variable"
    if "pocas" in text:
        return "cond-poor"
    if "incierto" in text:
        return "cond-uncertain"
    if "incompleto" in text:
        return "cond-incomplete"
    if "ventana" in text:
        return "cond-window"
    return "cond-neutral"
