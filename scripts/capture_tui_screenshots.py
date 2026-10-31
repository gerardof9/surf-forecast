#!/usr/bin/env python3
"""Capture TUI home at brief sizes: 120×30, 160×40, 190×49."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Cursor / CI often set NO_COLOR=1 → Textual renders monochrome SVGs.
# Force a color-capable environment before importing Textual/Rich.
os.environ.pop("NO_COLOR", None)
os.environ["FORCE_COLOR"] = "1"
os.environ.setdefault("TERM", "xterm-256color")
os.environ["COLORTERM"] = "truecolor"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "docs" / "ui-captures"
# Brief §10 method: three canonical sizes.
SIZES = ((120, 30), (160, 40), (190, 49))


def _svg_text_dump(svg_path: Path) -> str:
    import html
    import re

    if not svg_path.exists():
        return ""
    svg = svg_path.read_text(encoding="utf-8")
    texts = [html.unescape(t).replace("\xa0", " ") for t in re.findall(r"<text[^>]*>([^<]*)</text>", svg)]
    lines: list[str] = []
    deco = set("▊▎▏▁▔▆█│┌┐└┘─")
    for text in texts:
        stripped = text.strip()
        if not stripped or set(stripped) <= deco:
            continue
        if lines and lines[-1] == stripped:
            continue
        lines.append(stripped)
    return "\n".join(lines) + ("\n" if lines else "")


async def _capture() -> list[Path]:
    from surf_forecast.presentation.tui.app import SurfForecastApp
    from surf_forecast.presentation.tui.demo_payload import build_demo_payload

    payload = build_demo_payload()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("home_*"):
        old.unlink()

    paths: list[Path] = []
    for width, height in SIZES:
        app = SurfForecastApp()
        app.auto_query_on_mount = False
        async with app.run_test(size=(width, height)) as pilot:
            app.forecast_screen.show_payload(payload, "Demo (datos fijos)")
            await pilot.pause()
            await pilot.press("left")
            await pilot.pause()
            svg_name = f"home_{width}x{height}.svg"
            app.save_screenshot(filename=svg_name, path=str(OUT))
            svg_path = OUT / svg_name
            paths.append(svg_path)
            text_path = OUT / f"home_{width}x{height}.txt"
            text_path.write_text(_svg_text_dump(svg_path), encoding="utf-8")
            paths.append(text_path)
            # Alias legacy name for 120-wide
            if width == 120:
                alias = OUT / "home_120cols.svg"
                alias.write_text(svg_path.read_text(encoding="utf-8"), encoding="utf-8")
                paths.append(alias)
    return paths


def main() -> int:
    paths = asyncio.run(_capture())
    print("Captured:")
    for path in paths:
        print(f"  {path}  ({path.stat().st_size if path.exists() else 0} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
