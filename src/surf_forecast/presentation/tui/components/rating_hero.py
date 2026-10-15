"""Day / peak rating hero block."""

from __future__ import annotations

from typing import Any

from surf_forecast.presentation.tui.components.frame import Frame
from surf_forecast.presentation.tui.formatters import format_rating_block


class RatingHero(Frame):
    def __init__(self, title: str = "VALORACIÓN DEL DÍA", **kwargs: Any) -> None:
        super().__init__(title, "", **kwargs)

    def set_rating(self, rating: dict[str, Any] | None, absent: str | None = None) -> None:
        self.set_body(format_rating_block(rating, absent))
