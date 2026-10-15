# Quickstart / validation — 004 TUI visual craft

**Feature**: `004-tui-visual-craft`  
**Branch**: `004-tui-visual-craft`  
**Binding**: [`graphic-layer.md`](./graphic-layer.md) · baselines in [`references/`](./references/)

## Prerequisites

- Python 3.12+ venv with project deps (`textual`)
- Active Spec Kit pin: `.specify/feature.json` → `specs/004-tui-visual-craft`
- Do **not** modify engine thresholds or presentation 1.1.0 semantics for UI reasons

## Run TUI

```powershell
cd D:\repositorio\cursor\dev\surf-forecast
.\.venv\Scripts\python.exe -m surf_forecast
```

Wide terminal recommended (≥ 130 columns) for five-card row checks.

## Automated checks

```powershell
# Frozen presentation / rating / narrative (must still pass)
.\.venv\Scripts\python.exe .\scripts\check_report_presentation.py

# Graphic-layer smoke (add during implement — FR-G15)
.\.venv\Scripts\python.exe .\scripts\check_tui_visual_smoke.py
```

## Manual visual gates (required for sign-off)

Compare hierarchy to `references/modelo.png` (ignore mock numbers). Capture at ~120×40 and 80×24:

| ID | Check |
|----|--------|
| VS-A1 | View A resolved day: dual timestamps + status pill; analysis+hero frames; up to 5 peak cards with badges/metrics/Unicode stars; legend or Help |
| VS-A2 | Window-completed / no day score: one banner; cards still show fields; `Sin valoración` once |
| VS-B1 | View B: summary \| evolution/window/analysis; `HH:MM`; rounded meters; tech collapsed |
| VS-B2 | Tech expanded via `D`; primary path still clear when collapsed |
| VS-N1 | 80×24 usable stack; no crash |

**SC-V01**: In ≤ 5 seconds identify selected day, day score, and best-looking peak card.

## Keyboard smoke (manual)

1. Focus on days after load  
2. `←→` moves peak highlight (focus stays on day list)  
3. `Enter` → View B; `Esc` returns same day+peak  
4. `D` toggles técnicos  

## Rebuild exe (optional after implement)

```powershell
.\scripts\build-exe.ps1
```

## Stop conditions

Do not ship if: engine/presentation checks regress; CSS-only “frames” without Unicode title-in-border; 2-col hard cap on wide terminals; raw floats / ASCII stars / ISO-led wide windows in primary UI; technical pane dominates View B first paint.
