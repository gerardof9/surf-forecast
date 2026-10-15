# Tasks: TUI visual craft (graphic layer)

**Input**: Design documents from `/specs/004-tui-visual-craft/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, graphic-layer.md (binding), quickstart.md

**Tests**: Spec FR-G15 / SC-005 require Textual `run_test` smoke (`scripts/check_tui_visual_smoke.py`) plus keep `scripts/check_report_presentation.py` green. Manual VS-* screenshots in Polish. No pixel-diff CI. Do **not** change engine thresholds or presentation 1.1.0 semantics.

**Organization**: Tasks grouped by user story (US1â€“US3). Formatters + Frame/theme are foundational and block all stories.

**Constitution notes**: Graphic layer only under `presentation/tui/`. No LLM. No Nerd Fonts. Never name content helpers `_render` on Textual widgets (FR-G10).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1â€¦US3 for story phases only
- Include exact file paths in descriptions

## Path Conventions

- Package TUI: `src/surf_forecast/presentation/tui/`
- Feature docs: `specs/004-tui-visual-craft/`
- Smoke: `scripts/check_tui_visual_smoke.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create module skeleton and smoke harness stub without changing visible TUI behavior yet

- [x] T001 Create package dirs and empty modules `src/surf_forecast/presentation/tui/formatters.py`, `src/surf_forecast/presentation/tui/theme.py`, and `src/surf_forecast/presentation/tui/components/__init__.py` per `plan.md`
- [x] T002 [P] Add smoke runner stub `scripts/check_tui_visual_smoke.py` that exits 0 with â€œsmoke not implementedâ€ placeholder and documents the FR-G15 command from `quickstart.md`
- [x] T003 [P] Add brief pointer in `specs/004-tui-visual-craft/quickstart.md` confirming smoke stub command path once T002 exists (if not already accurate)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Display hygiene + Frame/theme/StatusBar primitives used by every story. **No View A/B redesign until this phase completes.**

**âš ï¸ CRITICAL**: Do not modify `src/surf_forecast/domain/evaluation.py` thresholds or presentation 1.1.0 field semantics

- [x] T004 Implement pure display formatters (meters 1-decimal comma, period/`n/d`, wind, score num, Unicode stars `â˜…â—â˜†`, local `HH:MM`, Spanish confidence, best-window wide-label rules) in `src/surf_forecast/presentation/tui/formatters.py` per `contracts/display-hygiene.md`
- [x] T005 [P] Define theme token roles (canvas/body/muted/accent/borders/cond-*) in `src/surf_forecast/presentation/tui/theme.py` aligned with `graphic-layer.md` Â§4
- [x] T006 Implement custom Unicode title-in-border `Frame` widget (focus chrome; no CSS-only substitute; do not override content via `_render`) in `src/surf_forecast/presentation/tui/components/frame.py` per FR-G11 / research R1
- [x] T007 [P] Implement `Badge`/`StatusPill` in `src/surf_forecast/presentation/tui/components/badge.py` with FR-017 role colors and text-always-present
- [x] T008 Implement dedicated non-Frame `StatusBar` with grouped shortcuts in `src/surf_forecast/presentation/tui/components/status_bar.py` per FR-G07
- [x] T009 Wire theme CSS variables/roles into `src/surf_forecast/presentation/tui/app.py` (replace ad-hoc cyan-only chrome where tokens apply) without changing query workers
- [x] T010 Export public components from `src/surf_forecast/presentation/tui/components/__init__.py`
- [x] T011 Expand `scripts/check_tui_visual_smoke.py` to assert formatters unit checks for float hygiene / no fake `0 s` / Unicode stars / wide-window label (import formatters directly; no full app yet OK)

**Checkpoint**: Formatters + Frame + StatusBar + theme ready â€” user story UI work can begin

---

## Phase 3: User Story 1 â€” View A surf report board (Priority: P1)

**Goal**: Framed analysis + RatingHero + up to five structured PeakCards; day-list focus; `â†â†’` peak selection

**Independent Test**: Wide terminal + `fixtures/normal` â†’ dual timestamps/pill, analysis+hero frames, multi-column peak cards with badges/metrics/Unicode stars; focus on days; `â†â†’` moves card chrome; Enter opens detail (detail layout may still be interim until US2)

