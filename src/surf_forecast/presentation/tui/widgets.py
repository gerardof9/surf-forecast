"""Legacy re-exports for older imports — prefer components/ and formatters."""

from __future__ import annotations

from surf_forecast.presentation.tui.components import StatusBar
from surf_forecast.presentation.tui.formatters import (
    format_analysis_block,
    format_day_chip,
    format_header,
    format_rating_block,
    format_size_dict,
    format_stars,
)
from surf_forecast.presentation.tui.theme import ATTRIBUTION, SHARED_GRID

__all__ = [
    "ATTRIBUTION",
    "SHARED_GRID",
    "StatusBar",
    "format_analysis_block",
    "format_day_chip",
    "format_header",
    "format_rating_block",
    "format_size_dict",
    "format_stars",
]
