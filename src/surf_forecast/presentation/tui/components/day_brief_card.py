"""Compact day forecast card — hierarchy: chip, size, stars, oleaje/viento."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from surf_forecast.presentation.tui.components.badge import Badge
from surf_forecast.presentation.tui.formatters import format_stars_from_grade
from surf_forecast.presentation.tui.theme import TOKENS as T


class DayBriefCard(Vertical):
    """One comparable day card (005: Hoy / Mañana)."""

    DEFAULT_CSS = f"""
    DayBriefCard {{
        width: 1fr;
        height: auto;
        min-height: 10;
        max-height: 16;
        margin: 0 1 0 0;
        padding: 0 1 1 1;
        background: {T['bg.panel']};
        border-left: thick {T['border.dim']};
        border-top: solid {T['border.dim']};
        border-right: solid {T['border.dim']};
        border-bottom: solid {T['border.dim']};
    }}
    DayBriefCard.focused {{
        border-left: thick {T['border.focus']};
        background: {T['bg.raised']};
    }}
    DayBriefCard > #card-title {{
        color: {T['text.dim']};
        height: 1;
        margin: 1 0 0 0;
    }}
    DayBriefCard > Badge {{
        height: 1;
        margin: 0 0 0 0;
    }}
    DayBriefCard > #card-size {{
        margin: 1 0 0 0;
        color: {T['text.primary']};
        text-style: bold;
        height: 1;
    }}
    DayBriefCard > #card-size-caption {{
        color: {T['text.dim']};
        height: 1;
    }}
    DayBriefCard > #card-rating {{
        color: {T['grade.razonable']};
        height: 1;
    }}
    DayBriefCard > #card-metrics {{
        color: {T['text.secondary']};
        height: auto;
        margin: 1 0 0 0;
    }}
    DayBriefCard.muted-day {{
        opacity: 0.8;
        border-left: thick {T['border.dim']};
    }}
    """

    def __init__(self, day: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._day: dict[str, Any] = day or {}
        self._focused = False

    def compose(self) -> ComposeResult:
        yield Static("", id="card-title", markup=False)
        yield Badge("", id="card-badge")
        yield Static("", id="card-size", markup=False)
        yield Static("", id="card-size-caption", markup=False)
        yield Static("", id="card-rating", markup=False)
        yield Static("", id="card-metrics", markup=False)

    def on_mount(self) -> None:
        if self._day:
            self.set_day(self._day)

    def set_day(self, day: dict[str, Any]) -> None:
        self._day = day
        brief = day.get("brief") or {}
        label = brief.get("label") or ""
        display = day.get("display_title") or day.get("local_date") or ""
        title = f"{label} · {display}".strip(" ·") if label or display else "Día"
        self.query_one("#card-title", Static).update(title)

        cond_id = brief.get("condition")
        cond_label = brief.get("condition_label") or ""
        self.query_one("#card-badge", Badge).set_condition(cond_label or None, condition_id=cond_id)

        height = brief.get("height") or {}
        size_text = height.get("display") if height else None
        self.query_one("#card-size", Static).update(size_text or "—")
        self.query_one("#card-size-caption", Static).update(
            "tamaño estimado" if size_text else "sin rango de altura"
        )

        rating_w = self.query_one("#card-rating", Static)
        stars = format_stars_from_grade(cond_id)
        if stars and stars != "—":
            rating_w.update(stars)
            rating_w.display = True
        else:
            rating_w.update("")
            rating_w.display = False

        metrics = brief.get("metrics") or {}
        self.query_one("#card-metrics", Static).update(_format_metrics_block(metrics))

        incomplete = (day.get("state") == "incomplete_forecast") or (
            (cond_label or "").lower().startswith("pronóstico incompleto")
            or (cond_label or "").lower() == "sin datos"
        )
        self.set_class(incomplete and not self._focused, "muted-day")

    def set_focused(self, focused: bool) -> None:
        self._focused = focused
        self.set_class(focused, "focused")
        if focused:
            self.remove_class("muted-day")
        elif self._day:
            brief = self._day.get("brief") or {}
            incomplete = self._day.get("state") == "incomplete_forecast"
            self.set_class(incomplete, "muted-day")


def _format_metrics_block(metrics: dict[str, Any]) -> str:
    lines: list[str] = []
    swell = _format_swell(metrics.get("swell") or [])
    wind = _format_wind(metrics.get("wind"))
    lines.append(f"Oleaje  {swell or '—'}")
    lines.append(f"Viento  {wind or '—'}")
    return "\n".join(lines)


def _format_swell(rows: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for row in rows:
        direction = row.get("dir_label")
        period = row.get("period_display")
        if period is None and row.get("period_s") is not None:
            ps = int(round(float(row["period_s"])))
            period = f"{ps} s" if ps > 0 else None
        if direction and period:
            parts.append(f"del {direction} · período {period}")
        elif direction:
            parts.append(f"del {direction}")
        elif period:
            parts.append(f"período {period}")
    return "  ·  ".join(parts)


def _format_wind(wind: dict[str, Any] | None) -> str:
    if not wind:
        return ""
    primary = wind.get("display") or wind.get("dir_display")
    return str(primary) if primary else ""
