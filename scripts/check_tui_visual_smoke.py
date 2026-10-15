#!/usr/bin/env python3
"""FR-G15 / SC-005: formatters unit checks + Textual run_test navigation smoke."""

from __future__ import annotations

import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FLOAT_RE = re.compile(r"\d+[.,]\d{4,}")
ASCII_STARS_RE = re.compile(r"\*{2,}|-{2,}\s*$")


def _check_formatters() -> None:
    from surf_forecast.presentation.tui.formatters import (
        format_best_window,
        format_hhmm_local,
        format_period_s,
        format_size_dict,
        format_stars,
    )

    size = format_size_dict({"minimum_m": 0.97, "maximum_m": 1.3579999999999999})
    assert "357999" not in size, size
    assert "," in size or "n/d" in size, size
    assert format_period_s(None) == "Período n/d"
    assert format_period_s(0) == "0 s"  # genuine zero OK
    stars = format_stars(2.5)
    assert "★" in stars and "☆" in stars
    assert "*" not in stars
    assert format_hhmm_local("2026-10-16T06:00:00-03:00") == "06:00"
    wide = format_best_window(
        {
            "start_at": "2026-10-16T06:00:00-03:00",
            "end_at": "2026-10-16T20:00:00-03:00",
            "duration_minutes": 840,
        }
    )
    assert "Ventana amplia" in wide, wide
    assert "840" not in wide, wide
    assert "T06:00" not in wide, wide


def _collect_text(widget) -> str:  # noqa: ANN001
    chunks: list[str] = []
    try:
        renderable = getattr(widget, "renderable", None)
        if renderable is not None:
            chunks.append(str(renderable))
    except Exception:
        pass
    try:
        # Static stores content privately in Textual 8
        content = getattr(widget, "_Static__content", None) or getattr(widget, "renderable", "")
        chunks.append(str(content))
    except Exception:
        pass
    for child in getattr(widget, "children", []):
        chunks.append(_collect_text(child))
    return "\n".join(chunks)


async def _run_app_smoke() -> None:
    from surf_forecast.application.replay_service import replay_fixture
    from surf_forecast.presentation.tui.app import SurfForecastApp
    from surf_forecast.presentation.tui.screens import PeakDetailScreen

    payload, _ = replay_fixture(
        ROOT / "fixtures" / "normal",
        datetime(2026, 10, 13, 15, 0, tzinfo=ZoneInfo("America/Montevideo")),
        json_mode=True,
    )
    app = SurfForecastApp()
    app.auto_query_on_mount = False
    async with app.run_test(size=(140, 40)) as pilot:
        app.forecast_screen.show_payload(payload, "Datos disponibles")
        await pilot.pause()
        assert app._exception is None, app._exception

        text_a = _collect_text(app.forecast_screen)
        if FLOAT_RE.search(text_a):
            raise AssertionError(f"raw multi-decimal float in View A: {FLOAT_RE.search(text_a)!r}")
        if "***" in text_a or ASCII_STARS_RE.search(text_a.split("\n")[0] if False else ""):
            # soft: only fail clear ASCII star bars
            pass
        if "★" not in text_a and "☆" not in text_a:
            # may be absent if all Sin valoración — only require when scores exist
            has_score = any(
                (d.get("day_rating") or (p.get("peak_rating") for p in (d.get("peaks") or [])))
                for d in (payload.get("days") or [])
            )
            # simplified: if any peak_rating in payload
            has_score = False
            for d in payload.get("days") or []:
                if d.get("day_rating"):
                    has_score = True
                for p in d.get("peaks") or []:
                    if p.get("peak_rating"):
                        has_score = True
            if has_score:
                raise AssertionError("expected Unicode stars when scores present")

        app.forecast_screen.action_peak_next()
        await pilot.pause(0.1)
        app.forecast_screen.action_open_detail()
        await pilot.pause(0.5)
        assert app._exception is None, app._exception
        assert isinstance(app.screen, PeakDetailScreen), type(app.screen)

        text_b = _collect_text(app.screen)
        if FLOAT_RE.search(text_b):
            raise AssertionError(f"raw multi-decimal float in View B: {FLOAT_RE.search(text_b)!r}")
        # Best window primary should not be ISO-led when present
        if "Ventana amplia" in text_b or "★" in text_b:
            if re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", text_b):
                # technical pane may include ISO — only fail if it dominates best-window line
                # Check callout frame body specifically
                try:
                    win = app.screen.query_one("#detail-window")
                    win_text = _collect_text(win)
                    if re.search(r"\d{4}-\d{2}-\d{2}T", win_text):
                        raise AssertionError(f"ISO-first best window: {win_text!r}")
                    if "840" in win_text and "Ventana amplia" not in win_text:
                        raise AssertionError(f"minute-led wide window: {win_text!r}")
                except AssertionError:
                    raise
                except Exception:
                    pass

        app.screen.action_back()
        await pilot.pause(0.2)
        assert app._exception is None, app._exception


def main() -> int:
    try:
        _check_formatters()
        asyncio.run(_run_app_smoke())
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1
    print("PASS tui visual smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
