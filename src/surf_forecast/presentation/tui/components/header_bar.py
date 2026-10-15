"""View A header + day banner helpers."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.presentation.tui.formatters import format_header


def header_text(
    *,
    data_updated: str | None,
    query_local: str | None,
    status: str,
    horizon: str,
) -> str:
    return format_header(
        data_updated=data_updated,
        query_local=query_local,
        status=status,
        horizon=horizon,
    )


def window_completed_banner(day: dict[str, Any] | None) -> str:
    if not day:
        return ""
    if day.get("state") == "analysis_window_completed" or day.get("headline_code") == "analysis_window_completed":
        return (
            "! Ventana de análisis finalizada (06:00–20:00 UYT) — "
            "sin nueva mejor hora; condiciones del día abajo."
        )
    return ""


class Banner(Static):
    DEFAULT_CSS = """
    Banner {
        color: #ffc400;
        height: auto;
        margin: 0 0 1 0;
    }
    """

    def __init__(self, text: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__(text, **kwargs)

    def set_text(self, text: str) -> None:
        self.update(text)
        self.display = bool(text)
