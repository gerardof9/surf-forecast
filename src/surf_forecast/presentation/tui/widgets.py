"""Legacy re-exports — prefer formatters/ and components/."""

from __future__ import annotations

from textual.widgets import Footer

from surf_forecast.presentation.tui.components import StatusBar, TechnicalDetails
from surf_forecast.presentation.tui.formatters import (
    condition_role as condition_style,
    format_analysis_block,
    format_day_chip,
    format_header,
    format_rating_block,
    format_score_num,
    format_stars,
)
from surf_forecast.presentation.tui.theme import ATTRIBUTION, LEGEND_LINES, SECTION_PEAKS, SHARED_GRID

__all__ = [
    "ATTRIBUTION",
    "LEGEND_LINES",
    "SECTION_PEAKS",
    "SHARED_GRID",
    "AttributionFooter",
    "StatusBar",
    "TechnicalDetails",
    "condition_style",
    "format_analysis_block",
    "format_day_chip",
    "format_header",
    "format_rating_block",
    "format_score_num",
    "format_stars",
]


class AttributionFooter(Footer):
    pass
