"""Home sections: dual-day labelled analysis + worth spots (005)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from surf_forecast.presentation.tui.theme import SECTION_PEAKS, TOKENS as T


class AnalysisSection(Vertical):
    """Label/value analysis for Hoy and Mañana."""

    DEFAULT_CSS = f"""
    AnalysisSection {{
        height: auto;
        margin: 0 1 0 1;
        padding: 1 1 0 1;
        border-top: solid {T['border.dim']};
    }}
    AnalysisSection > #analysis-head {{
        color: {T['text.dim']};
        text-style: bold;
        height: 1;
    }}
    AnalysisSection > #analysis-body {{
        color: {T['text.secondary']};
        height: auto;
    }}
    AnalysisSection > #analysis-note {{
        color: {T['text.dim']};
        height: auto;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Static("ANÁLISIS", id="analysis-head", markup=False)
        yield Static("", id="analysis-body", markup=False)
        yield Static("", id="analysis-note", markup=False)

    def set_days(self, days: list[dict[str, Any]]) -> None:
        blocks: list[str] = []
        notes: list[str] = []
        for day in days[:2]:
            brief = (day or {}).get("brief") or {}
            label = brief.get("label") or ""
            title = (day or {}).get("display_title") or (day or {}).get("local_date") or ""
            header = f"{label} · {title}".strip(" ·") or "Día"
            text = brief.get("analysis") or brief.get("body") or "—"
            blocks.append(f"{header}\n{text}")
            for note in brief.get("limitations") or []:
                # Skip long provisional prose; chip/help covers profiles
                if note and "calibrad" not in note.lower() and note not in notes:
                    notes.append(str(note))
        body = "\n\n".join(blocks) if blocks else "—"
        self.query_one("#analysis-body", Static).update(body)
        note_widget = self.query_one("#analysis-note", Static)
        if notes:
            note_widget.update("· " + " · ".join(notes[:1]))
            note_widget.display = True
        else:
            note_widget.update("")
            note_widget.display = False

    def set_day(self, day: dict[str, Any] | None) -> None:
        self.set_days([day] if day else [])


class SpotsSection(Vertical):
    """Worth spots for Hoy and Mañana — aligned columns."""

    DEFAULT_CSS = f"""
    SpotsSection {{
        height: auto;
        margin: 0 1 1 1;
        padding: 0 1 1 1;
        border-top: solid {T['border.dim']};
    }}
    SpotsSection > #spots-head {{
        color: {T['text.dim']};
        text-style: bold;
        height: 1;
        margin: 1 0 0 0;
    }}
    SpotsSection > #spots-body {{
        color: {T['text.secondary']};
        height: auto;
    }}
    """

    def compose(self) -> ComposeResult:
        yield Static(SECTION_PEAKS, id="spots-head", markup=False)
        yield Static("", id="spots-body", markup=False)

    def set_days(self, days: list[dict[str, Any]]) -> None:
        lines: list[str] = []
        for day in days[:2]:
            brief = (day or {}).get("brief") or {}
            label = (brief.get("label") or "").ljust(7)
            spots = brief.get("worth_spots") or []
            if spots:
                for i, spot in enumerate(spots, start=1):
                    name = (spot.get("display_name") or spot.get("peak_id") or "—")[:14].ljust(14)
                    cond = spot.get("condition_label") or "—"
                    lines.append(f"{label} {i}. {name}  {cond}")
            else:
                empty = brief.get("empty_spots_message") or "Ningún pico claro para ir."
                lines.append(f"{label} {empty}")
        self.query_one("#spots-body", Static).update("\n".join(lines) if lines else "—")

    def set_day(self, day: dict[str, Any] | None) -> None:
        self.set_days([day] if day else [])
