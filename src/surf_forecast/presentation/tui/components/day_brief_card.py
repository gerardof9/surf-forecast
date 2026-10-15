"""DayBriefCard — Hoy/Mañana brief for schema 1.2.0 home."""

from __future__ import annotations

from typing import Any

from surf_forecast.presentation.tui.components.frame import Frame


class DayBriefCard(Frame):
    """One day brief rendered as framed plain text."""

    DEFAULT_CSS = """
    DayBriefCard {
        width: 1fr;
        height: auto;
        min-height: 16;
        margin: 0 1;
    }
    """

    def __init__(self, day: dict[str, Any] | None = None, **kwargs: Any) -> None:
        day = day or {}
        brief = day.get("brief") or {}
        title = _card_title(day, brief)
        super().__init__(title, _card_body(brief), **kwargs)
        self._day = day

    def set_day(self, day: dict[str, Any]) -> None:
        self._day = day
        brief = day.get("brief") or {}
        self.set_title(_card_title(day, brief))
        self.set_body(_card_body(brief))


def _card_title(day: dict[str, Any], brief: dict[str, Any]) -> str:
    label = brief.get("label") or ""
    display = day.get("display_title") or day.get("local_date") or ""
    if label and display:
        return f"{label} · {display}".upper()
    return (label or display or "DÍA").upper()


def _card_body(brief: dict[str, Any]) -> str:
    lines: list[str] = []
    cond = brief.get("condition_label") or "—"
    lines.append(f"[ {cond} ]")
    height = brief.get("height") or {}
    lines.append(f"Altura  {height.get('display') if height else 'n/d'}")
    lines.append("")
    if brief.get("headline"):
        lines.append(str(brief["headline"]))
        lines.append("")
    if brief.get("body"):
        lines.append(str(brief["body"]))
        lines.append("")
    go = brief.get("go_window") or {}
    if go.get("display"):
        lines.append(str(go["display"]))
    else:
        lines.append("Sin hora clara")
    lines.append("")
    spots = brief.get("worth_spots") or []
    if spots:
        lines.append("Playas:")
        for spot in spots:
            name = spot.get("display_name") or spot.get("peak_id")
            reason = spot.get("reason_short")
            extra = f" — {reason}" if reason else ""
            lines.append(f"  · {name}{extra}")
    else:
        lines.append(brief.get("empty_spots_message") or "Ningún pico claro para ir.")
    if brief.get("caution"):
        lines.append("")
        lines.append(str(brief["caution"]))
    return "\n".join(lines)
