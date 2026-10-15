"""FR-017 / status badges — text always present (FR-G06, FR-G13)."""

from __future__ import annotations

from typing import Any

from textual.widgets import Static

from surf_forecast.presentation.tui.formatters import condition_role


class Badge(Static):
    """Compact label with semantic condition/status role class."""

    DEFAULT_CSS = """
    Badge {
        height: 1;
        width: auto;
        padding: 0 1;
    }
    Badge.cond-good { color: #9be205; text-style: bold; }
    Badge.cond-fair { color: #ffc400; text-style: bold; }
    Badge.cond-variable { color: #d78700; text-style: bold; }
    Badge.cond-poor { color: #ff260e; text-style: bold; }
    Badge.cond-uncertain { color: #815bb5; }
    Badge.cond-incomplete { color: #888888; }
    Badge.cond-window { color: #888888; }
    Badge.cond-neutral { color: #fffbf6; }
    Badge.status-ok { color: #9be205; text-style: bold; }
    Badge.status-warn { color: #ffc400; }
    """

    def __init__(self, text: str = "", *, role: str | None = None, **kwargs: Any) -> None:
        kwargs.setdefault("markup", False)
        super().__init__(f"[ {text} ]" if text else "", **kwargs)
        self._label = text
        if role:
            self.add_class(role)

    def set_condition(self, label: str | None) -> None:
        text = label or "Sin condición"
        self._label = text
        for cls in list(self.classes):
            if cls.startswith("cond-"):
                self.remove_class(cls)
        role = condition_role(text)
        self.add_class(role)
        self.update(f"[ {text} ]")

    def set_status(self, text: str, *, ok: bool = True) -> None:
        self._label = text
        self.remove_class("status-ok", "status-warn")
        self.add_class("status-ok" if ok else "status-warn")
        self.update(f"[ {text} ]")


class StatusPill(Badge):
    """Alias for header data-state pill."""