### Implementation

- [x] T012 [US1] Implement `PeakCard` structured layout (badge, size, period, wind, stars, best-of-day marker, selected chrome) in `src/surf_forecast/presentation/tui/components/peak_card.py` using formatters
- [x] T013 [P] [US1] Implement `RatingHero` in `src/surf_forecast/presentation/tui/components/rating_hero.py` (Unicode stars matching numeric; single Sin valoraciÃ³n path)
- [x] T014 [P] [US1] Implement `AnalysisPanel` sentence-kind styling (`â‰ˆ`/`â—‡`/`!`, facts before limitations) in `src/surf_forecast/presentation/tui/components/analysis_panel.py`
- [x] T015 [US1] Implement day-level Banner (window-completed once) and HeaderBar dual timestamps + StatusPill composition helpers in `src/surf_forecast/presentation/tui/components/` (e.g. `header_bar.py` or screens-local compose using Frame/Badge)
- [x] T016 [US1] Rewrite View A compose/populate in `src/surf_forecast/presentation/tui/screens.py` (`DailyReportScreen`) to use Frame + AnalysisPanel + RatingHero + PeakCard grid; remove multiline Static â€œcardâ€ dumps
- [x] T017 [US1] Enforce PeakGrid breakpoints in `src/surf_forecast/presentation/tui/screens.py` and/or `app.py` CSS: â‰¥130 up to 5 cols, 90â€“129 2â€“3 cols, &lt;90 1 col (FR-G03 â€” no hard max-2 on wide)
- [x] T018 [US1] Keep primary focus on day `ListView`; `â†â†’` updates `peak_index` + PeakCard selected chrome only; `Enter` opens View B (FR-G12) in `src/surf_forecast/presentation/tui/screens.py`
- [x] T019 [US1] Add/adjust LegendRail content using minimal iconography (`â—` + FR-017) via Frame in `src/surf_forecast/presentation/tui/screens.py`; hide on medium/narrow per breakpoints
- [x] T020 [US1] Replace StatusBar usage on View A with new `StatusBar` component in `src/surf_forecast/presentation/tui/screens.py`
- [x] T021 [US1] Extend `scripts/check_tui_visual_smoke.py` to mount View A with fixture, assert no raw multi-decimal floats / no ASCII `***` star bars in rendered text, and `â†â†’` + Enter does not raise

**Checkpoint**: US1 independently demoable as report board (View B may still be ugly)

---

## Phase 4: User Story 2 â€” View B three-zone detail board (Priority: P1)

**Goal**: Summary | evolution/window/analysis | secondary tech; hygiene times/meters; wide-window honesty

**Independent Test**: Enter from US1 â†’ summary+evolution+window hierarchy; `HH:MM`; rounded meters; tech collapsed; wide window label if applicable; Esc restores day+peak

### Implementation

- [x] T022 [P] [US2] Implement `EvolutionTable` (HH:MM rows, columns, condition `â—`) in `src/surf_forecast/presentation/tui/components/evolution_table.py`
- [x] T023 [P] [US2] Implement `BestWindowCallout` with local `HH:MMâ€“HH:MM` and FR-G14 wide-window label in `src/surf_forecast/presentation/tui/components/best_window.py`
- [x] T024 [US2] Implement `TechnicalDetails` collapsed-by-default (`D` toggle; safe labels; no `_render` name clash) in `src/surf_forecast/presentation/tui/components/technical_details.py`
- [x] T025 [US2] Rewrite View B compose/populate in `src/surf_forecast/presentation/tui/screens.py` (`PeakDetailScreen`) as three-zone board using Frame + summary Badge/metrics + EvolutionTable + BestWindowCallout + AnalysisPanel + TechnicalDetails (not homogeneous VerticalScroll dump)
- [x] T026 [US2] Apply formatters to all View B primary fields (size/period/wind/stars/confidence ES) in `src/surf_forecast/presentation/tui/screens.py`
- [x] T027 [US2] Wire `D` / Esc / `â†â†’` peak switch to `_populate` (not `_render`) and StatusBar context on View B in `src/surf_forecast/presentation/tui/screens.py` and `src/surf_forecast/presentation/tui/app.py` if needed
- [x] T028 [US2] Extend `scripts/check_tui_visual_smoke.py` for Enterâ†’View Bâ†’Esc, assert `HH:MM` preference over ISO-first in best-window primary text when window present, and no raw multi-decimal floats

