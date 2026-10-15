# Quickstart / manual validation: 005-daily-brief

**Date**: 2026-10-15  
**Branch**: `005-daily-brief`

## Prerequisites

- Repo venv with project deps (`Textual` 8.x)
- A normal forecast fixture or live on-demand run that yields ≥2 local days

## 1. Presentation contract check

```powershell
.\.venv\Scripts\python.exe scripts\check_report_presentation.py
```

Expect:

- `schema_version` `1.2.0`
- Exactly two days
- Each day has `brief` with worth_spots ≤3, fair+ only
- Empty worth ⇒ null height/go_window

## 2. TUI smoke

```powershell
.\.venv\Scripts\python.exe scripts\check_tui_visual_smoke.py
```

Expect (after implement updates):

- Two day cards
- No `PICOS DEL DÍA` / `LEYENDA`
- No peak-detail navigation

## 3. Manual TUI read (SC-001 / SC-004)

```powershell
.\.venv\Scripts\python.exe -m surf_forecast
# or project’s usual TUI entrypoint
```

For Hoy card, in one short read note:

1. Worth considering? (condition + headline)
2. Preferred time (`HH:MM–HH:MM` or honest empty/wide)
3. Up to three beach names (or “ningún pico claro”)

Repeat for Mañana. Confirm prose feels plain (not `≈` / Hs cruda / “ventana de análisis” as lead).

## 4. CLI / JSON parity

Run the same report to CLI and JSON; confirm the same headline, body, go_window.display, and worth spot names as the TUI cards (layout may differ; content must match).

## 5. Edge fixtures

| Case | Expect |
|------|--------|
| Only one fair+ peak | One worth spot; height/window from that peak |
| All poor | Empty list + message; height/window null |
| Wide best_window | “ventana amplia” (or equiv.) + times; not minute-led |
| Narrow terminal | Cards stack; no crash |

## Done when

- Checks above pass
- SC-001…SC-006 manually satisfied on at least one normal + one empty-worth fixture
