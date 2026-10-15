"""TUI screens: two-card daily brief home (schema 1.2.0)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Static

from surf_forecast.paths import config_dir
from surf_forecast.presentation.tui.components import DayBriefCard, Frame, StatusBar, header_text
from surf_forecast.presentation.tui.theme import SHARED_GRID


class DailyReportScreen(Screen):
    """Home — Hoy / Mañana DayBrief cards only."""

    BINDINGS = [
        Binding("left", "focus_hoy", "Hoy", show=True),
        Binding("right", "focus_manana", "Mañana", show=True),
        Binding("r", "refresh", "Actualizar"),
        Binding("o", "stored", "Solo guardado"),
        Binding("question_mark", "help", "Ayuda"),
        Binding("q", "quit", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.payload: dict[str, Any] | None = None
        self._status_text = "Iniciando…"
        self._focus_index = 0

    def compose(self) -> ComposeResult:
        yield Static("", id="report-header", markup=False)
        with Horizontal(id="brief-row"):
            yield DayBriefCard(id="card-hoy")
            yield DayBriefCard(id="card-manana")
        yield StatusBar(self._status_text, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_width(self.size.width)

    def on_resize(self, event) -> None:  # noqa: ANN001
        self._apply_width(event.size.width)

    def _apply_width(self, width: int) -> None:
        row = self.query_one("#brief-row")
        row.remove_class("stack")
        if width < 90:
            row.add_class("stack")

    def show_payload(self, payload: dict[str, Any], status: str) -> None:
        self.payload = payload
        self._status_text = status
        self._populate()
        self.query_one("#status", StatusBar).show(status)

    def _populate(self) -> None:
        payload = self.payload or {}
        days = payload.get("days") or []
        query = payload.get("query") or {}
        horizon = ""
        if query.get("horizon_start") and query.get("horizon_end"):
            horizon = f"{query['horizon_start']} → {query['horizon_end']}"
        data_times = payload.get("data_times") or {}
        query_times = payload.get("query_times") or {}
        self.query_one("#report-header", Static).update(
            header_text(
                data_updated=data_times.get("meteorological_updated_at_local"),
                query_local=query_times.get("executed_at_local"),
                status=self._status_text,
                horizon=horizon or "Hoy / Mañana",
            )
        )
        hoy = days[0] if len(days) > 0 else {}
        manana = days[1] if len(days) > 1 else {}
        self.query_one("#card-hoy", DayBriefCard).set_day(hoy)
        self.query_one("#card-manana", DayBriefCard).set_day(manana)
        self._apply_focus_chrome()

    def _apply_focus_chrome(self) -> None:
        hoy = self.query_one("#card-hoy", DayBriefCard)
        manana = self.query_one("#card-manana", DayBriefCard)
        hoy.set_focused(self._focus_index == 0)
        manana.set_focused(self._focus_index == 1)

    def action_focus_hoy(self) -> None:
        self._focus_index = 0
        self._apply_focus_chrome()

    def action_focus_manana(self) -> None:
        self._focus_index = 1
        self._apply_focus_chrome()


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cerrar"),
        Binding("q", "app.pop_screen", "Cerrar"),
    ]

    def compose(self) -> ComposeResult:
        path = config_dir() / "peaks.json"
        body = "\n".join(
            [
                "Ayuda — SURF · LA PALOMA",
                "",
                "Home: dos tarjetas — Hoy y Mañana (brief diario).",
                "Navegación:  ← Hoy   → Mañana",
                "Acciones:    R actualizar   o solo guardado   Q salir",
                "",
                "Cada tarjeta resume condición, altura estimada, prosa,",
                "mejor hora y playas que valen la pena (fair+).",
                "",
                "No hay pantalla de detalle de pico ni leyenda FR-017.",
                "Las recomendaciones son estimaciones, no garantías de olas",
                "ni de seguridad en el agua.",
                "",
                SHARED_GRID,
                f"Perfiles (archivo): {path}",
                "Datos: Open-Meteo (CC BY 4.0)",
            ]
        )
        yield Frame("AYUDA", body, id="help-frame", focused=True)
