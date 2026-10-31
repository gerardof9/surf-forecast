"""Grade / status chips — colored background, no brackets (brief §4)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.domain.presentation_labels import CONDITION_CHIP_LABELS, STATE_CHIP_LABELS
from surf_forecast.presentation.tui.formatters import condition_role, condition_role_from_id
from surf_forecast.presentation.tui.theme import TOKENS as T


class Badge(Static):
    """Compact chip: grade color background, dark text, bold."""

    DEFAULT_CSS = f"""
    Badge {{
        height: 1;
        width: auto;
        padding: 0 1;
        text-style: bold;
        color: {T['chip_text']};
        background: {T['grade.sin_olas']};
    }}
    Badge.cond-muy-buena {{ background: {T['grade.muy_buena']}; color: {T['chip_text']}; }}
    Badge.cond-buena {{ background: {T['grade.buena']}; color: {T['chip_text']}; }}
    Badge.cond-razonable {{ background: {T['grade.razonable']}; color: {T['chip_text']}; }}
    Badge.cond-pequenas {{ background: {T['grade.pequenas']}; color: {T['chip_text']}; }}
    Badge.cond-sin-olas {{ background: {T['grade.sin_olas']}; color: {T['chip_text']}; }}
    Badge.cond-uncertain {{ background: {T['state.incierto']}; color: {T['chip_text']}; }}
    Badge.cond-incomplete {{ background: {T['state.incompleto']}; color: {T['chip_text']}; }}
    Badge.cond-window {{ background: {T['state.incompleto']}; color: {T['chip_text']}; }}
    Badge.cond-neutral {{ background: {T['border.dim']}; color: {T['text.primary']}; }}
    Badge.cond-good {{ background: {T['grade.buena']}; color: {T['chip_text']}; }}
    Badge.cond-fair {{ background: {T['grade.razonable']}; color: {T['chip_text']}; }}
    Badge.cond-variable {{ background: {T['grade.pequenas']}; color: {T['chip_text']}; }}
    Badge.cond-poor {{ background: {T['grade.sin_olas']}; color: {T['chip_text']}; }}
    Badge.status-ok {{ background: {T['grade.buena']}; color: {T['chip_text']}; }}
    Badge.status-warn {{ background: {T['warn']}; color: {T['chip_text']}; }}
    """

    def __init__(self, text: str = "", *, role: str | None = None, **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__(text or "", **kwargs)
        self._label = text
        if role:
            self.add_class(role)

    def _clear_cond_classes(self) -> None:
        for cls in list(self.classes):
            if cls.startswith("cond-") or cls.startswith("status-"):
                self.remove_class(cls)

    def set_condition(self, label: str | None, *, condition_id: str | None = None) -> None:
        """Show chip text. Prefer condition_id for color; label for text."""
        chip = label or "—"
        if condition_id and condition_id in CONDITION_CHIP_LABELS:
            chip = CONDITION_CHIP_LABELS[condition_id]
        elif label and label in STATE_CHIP_LABELS.values():
            chip = label
        self._label = chip
        self._clear_cond_classes()
        if condition_id:
            self.add_class(condition_role_from_id(condition_id))
        else:
            self.add_class(condition_role(chip))
        self.update(f" {chip} ")

    def set_status(self, text: str, *, ok: bool = True) -> None:
        self._label = text
        self._clear_cond_classes()
        self.add_class("status-ok" if ok else "status-warn")
        self.update(f" {text} ")


class StatusPill(Badge):
    """Alias for header data-state pill."""
