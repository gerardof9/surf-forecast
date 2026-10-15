"""Full-screen Textual app. Domain logic stays in application services."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from textual.app import App
from textual.worker import Worker

from surf_forecast.application.forecast_service import ForecastUnavailable, PersistenceError, run_forecast
from surf_forecast.domain.models import QueryMode, QueryRequest
from surf_forecast.presentation.tui.screens import DailyReportScreen, HelpScreen


class SurfForecastApp(App):
    CSS = """
    Screen { layout: vertical; background: #0b1220; color: #fffbf6; }
    #report-header {
        height: auto;
        max-height: 3;
        padding: 0 1;
        color: #00a2fa;
        text-style: bold;
        border-bottom: solid #00a2fa;
    }
    #brief-row {
        height: 1fr;
        layout: horizontal;
        padding: 1;
    }
    #brief-row.stack {
        layout: vertical;
    }
    #help-frame { margin: 2 4; width: auto; }
    """
    TITLE = "SURF · LA PALOMA"
    auto_query_on_mount = True

    def on_mount(self) -> None:
        self.forecast_screen = DailyReportScreen()
        self.push_screen(self.forecast_screen)
        if self.auto_query_on_mount:
            self.run_query(QueryMode.NORMAL, "Actualizando datos…")

    def run_query(self, mode: QueryMode, status: str) -> None:
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


def run_tui() -> int:
    SurfForecastApp().run()
    return 0
