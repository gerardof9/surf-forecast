"""Single footer row — key hints left, status right (brief §4). No attribution here."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.presentation.tui.theme import TOKENS as T


class StatusBar(Static):
    DEFAULT_CSS = f"""
    StatusBar {{
        height: 1;
        background: {T['bg.raised']};
        color: {T['text.dim']};
        padding: 0 1;
    }}
    """

    def __init__(self, message: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__(message, **kwargs)
        self._message = message

    def show(self, message: str) -> None:
        self._message = message
        keys = "← Hoy  → Mañana  ·  R actualizar  ·  o guardado  ·  ? ayuda  ·  Q salir"
        status = message or "—"
        self.update(f"{keys}   │   ● {status}")
