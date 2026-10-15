"""Structured peak card with Unicode box (not multiline dump)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.presentation.tui.formatters import (
    condition_role,
    format_period_s,
    format_score_num,
    format_size_dict,
    format_stars,
    format_wind,
)


class PeakCard(Static):
    DEFAULT_CSS = """
    PeakCard {
        height: auto;
        min-height: 7;
        padding: 0;
        color: #fffbf6;
    }
    PeakCard.selected {
        background: #1a2740;
        color: #00d4ff;
        text-style: bold;
    }
    PeakCard.cond-good { border-left: tall #9be205; }
    PeakCard.cond-fair { border-left: tall #ffc400; }
    PeakCard.cond-variable { border-left: tall #d78700; }
    PeakCard.cond-poor { border-left: tall #ff260e; }
    PeakCard.cond-uncertain { border-left: tall #815bb5; }
    """

    def __init__(self, peak: dict[str, Any] | None = None, *, selected: bool = False, **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__("", **kwargs)
        self._peak = peak or {}
        self._selected = selected
        if selected:
            self.add_class("selected")
        self._apply_peak(self._peak, selected=selected)

    def set_peak(self, peak: dict[str, Any], *, selected: bool = False) -> None:
        self._apply_peak(peak, selected=selected)

    def _apply_peak(self, peak: dict[str, Any], *, selected: bool) -> None:
        self._peak = peak
        self._selected = selected
        self.set_class(selected, "selected")
        for cls in list(self.classes):
            if cls.startswith("cond-"):
                self.remove_class(cls)
        label = peak.get("condition_label") or "Sin condición"
        role = condition_role(label)
        self.add_class(role)

        name = peak.get("display_name") or peak.get("peak_id") or "—"
        marker = " ★" if peak.get("best_of_day") else ""
        cursor = "▶ " if selected else "  "
        size_txt = format_size_dict(peak.get("size"))
        period_txt = format_period_s(peak.get("period_s"))
        wind_txt = format_wind(
            dir_label=peak.get("wind_dir_label"),
            intensity=peak.get("wind_intensity"),
            speed_kmh=peak.get("wind_speed_kmh"),
        )
        rating = peak.get("peak_rating")
        if rating:
            score_txt = f"{format_stars(float(rating['score']))} {format_score_num(float(rating['score']))}"
        else:
            score_txt = "Sin nota"

        width = max(22, self.size.width if self.size.width > 10 else 28)
        inner = width - 2
        top = "╭" + "─" * inner + "╮"
        bot = "╰" + "─" * inner + "╯"

        def row(text: str) -> str:
            plain = text[:inner]
            return "│" + plain.ljust(inner)[:inner] + "│"

        body = "\n".join(
            [
                top,
                row(f"{cursor}{name}{marker}"),
                row(f"● {label}"),
                row(f"{size_txt}  ·  {period_txt}"),
                row(wind_txt),
                row(score_txt),
                bot,
            ]
        )
        self.update(body)

    def on_resize(self, event: Any) -> None:  # noqa: ANN401
        if self._peak:
            self._apply_peak(self._peak, selected=self._selected)
