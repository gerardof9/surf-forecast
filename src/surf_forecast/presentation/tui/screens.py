"""TUI screens that only render ForecastPresentation data."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Footer, Header, Static

from surf_forecast.domain.presentation import STATE_LABELS, spanish_reasons
from surf_forecast.presentation.tui.widgets import SHARED_GRID, StatusBar
from surf_forecast.paths import config_dir


class ForecastScreen(Screen):
    BINDINGS = [
        ("r", "refresh", "Actualizar"),
        ("o", "stored", "Solo guardado"),
        ("p", "profiles", "Perfiles"),
        ("s", "sources", "Fuentes"),
        ("question_mark", "help", "Ayuda"),
        ("q", "quit", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.payload: dict[str, Any] | None = None
        self.day_index = 0
        self.peak_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(SHARED_GRID, id="shared")
        with Horizontal():
            yield DataTable(id="days")
            yield DataTable(id="peaks")
            yield Static("Seleccione un día y un pico.", id="detail")
        yield StatusBar("Iniciando…", id="status")
        yield Footer()

    def on_mount(self) -> None:
        days = self.query_one("#days", DataTable)
        peaks = self.query_one("#peaks", DataTable)
        days.add_columns("Fecha", "Estado", "Titular")
        peaks.add_columns("Pico", "Condición", "*")
        days.cursor_type = "row"
        peaks.cursor_type = "row"

    def show_payload(self, payload: dict[str, Any], status: str) -> None:
        self.payload = payload
        days = self.query_one("#days", DataTable)
        days.clear()
        for day in payload.get("days", []):
            days.add_row(day.get("local_date"), day.get("state"), day.get("headline") or "")
        if payload.get("days"):
            self.day_index = 0
            self._render_peaks()
        self.query_one("#status", StatusBar).show(status)

    def _current_day(self) -> dict[str, Any] | None:
        if not self.payload:
            return None
        days = self.payload.get("days") or []
        if not days:
            return None
        return days[self.day_index]

    def _render_peaks(self) -> None:
        day = self._current_day()
        peaks = self.query_one("#peaks", DataTable)
        peaks.clear()
        if not day:
            return
        for peak in day.get("peaks", []):
            mark = "*" if peak.get("highlighted") else ""
            peaks.add_row(peak.get("peak_id"), peak.get("condition_label") or peak.get("state"), mark)
        self.peak_index = 0
        self._render_detail()

    def _render_detail(self) -> None:
        day = self._current_day()
        detail = self.query_one("#detail", Static)
        if not day:
            return
        peaks = day.get("peaks") or []
        if not peaks:
            detail.update("Sin picos completos para este día.")
            return
        peak = peaks[self.peak_index]
        lines = [
            f"Pico: {peak.get('peak_id')}",
            f"Estado: {STATE_LABELS.get(peak.get('state'), peak.get('state'))}",
            f"Condición: {peak.get('condition_label')}",
            f"Confianza: {peak.get('confidence', {}).get('level')}",
            f"k visible en criterios: {self.payload.get('criteria', {}).get('point_k') if self.payload else ''}",
        ]
        size = peak.get("size") or {}
        if size:
            lines.append(f"Hs {size.get('raw_hs_m')} → {size.get('point_m')} m [{size.get('minimum_m')}-{size.get('maximum_m')}]")
        window = peak.get("best_window")
        if window:
            lines.append(f"Ventana: {window.get('start_at')} – {window.get('end_at')}")
        else:
            lines.append("Sin ventana de 2 horas")
        for slot in peak.get("reference_slots") or []:
            lines.append(
                f"{slot.get('local_hour')}  {slot.get('condition')}  "
                f"viento {slot.get('wind_class')} {slot.get('wind_intensity')}"
            )
        lines.extend(spanish_reasons(peak.get("reason_codes") or []))
        if self.payload:
            lines.append(f"Snapshot: {self.payload.get('snapshot_id')}")
        detail.update("\n".join(lines))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "days":
            self.day_index = event.cursor_row
            self._render_peaks()
        elif event.data_table.id == "peaks":
            self.peak_index = event.cursor_row
            self._render_detail()


class ProfileScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Volver"), ("q", "app.pop_screen", "Volver")]

    def __init__(self, profiles: list[dict[str, Any]]) -> None:
        super().__init__()
        self.profiles = profiles

    def compose(self) -> ComposeResult:
        yield Header()
        table = DataTable()
        yield table
        yield Static(f"Editar: {config_dir() / 'peaks.json'}", id="path")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Nombre", "Estado", "Errores")
        for profile in self.profiles:
            table.add_row(
                profile.get("peak_id"),
                profile.get("name"),
                profile.get("status"),
                ", ".join(profile.get("validation_errors") or []) or "—",
            )


class HelpScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Cerrar"), ("q", "app.pop_screen", "Cerrar")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(
                "\n".join(
                    [
                        "Ayuda — Pronóstico La Paloma",
                        "r actualizar  o solo guardado  p perfiles  s fuentes  q salir",
                        "Hs del modelo no es la altura de rompiente. k × Hs es provisional.",
                        SHARED_GRID,
                        "Datos: Open-Meteo (CC BY 4.0)  https://open-meteo.com/",
                        "Licencia: https://creativecommons.org/licenses/by/4.0/",
                    ]
                )
            )
        )
