"""Full-screen Textual app. Domain logic stays in application services."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from textual.app import App
from textual.worker import Worker

from surf_forecast.application.forecast_service import ForecastUnavailable, PersistenceError, run_forecast
from surf_forecast.application.profile_service import list_profiles
from surf_forecast.domain.models import QueryMode, QueryRequest
from surf_forecast.presentation.tui.screens import ForecastScreen, HelpScreen, ProfileScreen


class SurfForecastApp(App):
    CSS = """
    #shared { color: $warning; padding: 0 1; }
    #detail { width: 1fr; padding: 1; }
    DataTable { width: 1fr; height: 1fr; }
    """
    TITLE = "Pronóstico La Paloma"

    def on_mount(self) -> None:
        self.forecast_screen = ForecastScreen()
        self.push_screen(self.forecast_screen)
        self.run_query(QueryMode.NORMAL, "Actualizando datos…")

    def run_query(self, mode: QueryMode, status: str) -> None:
        self.forecast_screen.query_one("#status").show(status)
        self.run_worker(self._load(mode), exclusive=True, thread=True, name="forecast")

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
                self.forecast_screen.query_one("#status").show(message)
            return
        result = event.worker.result
        if not result:
            return
        status = "Consulta completa"
        if result["code"] == 1:
            status = "Consulta degradada"
        if result["mode"] == "stored_only":
            status = "Solo datos guardados"
        self.forecast_screen.show_payload(result["payload"], status)

    def action_refresh(self) -> None:
        self.run_query(QueryMode.FORCE_REFRESH, "Actualizando datos…")

    def action_stored(self) -> None:
        self.run_query(QueryMode.STORED_ONLY, "Usando datos guardados…")

    def action_profiles(self) -> None:
        profiles = [
            {
                "peak_id": profile.peak_id,
                "name": profile.name,
                "status": profile.status.value,
                "validation_errors": profile.validation_errors,
            }
            for profile in list_profiles()
        ]
        self.push_screen(ProfileScreen(profiles))

    def action_sources(self) -> None:
        payload = self.forecast_screen.payload or {}
        lines = []
        for source in payload.get("sources", []):
            lines.append(
                f"{source.get('source_id')} {source.get('status')} "
                f"edad={source.get('data_age_seconds')} corrida={source.get('model_run_availability')}"
            )
        self.forecast_screen.query_one("#status").show(" | ".join(lines) or "Sin fuentes")

    def action_help(self) -> None:
        self.push_screen(HelpScreen())


def run_tui() -> int:
    SurfForecastApp().run()
    return 0
