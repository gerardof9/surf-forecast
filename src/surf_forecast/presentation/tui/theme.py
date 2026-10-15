"""Graphic-layer theme token roles (CSS class / color map)."""

from __future__ import annotations

# Role ids used as CSS classes / documentation — hex for explicit CSS in app.py
TOKENS = {
    "canvas": "#0b1220",
    "body": "#fffbf6",
    "muted": "#888888",
    "accent": "#00a2fa",
    "border_idle": "#565656",
    "border_focus": "#00a2fa",
    "border_selected_card": "#00d4ff",
    "status_bg": "#1a2740",
    "warning": "#ffc400",
    "cond_good": "#9be205",
    "cond_fair": "#ffc400",
    "cond_variable": "#d78700",
    "cond_poor": "#ff260e",
    "cond_uncertain": "#815bb5",
    "cond_incomplete": "#888888",
    "cond_window": "#888888",
}

ATTRIBUTION = "Datos: Open-Meteo (CC BY 4.0)"
SHARED_GRID = "Los picos cercanos comparten la misma celda regional del modelo."
SECTION_PEAKS = "PICOS DEL DÍA"

LEGEND_LINES = [
    "● Buena oportunidad  4–5",
    "● Surfeable           3",
    "● Variable            2",
    "● Pocas olas          1",
    "● Incierto / incompleto",
]
