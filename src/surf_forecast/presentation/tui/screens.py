"""TUI screens: daily report (View A) and peak detail (View B)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Label, ListItem, ListView, Static

from surf_forecast.paths import config_dir
from surf_forecast.presentation.tui.components import (
    AnalysisPanel,
    Banner,
    BestWindowCallout,
    EvolutionTable,
    Frame,
    PeakCard,
    RatingHero,
    StatusBar,
    TechnicalDetails,
    header_text,
    window_completed_banner,
)
from surf_forecast.presentation.tui.formatters import (
    format_confidence,
    format_day_chip,
    format_period_s,
    format_score_num,
    format_size_dict,
    format_stars,
    format_wind,
)
from surf_forecast.presentation.tui.theme import LEGEND_LINES, SECTION_PEAKS, SHARED_GRID


class DailyReportScreen(Screen):
    """View A — daily surf report board."""

    BINDINGS = [
        Binding("up", "day_prev", "Día↑", show=True),
        Binding("down", "day_next", "Día↓", show=True),
        Binding("left", "peak_prev", "Pico←", show=True),
        Binding("right", "peak_next", "Pico→", show=True),
        Binding("enter", "open_detail", "Detalle", show=True, priority=True),
        Binding("r", "refresh", "Actualizar"),
        Binding("o", "stored", "Solo guardado"),
        Binding("question_mark", "help", "Ayuda"),
        Binding("q", "quit", "Salir"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.payload: dict[str, Any] | None = None
        self.day_index = 0
        self.peak_index = 0
        self._status_text = "Iniciando…"

    def compose(self) -> ComposeResult:
        yield Static("", id="report-header", markup=False)
        with Horizontal(id="main"):
            with Vertical(id="days-rail"):
                yield Frame("DÍAS", "", id="days-frame")
                yield ListView(id="day-list")
            with VerticalScroll(id="report-body"):
                yield Static("", id="day-title", classes="day-title", markup=False)
                yield Banner("", id="day-banner")
                with Horizontal(id="analysis-row"):
                    yield AnalysisPanel("ANÁLISIS DEL DÍA", id="day-analysis")
                    yield RatingHero("VALORACIÓN DEL DÍA", id="day-rating")
                yield Static(SECTION_PEAKS, classes="day-title", markup=False)
                yield Grid(id="peak-grid")
            with Vertical(id="legend-rail"):
                yield Frame("LEYENDA", "\n".join(LEGEND_LINES) + "\n\n" + SHARED_GRID, id="legend-frame")
        yield StatusBar(self._status_text, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#day-list", ListView).focus()
        self._apply_width(self.size.width)

    def on_resize(self, event) -> None:  # noqa: ANN001
        self._apply_width(event.size.width)

    def _apply_width(self, width: int) -> None:
        main = self.query_one("#main")
        grid = self.query_one("#peak-grid", Grid)
        main.remove_class("narrow", "medium")
        grid.remove_class("cols-1", "cols-2", "cols-3", "cols-5")
        if width < 90:
            main.add_class("narrow")
            grid.add_class("cols-1")
        elif width < 130:
            main.add_class("medium")
            grid.add_class("cols-3")
        else:
            grid.add_class("cols-5")

    def show_payload(self, payload: dict[str, Any], status: str) -> None:
        self.payload = payload
        self._status_text = status
        self.day_index = min(self.day_index, max(0, len(payload.get("days") or []) - 1))
        self.peak_index = 0
        self._populate_days()
        self._populate_day()
        self.query_one("#status", StatusBar).show(status)

    def _populate_days(self) -> None:
        days = (self.payload or {}).get("days") or []
        lst = self.query_one("#day-list", ListView)
        lst.clear()
        for day in days:
            lst.append(ListItem(Label(format_day_chip(day))))
        if days:
            lst.index = self.day_index

    def _current_day(self) -> dict[str, Any] | None:
        days = (self.payload or {}).get("days") or []
        if not days:
            return None
        self.day_index = max(0, min(self.day_index, len(days) - 1))
        return days[self.day_index]

    def _populate_day(self) -> None:
        payload = self.payload or {}
        day = self._current_day()
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
                horizon=horizon or "hoy + 4 días",
            )
        )
        if not day:
            self.query_one("#day-title", Static).update("Sin días")
            self.query_one("#day-banner", Banner).set_text("")
            self.query_one("#day-analysis", AnalysisPanel).set_analysis(None, absent="Sin análisis.")
            self.query_one("#day-rating", RatingHero).set_rating(None, "Sin días")
            self._populate_peak_grid([])
            return

        title = day.get("display_title") or day.get("local_date") or ""
        self.query_one("#day-title", Static).update(title.upper())
        self.query_one("#day-banner", Banner).set_text(window_completed_banner(day))
        self.query_one("#day-analysis", AnalysisPanel).set_analysis(day.get("day_analysis"))
        self.query_one("#day-rating", RatingHero).set_rating(
            day.get("day_rating"), day.get("day_rating_absent_reason")
        )

        peaks = day.get("peaks") or []
        if peaks:
            self.peak_index = max(0, min(self.peak_index, len(peaks) - 1))
        self._populate_peak_grid(peaks)

    def _populate_peak_grid(self, peaks: list[dict[str, Any]]) -> None:
        grid = self.query_one("#peak-grid", Grid)
        grid.remove_children()
        if not peaks:
            grid.mount(Static("Sin picos evaluables.", classes="muted", markup=False))
            return
        for index, peak in enumerate(peaks):
            grid.mount(PeakCard(peak, selected=index == self.peak_index))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id != "day-list":
            return
        if event.list_view.index is not None:
            self.day_index = event.list_view.index
            self.peak_index = 0
            self._populate_day()

    def action_day_prev(self) -> None:
        self._move_day(-1)

    def action_day_next(self) -> None:
        self._move_day(1)

    def _move_day(self, delta: int) -> None:
        days = (self.payload or {}).get("days") or []
        if not days:
            return
        self.day_index = max(0, min(len(days) - 1, self.day_index + delta))
        self.peak_index = 0
        self.query_one("#day-list", ListView).index = self.day_index
        self._populate_day()

    def action_peak_prev(self) -> None:
        self._move_peak(-1)

    def action_peak_next(self) -> None:
        self._move_peak(1)

    def _move_peak(self, delta: int) -> None:
        day = self._current_day()
        if not day:
            return
        peaks = day.get("peaks") or []
        if not peaks:
            return
        self.peak_index = max(0, min(len(peaks) - 1, self.peak_index + delta))
        self._populate_peak_grid(peaks)

    def action_open_detail(self) -> None:
        day = self._current_day()
        if not day:
            return
        peaks = day.get("peaks") or []
        if not peaks:
            return
        self.app.push_screen(
            PeakDetailScreen(
                payload=self.payload or {},
                day_index=self.day_index,
                peak_index=self.peak_index,
            )
        )


class PeakDetailScreen(Screen):
    """View B — three-zone peak detail board."""

    BINDINGS = [
        Binding("escape", "back", "Volver", show=True),
        Binding("d", "toggle_tech", "Técnicos", show=True),
        Binding("left", "peak_prev", "Pico←", show=True),
        Binding("right", "peak_next", "Pico→", show=True),
        Binding("r", "refresh", "Actualizar"),
        Binding("o", "stored", "Solo guardado"),
        Binding("question_mark", "help", "Ayuda"),
        Binding("q", "quit", "Salir"),
    ]

    def __init__(self, payload: dict[str, Any], day_index: int, peak_index: int) -> None:
        super().__init__()
        self.payload = payload
        self.day_index = day_index
        self.peak_index = peak_index

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="detail-body"):
            yield Static("", id="detail-header", classes="day-title", markup=False)
            with Horizontal(id="detail-zones"):
                yield Frame("RESUMEN", "", id="detail-summary")
                with Vertical(id="detail-center"):
                    yield EvolutionTable(id="detail-evolution")
                    yield BestWindowCallout(id="detail-window")
                    yield AnalysisPanel("ANÁLISIS DEL PICO", id="detail-analysis")
                yield Frame("NOTAS", "", id="detail-meta")
            yield TechnicalDetails(id="technical")
        yield StatusBar("Detalle del pico · Esc vuelve al mismo día", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._populate()

    def _day(self) -> dict[str, Any] | None:
        days = self.payload.get("days") or []
        if not days:
            return None
        self.day_index = max(0, min(self.day_index, len(days) - 1))
        return days[self.day_index]

    def _peak(self) -> dict[str, Any] | None:
        day = self._day()
        if not day:
            return None
        peaks = day.get("peaks") or []
        if not peaks:
            return None
        self.peak_index = max(0, min(self.peak_index, len(peaks) - 1))
        return peaks[self.peak_index]

    def _populate(self) -> None:
        day = self._day()
        peak = self._peak()
        if not day or not peak:
            self.query_one("#detail-header", Static).update("Sin pico")
            return
        self.query_one("#detail-header", Static).update(
            f"← {peak.get('display_name')}  ·  {day.get('display_title')}  ·  06:00–20:00 UYT"
        )

        size_txt = format_size_dict(peak.get("size"))
        period_txt = format_period_s(peak.get("period_s"))
        wind_txt = format_wind(
            dir_label=peak.get("wind_dir_label"),
            intensity=peak.get("wind_intensity"),
            speed_kmh=peak.get("wind_speed_kmh"),
        )
        rating = peak.get("peak_rating")
        if rating:
            rating_txt = (
                f"{format_stars(float(rating['score']))} "
                f"{format_score_num(float(rating['score']))} / 5"
            )
        else:
            rating_txt = "Sin valoración de pico"
        conf = format_confidence((peak.get("confidence") or {}).get("level"))
        profile_note = "Perfil: —"
        for prof in self.payload.get("profiles") or []:
            if prof.get("peak_id") == peak.get("peak_id"):
                profile_note = f"Perfil: {prof.get('status')}"
                break

        summary = "\n".join(
            [
                f"● {peak.get('condition_label')}",
                f"Tamaño: {size_txt}",
                f"Período: {period_txt}",
                f"Viento: {wind_txt}",
                f"Valoración: {rating_txt}",
                f"Confianza: {conf}",
            ]
        )
        self.query_one("#detail-summary", Frame).set_body(summary)
        self.query_one("#detail-meta", Frame).set_body(
            "\n".join(
                [
                    profile_note,
                    SHARED_GRID,
                    "Hs del modelo ≠ altura de rompiente.",
                ]
            )
        )
        self.query_one("#detail-evolution", EvolutionTable).set_samples(peak.get("evolution_samples"))
        self.query_one("#detail-window", BestWindowCallout).set_window(peak.get("best_window"))
        analysis = peak.get("peak_analysis")
        absent = peak.get("peak_analysis_absent_reason") or "Sin análisis de pico."
        self.query_one("#detail-analysis", AnalysisPanel).set_analysis(analysis, absent=absent)

        tech = self.query_one("#technical", TechnicalDetails)
        tech.collapse()
        tech.set_body(self._technical_body(peak))
        self.query_one("#status", StatusBar).show(
            f"Detalle · {peak.get('display_name')} · Esc volver"
        )

    def _technical_body(self, peak: dict[str, Any]) -> str:
        size = peak.get("size") or {}
        criteria = self.payload.get("criteria") or {}
        data_times = self.payload.get("data_times") or {}
        query_times = self.payload.get("query_times") or {}
        # Higher precision OK in technical pane
        lines = [
            f"Snapshot: {self.payload.get('snapshot_id')}",
            f"Criterios: {criteria.get('criteria_version')}  k={criteria.get('point_k')}",
            f"Hs cruda: {size.get('raw_hs_m')}  → derivado: {size.get('point_m')}",
            f"Rango derivado: {size.get('minimum_m')}–{size.get('maximum_m')}",
            f"Datos meteorológicos: {data_times.get('meteorological_updated_at_local') or 'No disponible'}",
            f"Consulta: {query_times.get('executed_at_local') or '—'}",
            SHARED_GRID,
        ]
        for source in self.payload.get("sources") or []:
            lines.append(
                f"Fuente {source.get('source_id')}: {source.get('model')} "
                f"status={source.get('status')} edad={source.get('data_age_seconds')}s"
            )
        conf = peak.get("confidence") or {}
        if conf.get("caps") or conf.get("degradations"):
            lines.append(f"Confianza caps={conf.get('caps')} degradations={conf.get('degradations')}")
        return "\n".join(lines)

    def action_back(self) -> None:
        report = getattr(self.app, "forecast_screen", None)
        if report is not None:
            report.day_index = self.day_index
            report.peak_index = self.peak_index
            report._populate_day()
        self.app.pop_screen()

    def action_toggle_tech(self) -> None:
        self.query_one("#technical", TechnicalDetails).toggle()

    def action_peak_prev(self) -> None:
        self._move_peak(-1)

    def action_peak_next(self) -> None:
        self._move_peak(1)

    def _move_peak(self, delta: int) -> None:
        day = self._day()
        if not day:
            return
        peaks = day.get("peaks") or []
        if not peaks:
            return
        self.peak_index = max(0, min(len(peaks) - 1, self.peak_index + delta))
        self._populate()


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
                "Navegación:  ↑↓ día   ←→ pico   Enter detalle   Esc volver",
                "Acciones:    R actualizar   o solo guardado   D técnicos   Q salir",
                "",
                "Foco primario: lista de días. ←→ selecciona pico (no quita el foco).",
                "",
                "La valoración 1–5 (pasos 0,5) es una codificación ordinal del grado",
                "del motor con ajuste de confianza/perfil; no es una probabilidad.",
                "",
                "LEYENDA",
                *LEGEND_LINES,
                "",
                "Hs del modelo ≠ altura de rompiente. k × Hs es provisional.",
                SHARED_GRID,
                f"Perfiles (archivo): {path}",
                "Datos: Open-Meteo (CC BY 4.0)",
            ]
        )
        yield Frame("AYUDA", body, id="help-frame", focused=True)
