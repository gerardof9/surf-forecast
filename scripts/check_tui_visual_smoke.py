#!/usr/bin/env python3
"""TUI smoke for 005-daily-brief: formatters + two DayBrief cards, no View B."""

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
    assert format_period_s(0) == "0 s"
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
    from surf_forecast.presentation.tui.components.day_brief_card import DayBriefCard

    payload, _ = replay_fixture(
        ROOT / "fixtures" / "normal",
        datetime(2026, 10, 13, 15, 0, tzinfo=ZoneInfo("America/Montevideo")),
        json_mode=True,
    )
    assert payload.get("schema_version") == "1.2.0", payload.get("schema_version")
    assert len(payload.get("days") or []) == 2

    app = SurfForecastApp()
    app.auto_query_on_mount = False
    async with app.run_test(size=(140, 40)) as pilot:
        app.forecast_screen.show_payload(payload, "Datos disponibles")
        await pilot.pause()
        assert app._exception is None, app._exception

        text = _collect_text(app.forecast_screen)
        if FLOAT_RE.search(text):
            raise AssertionError(f"raw multi-decimal float in home: {FLOAT_RE.search(text)!r}")
        if "PICOS DEL DÍA" in text:
            raise AssertionError("PICOS DEL DÍA must be absent")
        if "LEYENDA" in text:
            raise AssertionError("LEYENDA must be absent")

        # Dual timestamps (FR-014)
        header = _collect_text(app.forecast_screen.query_one("#report-header"))
        if "Consulta" not in header and "consulta" not in header.lower():
            # header_text uses "Consulta:"
            if "Consulta:" not in header:
                raise AssertionError(f"missing consultation timestamp in header: {header!r}")
        if "Datos" not in header and "meteorológ" not in header.lower():
            if "Datos meteorológicos:" not in header:
                raise AssertionError(f"missing data timestamp in header: {header!r}")

        cards = list(app.forecast_screen.query(DayBriefCard))
        if len(cards) != 2:
            raise AssertionError(f"expected 2 DayBriefCard, got {len(cards)}")

        # Enter must not open peak detail
        await pilot.press("enter")
        await pilot.pause(0.2)
        assert app._exception is None, app._exception
        assert type(app.screen).__name__ != "PeakDetailScreen", type(app.screen)
        # PeakDetailScreen should not be import-routed from screens for home
        from surf_forecast.presentation.tui import screens as screens_mod

        if hasattr(screens_mod, "PeakDetailScreen"):
            raise AssertionError("PeakDetailScreen must be removed from screens module")


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
