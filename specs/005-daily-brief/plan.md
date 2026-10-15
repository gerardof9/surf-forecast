# Implementation Plan: Daily brief (Hoy / Mañana)

**Branch**: `005-daily-brief` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-daily-brief/spec.md`

**User planning prompt**: Planificar 005-daily-brief según clarifications: DayBrief en contrato compartido (TUI+CLI+JSON); solo Hoy/Mañana en presentación; sin View B; worth-spots fair+ máx 3; altura y go-window del mejor worth-spot; prosa natural; quitar rail DÍAS, PICOS DEL DÍA y LEYENDA. Conservar motor grades/best_window; reescribir narrative/presentation. Documentar excepción constitución VI en Complexity Tracking.

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the 003/004 “5-day board + all peaks + legend + technical narrative” home with a **two-card daily brief** (Hoy / Mañana). Build a shared **DayBrief** in the presentation payload (schema **1.2.0**): plain-Spanish headline + analysis, go-window and height from the **best worth-spot**, and up to three fair-or-better beaches. TUI, CLI, and JSON all consume the same brief. Remove View B. Keep evaluation grades / `best_window` formulas unchanged; extend presentation assembly + narrative templates only. Engine may still compute a longer horizon; presentation emits only two days.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Textual `>=8.2,<9` (existing TUI); stdlib for presentation/narrative; no LLM; no new paid services

**Storage**: N/A for this feature (existing forecast store/fixtures unchanged)

**Testing**: Update `scripts/check_report_presentation.py` for schema 1.2.0 + DayBrief invariants; new/updated Textual smoke (two cards, no PICOS/LEYENDA/View B); manual read of prose on fixtures — constitution XI (no complex CI required)

**Target Platform**: Windows terminal (primary) + UTF-8 terminals; existing PyInstaller exe path

**Project Type**: Local on-demand CLI/TUI (`surf_forecast`)

**Performance Goals**: Interactive TUI; building two DayBriefs from existing day/peak evaluations is negligible vs fetch

**Constraints**:
- Do **not** change grade/score/`best_window` selection formulas in the evaluation engine
- Presentation schema bump **1.1.0 → 1.2.0** (breaking for consumers expecting 5 days / old `day_analysis` shape)
- No Tiempo / Energía metrics
- No View B / peak-detail screen
- Active Spec Kit feature = `specs/005-daily-brief` only
- Constitution VI advisory exception documented in Complexity Tracking

**Scale/Scope**: Shared presentation + narrative rewrite; TUI home rewrite (2× DayBriefCard); CLI/JSON adapters; remove PeakDetailScreen path; checks/smoke updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (Surf Forecast La Paloma).
Any FAIL that must proceed requires an entry in Complexity Tracking.

- [x] **I. Zero cost / personal use**: No paid APIs; template narrative only
- [x] **II. On-demand execution**: Local run; no daemons
- [x] **III. Configurable criteria**: Worth threshold is a presentation filter over existing grades (fair+); engine criteria untouched
- [x] **IV. Modular simplicity**: DayBrief built in presentation/narrative; TUI only renders; evaluation separate
- [x] **V. Honest uncertainty**: Empty worth list, n/d height, wide-window wording; no invented beaches
- [ ] **VI. Inform, don't decide**: **JUSTIFIED FAIL** — home brief MAY recommend when/where (FR-010); still no wave/safety guarantees → see Complexity Tracking
- [x] **VII. Reality validation**: Manual prose review on real fixtures; no superiority claim for forecast skill
- [x] **VIII. No invented/confused data**: Height remains derived; below-threshold peaks not used for height/window; offshore ≠ breaking
- [x] **IX. Traceability**: snapshot_id / criteria_version / sources remain in payload; tech depth may move off interactive path
- [x] **X. Simplicity first**: Two cards + templates; no LLM; no new services
- [x] **XI. Pragmatic verification**: Presentation checks + TUI smoke + manual reads
- [x] **XII. Graceful degradation**: Incomplete Mañana / no worth spots → explicit empty states
- [x] **XIII. Privacy / minimal scope**: Unchanged
- [x] **XIV. Implementation discipline**: Clarifications closed; VI exception explicit

**Post-design re-check**: PASS with same VI justified exception — contracts encode advisory copy + honesty rules; engine unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/005-daily-brief/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── spec.md
├── checklists/requirements.md
├── contracts/
│   ├── presentation-1.2.0.md
│   └── tui-home.md
└── tasks.md                 # /speckit-tasks (not created here)
```

### Source Code (repository root)

```text
src/surf_forecast/
├── domain/
│   ├── narrative.py          # REWRITE — plain DayBrief prose + headline (template_v2)
│   ├── presentation.py       # EXTEND — schema 1.2.0; slice Hoy/Mañana; build DayBrief; worth filter
│   ├── day_rating.py         # REUSE — day condition / scores
│   ├── windows.py            # REUSE — best_window (no formula change)
│   └── models.py             # REUSE — grades, BestWindow, DaySummary
├── presentation/
│   ├── cli.py                # ADAPT — print DayBrief for two days
│   ├── json_output.py        # ADAPT — emit 1.2.0 payload
│   └── tui/
│       ├── app.py            # REMOVE PeakDetailScreen route; bindings/CSS for two cards
│       ├── screens.py        # REWRITE home = 2× DayBriefCard; delete/retire detail screen
│       ├── formatters.py     # REUSE/EXTEND — HH:MM, meters, wide-window label
│       ├── theme.py          # DROP legend/peaks section constants from home
│       └── components/
│           ├── day_brief_card.py   # NEW
│           ├── frame.py            # REUSE chrome
│           ├── badge.py            # REUSE condition pill
│           ├── status_bar.py       # UPDATE shortcuts (no Enter→detail, no ←→ peak)
│           └── …                   # peak_card / evolution / View-B widgets unused on home
scripts/
├── check_report_presentation.py    # UPDATE — 1.2.0 + DayBrief invariants
└── check_tui_visual_smoke.py       # UPDATE — two cards; forbid PICOS/LEYENDA/detail
```

**Structure Decision**: Single package `surf_forecast`. Product change is presentation + narrative + TUI home; evaluation engine stays put. Prefer new `DayBriefCard` over forcing `PeakCard` into a day role.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **VI. Inform, don't decide** — advisory “conviene ir a X a la hora Y” on home | Personal-use product goal is exactly when/where guidance (spec clarifications + FR-010); still forbids guarantees of waves/safety | Strict “facts only, never recommend beaches/times” keeps the 003 five-peak board that the user rejected as useless |
| **Supersede 003 “show poor peaks on board”** | Worth filter (fair+, max 3) is the core UX | Showing all five peaks implies equal relevance and hides the one beach worth going |
| **Schema 1.2.0 breaking change** | Shared contract must drop days 3–5 and ship DayBrief fields for TUI/CLI/JSON parity | TUI-only rewrite would leave CLI/JSON on the old technical narrative (clarify Q1 rejected) |
