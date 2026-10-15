"""Best window callout with wide-window honesty (FR-G14)."""

from __future__ import annotations

from typing import Any

from surf_forecast.presentation.tui.components.frame import Frame
from surf_forecast.presentation.tui.formatters import format_best_window


class BestWindowCallout(Frame):
    DEFAULT_CSS = """
    BestWindowCallout > .frame-edge {
        color: #ffc400;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("MEJOR VENTANA ESTIMADA", "", **kwargs)

    def set_window(self, window: dict[str, Any] | None) -> None:
        self.set_body(format_best_window(window))
