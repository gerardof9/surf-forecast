"""Full-screen Textual app. Domain logic stays in application services."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from textual.app import App
from textual.worker import Worker

from surf_forecast.application.forecast_service import ForecastUnavailable, PersistenceError, run_forecast
from surf_forecast.domain.models import QueryMode, QueryRequest
from surf_forecast.presentation.tui.screens import DailyReportScreen, HelpScreen
from surf_forecast.presentation.tui.theme import css_vars


class SurfForecastApp(App):
    CSS = css_vars()
    TITLE = "SURF · LA PALOMA"
    # Brief §4 / §10: no command palette leak (^p).
    ENABLE_COMMAND_PALETTE = False
    auto_query_on_mount = True
    demo_payload: dict[str, Any] | None = None

    def on_mount(self) -> None:
        self.forecast_screen = DailyReportScreen()
        self.push_screen(self.forecast_screen)
        if self.demo_payload is not None:
            # Screen compose finishes after push; defer populate.
            self.call_after_refresh(self._show_demo)
            return
        if self.auto_query_on_mount:
            self.run_query(QueryMode.NORMAL, "Actualizando datos…")

    def _show_demo(self) -> None:
        if self.demo_payload is not None and hasattr(self, "forecast_screen"):
            self.forecast_screen.show_payload(self.demo_payload, "Demo (datos fijos)")

    def run_query(self, mode: QueryMode, status: str) -> None:
        if self.demo_payload is not None:
            self.forecast_screen.show_payload(self.demo_payload, "Demo (datos fijos)")
            return
        if hasattr(self, "forecast_screen"):
            try:
                self.forecast_screen.query_one("#status").show(status)
            except Exception:
                pass
        self.run_worker(lambda: self._load(mode), exclusive=True, thread=True, name="forecast")

    def _load(self, mode: QueryMode) -> dict:
        request = QueryRequest(
            mode=mode,
            reference_time=datetime.now(ZoneInfo("America/Montevideo")),
            timezone="America/Montevideo",
            output_mode="tui",
        )
        _result, presentation, code = run_forecast(request)
        return {"payload": presentation.payload, "code": code, "mode": mode.value}

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.name != "forecast":
            return
        if event.state.name != "SUCCESS":
            if event.state.name == "ERROR":
                message = "No hay pronóstico disponible."
                error = event.worker.error
                if isinstance(error, ForecastUnavailable):
                    message = "Sin datos ni snapshot guardado."
                elif isinstance(error, PersistenceError):
                    message = "No se pudo guardar el snapshot."
                try:
                    self.forecast_screen.query_one("#status").show(message)
                except Exception:
                    pass
            return
        result = event.worker.result
        if not result:
            return
        status = "Datos disponibles"
        if result["code"] == 1:
            status = "Consulta degradada"
        if result["mode"] == "stored_only":
            status = "Solo datos guardados"
        self.forecast_screen.show_payload(result["payload"], status)

    def action_refresh(self) -> None:
        self.run_query(QueryMode.FORCE_REFRESH, "Actualizando datos…")

    def action_stored(self) -> None:
        self.run_query(QueryMode.STORED_ONLY, "Usando datos guardados…")

    def action_help(self) -> None:
        self.push_screen(HelpScreen())


def run_tui(*, demo: bool = False) -> int:
    import os

    # Cursor / some shells export NO_COLOR=1, which strips theme colors to gray.
    # Grade chips and panels need truecolor; clear only for this process.
    os.environ.pop("NO_COLOR", None)
    os.environ.setdefault("FORCE_COLOR", "1")
    os.environ.setdefault("COLORTERM", "truecolor")

    app = SurfForecastApp()
    if demo:
        from surf_forecast.presentation.tui.demo_payload import build_demo_payload

        app.demo_payload = build_demo_payload()
        app.auto_query_on_mount = False
    app.run()
    return 0