**Checkpoint**: US1+US2 deliver the modelo hierarchy loop

---

## Phase 5: User Story 3 â€” Professional chrome & hygiene polish (Priority: P2)

**Goal**: Consistent Frame chrome everywhere primary; StatusBar distinct; condition color reinforces labels; Help parity

**Independent Test**: VS-A1/VS-B1 screenshots show title-in-border Frames; StatusBar not framed; badges readable without color

### Implementation

- [x] T029 [US3] Audit View A/B/Help so primary content regions use `Frame` (reject floating titles over bare canvas) in `src/surf_forecast/presentation/tui/screens.py`
- [x] T030 [P] [US3] Ensure NO_COLOR / muted fallback still shows full Spanish FR-017 text on badges in `src/surf_forecast/presentation/tui/components/badge.py`
- [x] T031 [US3] Update `HelpScreen` in `src/surf_forecast/presentation/tui/screens.py` to carry legend/how-to when rails hidden; `markup=False` on Static bodies
- [x] T032 [US3] Trim/re-export legacy helpers from `src/surf_forecast/presentation/tui/widgets.py` to avoid duplicate format paths (delegate to formatters/components)
- [x] T033 [US3] Final pass on `src/surf_forecast/presentation/tui/app.py` CSS: remove obsolete peak-card CSS that fights Frame/PeakCard; keep responsive classes

**Checkpoint**: Chrome consistent with graphic-layer anti-patterns list

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Validation gates, docs, exe

- [x] T034 Run `scripts/check_report_presentation.py` and fix any incidental breakages without changing rating math semantics
- [x] T035 Finalize `scripts/check_tui_visual_smoke.py` to exit non-zero on FR-G15 failures; document in `specs/004-tui-visual-craft/quickstart.md`
- [x] T036 [P] Capture/manual checklist VS-A1, VS-A2, VS-B1, VS-B2, VS-N1 per `quickstart.md` / `graphic-layer.md` Â§12 (store under `specs/004-tui-visual-craft/references/` if desired)
- [x] T037 [P] Rebuild exe with `scripts/build-exe.ps1` and smoke-launch View A/B once on Windows
- [x] T038 Update `specs/004-tui-visual-craft/README.md` status notes if any contract paths changed during implement

---

## Dependencies & Story Order

```text
Phase 1 Setup â†’ Phase 2 Foundational
        â”œâ†’ US1 (View A board)     â† MVP
        â”œâ†’ US2 (View B board)     â† after US1 Enter path exists
        â””â†’ US3 (chrome polish)    â† after US1/US2 structure
                â†’ Polish
```

- US2 depends on US1 for navigation entry (Enter from cards)
- US3 can overlap late US2 polish but should not precede Frame/PeakCard existence
- Foundational blocks all stories

## Parallel Opportunities

**Within Foundational** (after T004 started): T005 âˆ¥ T007; T006 before T009  
**Within US1**: T013 âˆ¥ T014 after PeakCard contract clear; T012 then T016  
**Within US2**: T022 âˆ¥ T023 âˆ¥ T024 then T025  
**Polish**: T036 âˆ¥ T037

## Implementation Strategy

### MVP

1. Phase 1 + 2  
2. US1 only â†’ stop and validate report board vs `references/modelo.png` hierarchy  
3. Then US2 â†’ US3 â†’ Polish  

### Suggested MVP scope

**US1** (View A Frames + PeakCard grid + focus model + smoke hygiene on View A)

---

## Notes

- [P] = different files / safe parallel  
- Never reimplement classification inside components  
- `graphic-layer.md` wins on pixels/layout; frozen presentation wins on meteorology/honesty  
- Commit after each task or logical group  
- Stop at checkpoints to validate independently  
