# Implementation Plan: TUI visual craft (graphic layer)

**Branch**: `004-tui-visual-craft` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-tui-visual-craft/spec.md`  
**Binding visual contract**: [graphic-layer.md](./graphic-layer.md) (source of truth for chrome, layout, components, gates)  
**User planning prompt**: Plan graphic layer only — custom Unicode Frame, PeakCard grid, View B 3-zone board, formatters, StatusBar; do not change forecast engine or frozen presentation 1.1.0 semantics; baselines in `references/`.

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the current Textual “diagnostic dump” chrome with a professional graphic layer that matches `references/modelo.png` hierarchy (LazyGit/btop/K9s quality bar): custom Unicode `Frame` with title-in-border, structured `PeakCard` grid (up to 5 columns), View B three-zone board, display hygiene formatters, and a dedicated StatusBar. Clarifications FR-G11–FR-G15 are decided. Domain evaluation and presentation 1.1.0 field semantics stay frozen; only `src/surf_forecast/presentation/tui/` (+ pure display formatters) change.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Textual `>=8.2,<9` (existing); stdlib only for formatters/smoke helpers — no new paid UI kits

**Storage**: N/A (reads existing presentation payload / fixtures; no new persistence schema)

**Testing**: `scripts/check_report_presentation.py` (must still pass); new Textual `run_test` smoke script for hygiene + Enter/Esc navigation (FR-G15 / SC-005); manual VS-* screenshots — no pixel-diff CI

**Target Platform**: Windows terminal (primary) + any UTF-8 capable terminal; PyInstaller exe via existing `scripts/build-exe.ps1`

**Project Type**: Local on-demand CLI/TUI desktop tool (single package `surf_forecast`)

**Performance Goals**: Interactive TUI; View A/B populate without perceptible lag on five-day / five-peak fixtures; Frame paint cost negligible vs data load

**Constraints**:
- No engine / evaluation threshold changes
- No presentation 1.1.0 semantic divergence
- No Nerd Font / decorative wave-pin icons
- Never override Textual `Widget._render` for content population
- Active Spec Kit feature = `specs/004-tui-visual-craft` only

**Scale/Scope**: Two screens (View A daily report, View B peak detail) + Help modal; ~8–12 TUI components; theme tokens; formatters; one smoke runner

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (Surf Forecast La Paloma).
Any FAIL that must proceed requires an entry in Complexity Tracking.

- [x] **I. Zero cost / personal use**: Textual already free; no paid fonts/services
- [x] **II. On-demand execution**: Local TUI only; no daemons
- [x] **III. Configurable criteria**: Untouched — graphic layer does not alter criteria
- [x] **IV. Modular simplicity**: Changes confined to `presentation/tui`; domain separate
- [x] **V. Honest uncertainty**: Formatters/labels must not hide provisional/incomplete; wide windows labeled honestly (FR-G14)
- [x] **VI. Inform, don't decide**: Badges/ratings remain indicators; no “go surf” chrome
- [x] **VII. Reality validation**: Visual gates vs real captures + modelo; not claimed forecast skill change
- [x] **VIII. No invented/confused data**: Hygiene forbids fake `0 s` / raw floats; offshore≠beach already in frozen copy
- [x] **IX. Traceability**: Tech details remain available (collapsed); snapshot ids stay in tech pane
- [x] **X. Simplicity first**: Reuse Textual; custom Frame only where CSS borders fail the contract
- [x] **XI. Pragmatic verification**: Manual screenshots + focused `run_test` smoke; no CI pixel suite
- [x] **XII. Graceful degradation**: Narrow layout / missing metrics use `n/d` and Help; no crash
- [x] **XIII. Privacy / minimal scope**: No auth/telemetry
- [x] **XIV. Implementation discipline**: Clarifications closed; graphic-layer is binding

**Post-design re-check**: PASS — contracts document display-only transforms; no engine coupling.

## Project Structure

### Documentation (this feature)

```text
specs/004-tui-visual-craft/
├── plan.md                 # This file
├── research.md             # Phase 0
├── data-model.md           # Phase 1 (display/view-model entities)
├── quickstart.md           # Phase 1 manual + smoke validation
├── graphic-layer.md        # Binding visual contract (pre-existing)
├── spec.md                 # Feature spec + clarifications
├── references/             # modelo + non-compliant baselines
├── contracts/
│   ├── tui-chrome.md       # Component/module boundaries
│   └── display-hygiene.md  # Formatter + anti-pattern contract
└── tasks.md                # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
src/surf_forecast/presentation/tui/
├── app.py                 # App shell, CSS theme tokens, workers, bindings
├── screens.py             # DailyReportScreen (View A), PeakDetailScreen (View B), Help
├── formatters.py          # NEW — pure display hygiene (meters, period, stars, HH:MM, confidence ES)
├── theme.py               # NEW — token names / helpers shared with CSS roles
├── widgets.py             # Legacy helpers trimmed or re-export; avoid god-file growth
└── components/            # NEW — Frame, Badge, PeakCard, RatingHero, EvolutionTable, …
    ├── __init__.py
    ├── frame.py
    ├── badge.py
    ├── peak_card.py
    ├── rating_hero.py
    ├── analysis_panel.py
    ├── evolution_table.py
    ├── best_window.py
    ├── status_bar.py
    └── technical_details.py

scripts/
├── check_report_presentation.py   # unchanged must-pass
└── check_tui_visual_smoke.py      # NEW — Textual run_test hygiene + nav (FR-G15)
```

**Structure Decision**: Single-package Surf Forecast app. Graphic craft lives entirely under `presentation/tui/` with a new `components/` package and pure `formatters.py`. No parallel frontend. Domain/application packages are read-only for this feature.

## Complexity Tracking

> No constitution violations requiring exceptions. Custom `Frame` is justified: CSS-only borders failed the professional chrome bar and were clarified as non-compliant (FR-G11).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Implementation Approach (for `/speckit-tasks`)

Ordered phases from `graphic-layer.md` §13:

1. Display formatters (hygiene) + smoke harness skeleton  
2. Theme tokens + `Frame` + StatusBar  
3. `PeakCard` + PeakGrid column rules (View A win)  
4. `RatingHero` + `AnalysisPanel` + day Banner  
5. View B three-zone layout + `EvolutionTable` + `BestWindowCallout`  
6. LegendRail / Help + responsive breakpoints  
7. VS-* screenshots + exe rebuild  

**Keyboard (clarified)**: Day-list focus primary; `←→` peak selection highlight; `Enter` → View B; Esc back; `D` tech toggle.
