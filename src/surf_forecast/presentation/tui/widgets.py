"""Shared TUI widgets for the daily surf report."""

from __future__ import annotations

from typing import Any

from textual.widgets import Footer, Static

ATTRIBUTION = "Datos: Open-Meteo (CC BY 4.0)"
SHARED_GRID = "Los picos cercanos comparten la misma celda regional del modelo."
SECTION_PEAKS = "PICOS DEL DÍA"

FR017_LEGEND = (
    "Buena oportunidad · Surfeable · Variable · Pocas olas · "
    "Incierto · Pronóstico incompleto · Ventana de análisis finalizada"
)


class StatusBar(Static):
    def show(self, message: str) -> None:
        self.update(f"{message}  ·  {ATTRIBUTION}")


class AttributionFooter(Footer):
    pass


def format_stars(score: float | None) -> str:
    """Whole-point glyph string; empty when no score."""
    if score is None:
        return ""
    filled = int(round(score))
    filled = max(0, min(5, filled))
    return "★" * filled + "☆" * (5 - filled)


def format_rating_line(rating: dict[str, Any] | None, absent: str | None = None) -> str:
    if not rating:
        return f"Sin valoración — {absent or 'sin grado resuelto'}"
    score = float(rating["score"])
    stars = format_stars(score)
    caption = rating.get("caption") or ""
    line = f"{stars}  {score:.1f} / 5".replace(".", ",")
    if caption:
        line = f"{line}  {caption}"
    return line


def format_analysis_block(analysis: dict[str, Any] | None) -> str:
    if not analysis:
        return ""
    sentences = analysis.get("sentences") or []
    if not sentences:
        return analysis.get("text") or ""
    prefixes = {
        "fact": "·",
        "interpretation": "◇",
        "limitation": "!",
    }
    lines = []
    for sentence in sentences:
        kind = sentence.get("kind", "fact")
        prefix = prefixes.get(kind, "·")
        lines.append(f"{prefix} {sentence.get('text', '')}")
    return "\n".join(lines)


def format_peak_card(peak: dict[str, Any]) -> str:
    name = peak.get("display_name") or peak.get("peak_id")
    label = peak.get("condition_label") or peak.get("state")
    size = peak.get("size") or {}
    size_txt = ""
    if size.get("minimum_m") is not None and size.get("maximum_m") is not None:
        size_txt = f"{size['minimum_m']:.1f}–{size['maximum_m']:.1f} m"
    elif size.get("point_m") is not None:
        size_txt = f"~{size['point_m']:.1f} m"
    period = ""
    wind_parts = []
    if peak.get("wind_dir_label"):
        wind_parts.append(str(peak["wind_dir_label"]))
    if peak.get("wind_intensity"):
        wind_parts.append(str(peak["wind_intensity"]))
    if peak.get("wind_speed_kmh") is not None:
        wind_parts.append(f"{peak['wind_speed_kmh']:.0f} km/h")
    wind = " ".join(wind_parts)
    rating = peak.get("peak_rating")
    score = f"{rating['score']:.0f}/5" if rating else "—"
    marker = " ★día" if peak.get("best_of_day") else ""
    bits = [label, size_txt, wind, score]
    body = " · ".join(b for b in bits if b)
    return f"{name}{marker}\n  {body}"


def format_header(
    *,
    data_updated: str | None,
    query_local: str | None,
    status: str,
    horizon: str,
) -> str:
    data = data_updated or "No disponible"
    query = query_local or ""
    return f"SURF · LA PALOMA  ·  {horizon}  ·  Datos {data}  ·  {status}"


class TechnicalDetails(Static):
    """Collapsed-by-default technical block."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("DETALLES TÉCNICOS [plegado — D]", **kwargs)
        self._expanded = False
        self._body = ""

    def set_body(self, body: str) -> None:
        self._body = body
        self._render()

    def toggle(self) -> None:
        self._expanded = not self._expanded
        self._render()

    def collapse(self) -> None:
        self._expanded = False
        self._render()

    def _render(self) -> None:
        if self._expanded:
            self.update(f"DETALLES TÉCNICOS [D para plegar]\n{self._body}")
        else:
            self.update("DETALLES TÉCNICOS [plegado — D]")

