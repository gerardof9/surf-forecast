"""Shared TUI footer, attribution, and status text."""

from __future__ import annotations

from textual.widgets import Footer, Static

ATTRIBUTION = "Datos: Open-Meteo (CC BY 4.0)"
SHARED_GRID = "Los picos cercanos comparten la misma celda regional del modelo."


class StatusBar(Static):
    def show(self, message: str) -> None:
        self.update(f"{message}  ·  {ATTRIBUTION}")


class AttributionFooter(Footer):
    pass
