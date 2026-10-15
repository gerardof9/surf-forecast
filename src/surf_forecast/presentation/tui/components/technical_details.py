"""Collapsed-by-default technical details (toggle D)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static


class TechnicalDetails(Static):
    DEFAULT_CSS = """
    TechnicalDetails {
        height: auto;
        color: #888888;
        margin-top: 1;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__("DETALLES TÉCNICOS (plegado — D)", **kwargs)
        self._expanded = False
        self._body = ""

    def set_body(self, body: str) -> None:
        self._body = body
        self._apply()

    def toggle(self) -> None:
        self._expanded = not self._expanded
        self._apply()

    def collapse(self) -> None:
        self._expanded = False
        self._apply()

    def _apply(self) -> None:
        # Do not name this `_render`: Widget._render must return a Visual.
        if self._expanded:
            self.update(f"DETALLES TÉCNICOS (D para plegar)\n{self._body}")
        else:
            self.update("DETALLES TÉCNICOS (plegado — D)")
