"""Analysis sentences with kind prefixes."""

from __future__ import annotations

from typing import Any

from surf_forecast.presentation.tui.components.frame import Frame
from surf_forecast.presentation.tui.formatters import format_analysis_block


class AnalysisPanel(Frame):
    def __init__(self, title: str = "ANÁLISIS DEL DÍA", **kwargs: Any) -> None:
        super().__init__(title, "", **kwargs)

    def set_analysis(self, analysis: dict[str, Any] | None, *, absent: str | None = None) -> None:
        text = format_analysis_block(analysis)
        if not text:
            text = absent or "Sin análisis disponible."
        self.set_body(text)
