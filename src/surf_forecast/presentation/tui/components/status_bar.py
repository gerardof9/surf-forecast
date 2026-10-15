"""Dedicated StatusBar footer — not a Frame (FR-G07)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.presentation.tui.theme import ATTRIBUTION


class StatusBar(Static):
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #1a2740;
        color: #fffbf6;
        padding: 0 1;
    }
    """

    def __init__(self, message: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__(message, **kwargs)
        self._message = message

    def show(self, message: str) -> None:
        self._message = message
        shortcuts = "← Hoy  → Mañana  ·  R actualizar  ·  o guardado  ·  ?  ·  Q"
        self.update(f"{message}  ·  {shortcuts}  ·  {ATTRIBUTION}")
