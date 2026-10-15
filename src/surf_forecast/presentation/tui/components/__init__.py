"""Graphic-layer TUI components."""

from surf_forecast.presentation.tui.components.analysis_panel import AnalysisPanel
from surf_forecast.presentation.tui.components.badge import Badge, StatusPill
from surf_forecast.presentation.tui.components.best_window import BestWindowCallout
from surf_forecast.presentation.tui.components.evolution_table import EvolutionTable
from surf_forecast.presentation.tui.components.frame import Frame
from surf_forecast.presentation.tui.components.header_bar import Banner, header_text, window_completed_banner
from surf_forecast.presentation.tui.components.peak_card import PeakCard
from surf_forecast.presentation.tui.components.rating_hero import RatingHero
from surf_forecast.presentation.tui.components.status_bar import StatusBar
from surf_forecast.presentation.tui.components.technical_details import TechnicalDetails

__all__ = [
    "AnalysisPanel",
    "Badge",
    "Banner",
    "BestWindowCallout",
    "EvolutionTable",
    "Frame",
    "PeakCard",
    "RatingHero",
    "StatusBar",
    "StatusPill",
    "TechnicalDetails",
    "header_text",
    "window_completed_banner",
]
