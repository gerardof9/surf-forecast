"""TUI screens: daily report (View A) and peak detail (View B)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from surf_forecast.paths import config_dir
from surf_forecast.presentation.tui.widgets import (
    FR017_LEGEND,
    SHARED_GRID,
    SECTION_PEAKS,
    StatusBar,
    TechnicalDetails,
    format_analysis_block,
    format_header,
    format_peak_card,
    format_rating_line,
)


class DailyReportScreen(Screen):
    """View A — daily surf report."""

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
        yield Header(show_clock=False)
        yield Static("", id="report-header")
        with Horizontal(id="main"):
            with Vertical(id="days-rail"):
                yield Static("DÍAS", classes="section-title")
                yield ListView(id="day-list")
                yield Static(FR017_LEGEND, id="legend")
            with VerticalScroll(id="report-body"):
                yield Static("", id="day-title", classes="section-title")
                yield Static("ANÁLISIS DEL DÍA", classes="section-title")
                yield Static("", id="day-analysis")
                yield Static("VALORACIÓN DEL DÍA", classes="section-title")
                yield Static("", id="day-rating")
                yield Static(SECTION_PEAKS, classes="section-title")
                yield Static("", id="peak-cards")
        yield StatusBar(self._status_text, id="status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#day-list", ListView).focus()
        self._apply_width(self.size.width)

    def on_resize(self, event) -> None:  # noqa: ANN001
        self._apply_width(event.size.width)

    def _apply_width(self, width: int) -> None:
        main = self.query_one("#main")
        if width < 90:
            main.add_class("narrow")
        else:
            main.remove_class("narrow")

    def show_payload(self, payload: dict[str, Any], status: str) -> None:
        self.payload = payload
        self._status_text = status
        self.day_index = min(self.day_index, max(0, len(payload.get("days") or []) - 1))
        self.peak_index = 0
        self._populate_days()
        self._render_day()
        self.query_one("#status", StatusBar).show(status)

    def _populate_days(self) -> None:
        days = (self.payload or {}).get("days") or []
        lst = self.query_one("#day-list", ListView)
        lst.clear()
        for day in days:
            title = day.get("display_title") or day.get("local_date")
            rating = day.get("day_rating")
            chip = f"{rating['score']:.0f}/5" if rating else "—"
            lst.append(ListItem(Label(f"{title}  {chip}")))
        if days:
            lst.index = self.day_index

    def _current_day(self) -> dict[str, Any] | None:
        days = (self.payload or {}).get("days") or []
        if not days:
            return None
        self.day_index = max(0, min(self.day_index, len(days) - 1))
        return days[self.day_index]

    def _render_day(self) -> None:
        payload = self.payload or {}
        day = self._current_day()
        query = payload.get("query") or {}
        horizon = ""
        if query.get("horizon_start") and query.get("horizon_end"):
            horizon = f"{query['horizon_start']} → {query['horizon_end']}"
        data_times = payload.get("data_times") or {}
        query_times = payload.get("query_times") or {}
        self.query_one("#report-header", Static).update(
            format_header(
                data_updated=data_times.get("meteorological_updated_at_local"),
                query_local=query_times.get("executed_at_local"),
                status=self._status_text,
                horizon=horizon,
            )
        )
        if not day:
            self.query_one("#day-title", Static).update("Sin días")
            self.query_one("#day-analysis", Static).update("")
            self.query_one("#day-rating", Static).update("Sin valoración")
            self.query_one("#peak-cards", Static).update("")
            return
        self.query_one("#day-title", Static).update(day.get("display_title") or day.get("local_date") or "")
        self.query_one("#day-analysis", Static).update(format_analysis_block(day.get("day_analysis")))
        self.query_one("#day-rating", Static).update(
            format_rating_line(day.get("day_rating"), day.get("day_rating_absent_reason"))
        )
        peaks = day.get("peaks") or []
        if peaks:
            self.peak_index = max(0, min(self.peak_index, len(peaks) - 1))
        lines = [format_peak_card(p) for p in peaks]
        rendered = []
        for i, line in enumerate(lines):
            mark = "▶ " if i == self.peak_index else "  "
            rendered.append(mark + line.replace("\n", "\n   "))
        self.query_one("#peak-cards", Static).update("\n\n".join(rendered) if rendered else "Sin picos")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "day-list":
            return
        if event.list_view.index is not None:
            self.day_index = event.list_view.index
            self.peak_index = 0
            self._render_day()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.list_view.id != "day-list":
            return
        if event.list_view.index is not None:
            self.day_index = event.list_view.index
            self.peak_index = 0
            self._render_day()

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
        lst = self.query_one("#day-list", ListView)
        lst.index = self.day_index
        self._render_day()

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
        self._render_day()

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
    """View B — peak detail with sampled evolution and collapsible technicals."""

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
        yield Header(show_clock=False)
        with VerticalScroll(id="detail-body"):
            yield Static("", id="detail-header", classes="section-title")
            yield Static("", id="detail-summary")
            yield Static("EVOLUCIÓN (muestras)", classes="section-title")
            yield Static("", id="detail-evolution")
            yield Static("MEJOR VENTANA ESTIMADA", classes="section-title")
            yield Static("", id="detail-window")
            yield Static("ANÁLISIS DEL PICO", classes="section-title")
            yield Static("", id="detail-analysis")
            yield TechnicalDetails(id="technical")
        yield StatusBar("Detalle", id="status")
        yield Footer()

    def on_mount(self) -> None:
        self._render()

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

    def _render(self) -> None:
        day = self._day()
        peak = self._peak()
        if not day or not peak:
            self.query_one("#detail-header", Static).update("Sin pico")
            return
        title = (
            f"← {peak.get('display_name')} · {day.get('display_title')} · "
            f"06:00–20:00 UYT · {peak.get('condition_label')}"
        )
        self.query_one("#detail-header", Static).update(title)

        size = peak.get("size") or {}
        size_txt = (
            f"{size.get('minimum_m', '—')}–{size.get('maximum_m', '—')} m"
            if size
            else "tamaño n/d"
        )
        wind_bits = []
        if peak.get("wind_dir_label"):
            wind_bits.append(str(peak["wind_dir_label"]))
        if peak.get("wind_intensity"):
            wind_bits.append(str(peak["wind_intensity"]))
        if peak.get("wind_speed_kmh") is not None:
            wind_bits.append(f"{peak['wind_speed_kmh']:.0f} km/h")
        rating = peak.get("peak_rating")
        rating_txt = format_rating_line(rating) if rating else "Sin valoración de pico"
        conf = (peak.get("confidence") or {}).get("level") or "—"
        profile_note = ""
        for prof in self.payload.get("profiles") or []:
            if prof.get("peak_id") == peak.get("peak_id"):
                profile_note = f"Perfil: {prof.get('status')}"
                break
        summary = "\n".join(
            [
                f"Condición: {peak.get('condition_label')}",
                f"Tamaño surfeable estimado: {size_txt}",
                f"Viento: {' '.join(wind_bits) or 'n/d'}",
                f"Confianza: {conf}",
                rating_txt,
                profile_note,
            ]
        )
        self.query_one("#detail-summary", Static).update(summary)

        samples = peak.get("evolution_samples") or []
        if samples:
            evo_lines = []
            for sample in samples:
                wind = []
                if sample.get("wind_dir_label"):
                    wind.append(str(sample["wind_dir_label"]))
                if sample.get("wind_speed_kmh") is not None:
                    wind.append(f"{sample['wind_speed_kmh']:.0f} km/h")
                if sample.get("wind_intensity"):
                    wind.append(str(sample["wind_intensity"]))
                size_p = sample.get("size_point_m")
                size_s = f"{size_p:.1f} m" if size_p is not None else "—"
                flag = " (incierto/incompleto)" if sample.get("incomplete_or_uncertain") else ""
                evo_lines.append(
                    f"{sample.get('band')}: {sample.get('local_hour')}  {size_s}  "
                    f"{' '.join(wind)}  {sample.get('condition_label') or ''}{flag}"
                )
            self.query_one("#detail-evolution", Static).update("\n".join(evo_lines))
        else:
            self.query_one("#detail-evolution", Static).update("Sin muestras en la ventana de análisis.")

        window = peak.get("best_window")
        if window:
            self.query_one("#detail-window", Static).update(
                f"{window.get('start_at')} – {window.get('end_at')}  "
                f"({window.get('duration_minutes')} min, {window.get('condition')})"
            )
        else:
            self.query_one("#detail-window", Static).update(
                "No hay una ventana clara respaldada por el motor para este pico."
            )

        analysis = peak.get("peak_analysis")
        if analysis:
            self.query_one("#detail-analysis", Static).update(format_analysis_block(analysis))
        else:
            reason = peak.get("peak_analysis_absent_reason") or "Sin análisis de pico."
            self.query_one("#detail-analysis", Static).update(reason)

        tech = self.query_one("#technical", TechnicalDetails)
        tech.collapse()
        tech.set_body(self._technical_body(peak))

    def _technical_body(self, peak: dict[str, Any]) -> str:
        size = peak.get("size") or {}
        criteria = self.payload.get("criteria") or {}
        data_times = self.payload.get("data_times") or {}
        lines = [
            f"Snapshot: {self.payload.get('snapshot_id')}",
            f"Criterios: {criteria.get('criteria_version')}  k={criteria.get('point_k')} "
            f"[{criteria.get('range_k_low')}–{criteria.get('range_k_high')}]",
            f"Hs cruda: {size.get('raw_hs_m')}  → tamaño derivado punto: {size.get('point_m')} m",
            f"Rango derivado: {size.get('minimum_m')}–{size.get('maximum_m')} m  método: {size.get('method')}",
            f"Datos: {data_times.get('meteorological_updated_at_local') or 'No disponible'}",
            SHARED_GRID,
        ]
        for source in self.payload.get("sources") or []:
            lines.append(
                f"Fuente {source.get('source_id')}: {source.get('model')} "
                f"status={source.get('status')} edad={source.get('data_age_seconds')}s "
                f"corrida={source.get('model_run_availability')}"
            )
        conf = peak.get("confidence") or {}
        if conf.get("caps") or conf.get("degradations"):
            lines.append(f"Confianza caps={conf.get('caps')} degradations={conf.get('degradations')}")
        lines.append(f"Códigos: {', '.join(peak.get('reason_codes') or []) or '—'}")
        lines.append("Hs del modelo no es la altura de rompiente en playa.")
        return "\n".join(lines)

    def action_back(self) -> None:
        report = getattr(self.app, "forecast_screen", None)
        if report is not None:
            report.day_index = self.day_index
            report.peak_index = self.peak_index
            report._render_day()
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
        self._render()


class HelpScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cerrar"),
        Binding("q", "app.pop_screen", "Cerrar"),
    ]

    def compose(self) -> ComposeResult:
        path = config_dir() / "peaks.json"
        yield Vertical(
            Static(
                "\n".join(
                    [
                        "Ayuda — SURF · LA PALOMA",
                        "",
                        "↑↓ cambiar día   ←→ pico   Enter detalle   Esc volver",
                        "D detalles técnicos (en detalle)   R actualizar   o solo guardado   Q salir",
                        "",
                        "La valoración 1–5 es una codificación ordinal del grado del motor,",
                        "no una probabilidad ni un skill score calibrado.",
                        "",
                        f"Vocabulario: {FR017_LEGEND}",
                        "",
                        "Hs del modelo ≠ altura de rompiente. k × Hs es provisional.",
                        SHARED_GRID,
                        f"Perfiles (solo archivo, sin pantalla): {path}",
                        "Datos: Open-Meteo (CC BY 4.0)  https://open-meteo.com/",
                    ]
                ),
                id="help-body",
            )
        )
