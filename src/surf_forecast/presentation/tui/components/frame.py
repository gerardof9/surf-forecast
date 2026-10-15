"""Unicode title-in-border Frame (FR-G11)."""

from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Frame(Vertical):
    """Panel with title embedded in the top Unicode border."""

    DEFAULT_CSS = """
    Frame {
        height: auto;
        margin: 0 1 1 0;
    }
    Frame > .frame-edge {
        height: 1;
        color: #565656;
    }
    Frame.focused > .frame-edge {
        color: #00a2fa;
        text-style: bold;
    }
    Frame > #frame-body {
        height: auto;
        padding: 0 1;
        color: #fffbf6;
    }
    """

    def __init__(
        self,
        title: str = "",
        content: str = "",
        *,
        focused: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._title = title
        self._content = content
        self._focused = focused
        if focused:
            self.add_class("focused")

    def compose(self) -> ComposeResult:
        yield Static(self._top_line(40), id="frame-top", classes="frame-edge", markup=False)
        yield Static(self._content, id="frame-body", markup=False)
        yield Static(self._bottom_line(40), id="frame-bottom", classes="frame-edge", markup=False)

    def on_mount(self) -> None:
        self._refresh_edges()

    def on_resize(self, event: Any) -> None:  # noqa: ANN401
        self._refresh_edges()

    def set_title(self, title: str) -> None:
        self._title = title
        self._refresh_edges()

    def set_body(self, content: str) -> None:
        self._content = content
        try:
            self.query_one("#frame-body", Static).update(content)
        except Exception:
            pass
        self._refresh_edges()

    def set_focused(self, focused: bool) -> None:
        self._focused = focused
        self.set_class(focused, "focused")
        self._refresh_edges()

    def _width(self) -> int:
        w = self.size.width if self.size.width > 4 else 40
        return max(12, w)

    def _top_line(self, width: int) -> str:
        title = f" {self._title} " if self._title else ""
        # ╭─ title ────────╮
        inner = width - 2
        if len(title) + 2 > inner:
            title = title[: max(0, inner - 2)]
        fill = max(1, inner - len(title) - 1)
        edge = "═" if self._focused else "─"
        return f"╭{edge}{title}{edge * fill}╮"

    def _bottom_line(self, width: int) -> str:
        inner = max(1, width - 2)
        return "╰" + ("─" * inner) + "╯"

    def _refresh_edges(self) -> None:
        width = self._width()
        try:
            self.query_one("#frame-top", Static).update(self._top_line(width))
            self.query_one("#frame-bottom", Static).update(self._bottom_line(width))
        except Exception:
            pass
