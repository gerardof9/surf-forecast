"""Single theme file — design tokens (brief §3). No inline colors in widgets."""

from __future__ import annotations

TOKENS = {
    "bg.app": "#0B1220",
    "bg.panel": "#101A2B",
    "bg.raised": "#16243A",
    "border.dim": "#24364F",
    "border.focus": "#4FC3F7",
    "accent": "#4FC3F7",
    "text.primary": "#E6EDF3",
    "text.secondary": "#B6C4D4",
    "text.dim": "#7F93A8",
    "grade.muy_buena": "#3DDC97",
    "grade.buena": "#9BE15D",
    "grade.razonable": "#FFD447",
    "grade.pequenas": "#FF9F43",
    "grade.sin_olas": "#8A94A6",
    "state.incierto": "#B57BFF",
    "state.incompleto": "#8EA4BD",
    "warn": "#F5B84B",
    "error": "#F0616D",
    "chip_text": "#0B1220",
}

# Backward-compatible aliases used by older widgets during transition.
TOKENS.update(
    {
        "canvas": TOKENS["bg.app"],
        "panel": TOKENS["bg.panel"],
        "panel_focus": TOKENS["bg.raised"],
        "body": TOKENS["text.primary"],
        "muted": TOKENS["text.dim"],
        "border_idle": TOKENS["border.dim"],
        "border_focus": TOKENS["border.focus"],
        "border_muted": TOKENS["border.dim"],
        "status_bg": TOKENS["bg.raised"],
        "warning": TOKENS["warn"],
        "cond_good": TOKENS["grade.buena"],
        "cond_fair": TOKENS["grade.razonable"],
        "cond_variable": TOKENS["grade.pequenas"],
        "cond_poor": TOKENS["grade.sin_olas"],
        "cond_uncertain": TOKENS["state.incierto"],
        "cond_incomplete": TOKENS["state.incompleto"],
        "cond_window": TOKENS["state.incompleto"],
    }
)

ATTRIBUTION = "Datos: Open-Meteo (CC BY 4.0)"
SHARED_GRID = "Los picos cercanos comparten la misma celda regional del modelo."
SECTION_PEAKS = "PICOS DE LA PALOMA"

LEGEND_LINES = [
    "● Muy buena",
    "● Buena",
    "● Razonable",
    "● Pequeñas",
    "● Sin olas / Incierto",
]


def css_vars() -> str:
    """Textual CSS block using design tokens (imported once from App)."""
    t = TOKENS
    return f"""
    Screen {{
        layout: vertical;
        background: {t['bg.app']};
        color: {t['text.primary']};
    }}
    #report-header {{
        height: auto;
        max-height: 3;
        padding: 0 1;
        color: {t['text.secondary']};
        border-bottom: solid {t['border.dim']};
    }}
    #home-body {{
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }}
    #brief-row {{
        height: auto;
        layout: horizontal;
        padding: 1 1 0 1;
    }}
    #brief-row.stack {{
        layout: vertical;
    }}
    #help-frame {{ margin: 2 4; width: auto; }}
    Footer {{ display: none; }}
    """
