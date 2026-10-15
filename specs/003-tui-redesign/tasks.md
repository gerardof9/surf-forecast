# Tasks: Surfer-friendly TUI redesign

**Input**: Design documents from `/specs/003-tui-redesign/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Spec FR-027 / plan request **focused pure-Python checks** for rating, narrative omission, sampling, and FR-017 labels (constitution XI). Manual TUI checklist in `quickstart.md`. No CI suite required. Do **not** change `evaluation.py` thresholds for UI reasons.

**Organization**: Tasks grouped by user story (US1–US5). Presentation helpers are foundational and block all stories.

**Constitution notes**: Engine / interpretation / TUI stay separated. No LLM or external generative service. No favorites/alerts/preferences. Neutral title `PICOS DEL DÍA`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1…US5 for story phases only
- Include exact file paths in descriptions

## Path Conventions

- Package root: `src/surf_forecast/`
- Feature docs: `specs/003-tui-redesign/`
- Focused checks: `scripts/check_report_presentation.py` (stdlib runner; no pytest mandate)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add feature contract artifact and check harness skeleton without changing runtime behavior yet

- [x] T001 Create additive presentation schema draft in `specs/003-tui-redesign/contracts/schemas/forecast-output-1.1.0.schema.json` documenting 1.1.0 fields from `contracts/presentation.md` (do not rewrite `001` schema in place)
- [x] T002 [P] Create focused check runner stub `scripts/check_report_presentation.py` that exits 0 with “no checks yet” placeholder and documents how to run it from repo root
- [x] T003 [P] Add brief pointer in `specs/003-tui-redesign/quickstart.md` to the check runner command once stub exists

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared presentation 1.1.0 fields and domain helpers used by every story. **No user story TUI work until this phase completes.**

**⚠️ CRITICAL**: Do not modify surfability thresholds, `k`, or quality rules in `src/surf_forecast/domain/evaluation.py`

- [x] T004 Replace user-facing label tables with FR-017 map and keep English machine ids in `src/surf_forecast/domain/presentation.py`
- [x] T005 [P] Implement confirmed ordinal grade→score map only (no multi-factor formula) and best-resolved day/peak rating helpers in `src/surf_forecast/domain/day_rating.py` (`best_resolved_grade_map_v1`, whole points, captions from `data-model.md`)
- [x] T006 [P] Implement template day/peak narrative builders emitting `sentences[]` with `kind` ∈ {fact, interpretation, limitation} (facts only; no LLM) in `src/surf_forecast/domain/narrative.py`
- [x] T007 [P] Implement evolution band sampler (`06:00–10:59` / `11:00–14:59` / `15:00–20:00` UYT) including wind speed/direction pass-through when available in `src/surf_forecast/domain/evolution_samples.py`
- [x] T008 Wire helpers into `build_presentation` in `src/surf_forecast/domain/presentation.py`: `schema_version` `1.1.0`, report fields, dual timestamps; pass through `wind_speed_kmh` / direction for cards and samples from engine slot inputs (extend `WindAssessment` or slot dict with display-only speed/direction—**do not** change evaluation thresholds); ensure snapshots continue to persist the presentation payload
- [x] T009 [P] Add pure-Python checks for FR-017 labels, ordinal grade→score, best-peak day rating, narrative omission, sampling bands, **provisional-profile day**, and **analysis-window-completed today** in `scripts/check_report_presentation.py`
- [x] T010 Update CLI human summary to print day analysis, day rating, and peak ratings from payload in `src/surf_forecast/presentation/cli.py` (no TUI redesign yet)

**Checkpoint**: A normal/`fixture` forecast payload includes 1.1.0 report fields; `scripts/check_report_presentation.py` passes; engine thresholds untouched

---

## Phase 3: User Story 1 — Daily surf report at a glance (P1) 🎯 MVP

**Goal**: View A shows header, `ANÁLISIS DEL DÍA`, valoración 1–5 (or `Sin valoración`), and ranked `PICOS DEL DÍA` cards.

**Independent Test**: With a complete sample payload, open TUI and verify View A answers questions 1–2 for the selected day without opening detail/technicals (`quickstart.md` View A checklist).

### Tests for User Story 1

- [x] T011 [P] [US1] Extend `scripts/check_report_presentation.py` with fixtures covering good day, mixed peaks, insufficient-for-rating (`Sin valoración`), provisional profile, and analysis-window-completed today

### Implementation for User Story 1

- [x] T012 [P] [US1] Add star/numeric rating widget helpers in `src/surf_forecast/presentation/tui/widgets.py` (glyph must match whole-point score; numeric always visible)
- [x] T013 [P] [US1] Add peak card / day-list / condition-legend widgets in `src/surf_forecast/presentation/tui/widgets.py` (section title exactly `PICOS DEL DÍA`; wind shows intensity/class and km/h when pass-through present)
- [x] T014 [US1] Implement `DailyReportScreen` (View A) composition per `contracts/tui.md` / `mock2.png` hierarchy in `src/surf_forecast/presentation/tui/screens.py` (replace three-pane comparator layout)
- [x] T015 [US1] Render `day_analysis.sentences` with distinct styling/prefixes for `fact` vs `interpretation` vs `limitation` (FR-006) in `src/surf_forecast/presentation/tui/screens.py` / `widgets.py`
- [x] T016 [US1] Render dual timestamps and data-state chip from payload in View A header via `src/surf_forecast/presentation/tui/screens.py` and header helpers in `widgets.py`
- [x] T017 [US1] Bind View A day list as initial focus; ↑/↓ change day and refresh analysis/rating/cards in `src/surf_forecast/presentation/tui/screens.py`
- [x] T018 [US1] Point app mount to `DailyReportScreen` and keep refresh worker flow in `src/surf_forecast/presentation/tui/app.py`

**Checkpoint**: View A usable as daily report MVP; cards use `PICOS DEL DÍA`; no “recomendados”

---

## Phase 4: User Story 2 — Navigate days and open peak detail (P1)

**Goal**: Keyboard navigation across days/spots; Enter opens View B; Esc returns; help/refresh/stored-only available.

**Independent Test**: From View A, change days, move among cards, open a peak, Esc back to same day; `R` / `o` / `?` / `Q` work per contract.

### Implementation for User Story 2

- [x] T019 [US2] Implement ←/→ spot focus and Enter → push peak detail screen in `src/surf_forecast/presentation/tui/screens.py`
- [x] T020 [US2] Add `PeakDetailScreen` shell (header + placeholder body) and Esc pop preserving day/peak indices in `src/surf_forecast/presentation/tui/screens.py`
- [x] T021 [US2] Update app-level bindings: keep `R`, `o`, `?`, `Q`; **remove** `p`/ProfileScreen wiring in `src/surf_forecast/presentation/tui/app.py`
- [x] T022 [US2] Update Help/About copy with new keys, profile JSON path (no interactive profiles), and honesty notes in `src/surf_forecast/presentation/tui/screens.py`

**Checkpoint**: Navigation loop A↔B works; profiles screen gone

---

## Phase 5: User Story 3 — Peak detail, sampled evolution, best window (P1)

**Goal**: View B shows conditions, sampled evolution, engine best window (or absence), peak rating, and peak analysis when facts suffice.

**Independent Test**: Open a peak with slots/window and one without; verify samples, window rules, and analysis omission (`quickstart.md` View B).

### Tests for User Story 3

- [x] T023 [P] [US3] Add checks in `scripts/check_report_presentation.py` for evolution sample bands (incl. wind pass-through when present) and peak-analysis omit-when-thin behavior

### Implementation for User Story 3

- [x] T024 [US3] Render peak summary (display_name, FR-017 condition, size, swell/wind with km/h when available, confidence, peak_rating) in `PeakDetailScreen` inside `src/surf_forecast/presentation/tui/screens.py`
- [x] T025 [US3] Render `evolution_samples` table/rows and `MEJOR VENTANA ESTIMADA` only from engine `best_window` (never invent) in `src/surf_forecast/presentation/tui/screens.py`
- [x] T026 [US3] Render peak analysis text when present (else omit/limitation) in `src/surf_forecast/presentation/tui/screens.py`
- [x] T027 [US3] Support ←/→ to change peak within the selected day while on View B in `src/surf_forecast/presentation/tui/screens.py`

**Checkpoint**: Question 3 (timing) answerable from View B without technical pane

---

## Phase 6: User Story 4 — Secondary technical details (P2)

**Goal**: Collapsible `DETALLES TÉCNICOS` inside View B; no third diagnostic screen.

**Independent Test**: View B opens with technicals collapsed; `D` expands showing Hs vs derived, ages, snapshot, shared-cell warning.

### Implementation for User Story 4

- [x] T028 [US4] Add collapsible technical details widget (collapsed by default) in `src/surf_forecast/presentation/tui/widgets.py`
- [x] T029 [US4] Wire `D` toggle and populate technical fields from payload/sources/criteria/snapshot in `src/surf_forecast/presentation/tui/screens.py`
- [x] T030 [US4] Ensure footer hints document `D` / Esc and technical content does not dominate default View B layout in `src/surf_forecast/presentation/tui/screens.py` / `widgets.py`

**Checkpoint**: Traceability available without a separate diagnostics screen

---

## Phase 7: User Story 5 — Consistent Spanish vocabulary and honest states (P2)

**Goal**: FR-017 everywhere; incomplete ≠ “Pocas olas”; color never sole signal; `good`/`very_good` both “Buena oportunidad”.

**Independent Test**: Review labels for normal, uncertain, incomplete, window-completed cases against FR-017.

### Tests for User Story 5

- [x] T031 [P] [US5] Add label-map assertions for all FR-017 ids and “incomplete not mapped to few waves” in `scripts/check_report_presentation.py`

### Implementation for User Story 5

- [x] T032 [US5] Ensure cards/detail/legend never show raw enums (`fair`, `resolved`) as primary labels in `src/surf_forecast/presentation/tui/screens.py` and `widgets.py`
- [x] T033 [US5] Ensure incomplete/unevaluable peaks cannot appear as recommended/`Pocas olas` and best_of_day only on resolved rating source in `src/surf_forecast/domain/presentation.py` + TUI card rendering
- [x] T034 [US5] Align Help legend text with FR-017 and score honesty (not a probability) in `src/surf_forecast/presentation/tui/screens.py`

**Checkpoint**: Vocabulary and honesty rules hold across A/B/Help

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Responsive layout, regression, manual validation

- [x] T035 [P] Implement narrow vs wide stacking/scroll behavior for View A/B without silent truncation of analysis in `src/surf_forecast/presentation/tui/screens.py` and CSS in `src/surf_forecast/presentation/tui/app.py`
- [x] T036 [P] Remove dead `ProfileScreen` code paths and unused imports from `src/surf_forecast/presentation/tui/screens.py` / `app.py` if any remain
- [x] T037 Run `scripts/check_report_presentation.py` and existing engine fixture/manual replay from `specs/001-la-paloma-surf-forecast/quickstart.md`; fix regressions without changing thresholds
- [x] T038 Execute `specs/003-tui-redesign/quickstart.md` manual TUI checklist (good / mixed / incomplete / provisional / window-completed / dual time / narrow width / fact-vs-interpretation / wind km/h when present) and record gaps if any
- [x] T039 [P] Sync any final binding/copy tweaks into `specs/003-tui-redesign/contracts/tui.md` only if implementation required a documented adaptation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — MVP
- **US2 (Phase 4)**: After US1 screen exists (needs View A to navigate from)
- **US3 (Phase 5)**: After US2 shell `PeakDetailScreen`
- **US4 (Phase 6)**: After US3 body (technicals attach to detail)
- **US5 (Phase 7)**: Can overlap late US1–US4 polish; foundational labels already done in T004
- **Polish (Phase 8)**: After desired stories complete

### User Story Dependencies

- **US1**: After Phase 2 only
- **US2**: After US1 View A
- **US3**: After US2 PeakDetailScreen shell
- **US4**: After US3 detail content
- **US5**: Mostly verification/copy; depends on T004 + card/detail renderers

### Parallel Opportunities

- T005, T006, T007 in parallel after T004 (or with T004 if careful on imports)
- T012 / T013 in parallel before T014
- T023 checks parallel with T024–T026 implementation once helpers exist
- T035 / T036 / T039 polish items in parallel

### Parallel Example: Foundational helpers

```text
Task: "Implement day_rating.py"
Task: "Implement narrative.py"
Task: "Implement evolution_samples.py"
```

### Parallel Example: User Story 1 widgets

```text
Task: "Star/numeric widgets in widgets.py"
Task: "Peak card / day-list / legend widgets in widgets.py"
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup
2. Phase 2 Foundational (critical)
3. Phase 3 US1 View A
4. **STOP**: validate daily report independently
5. Then US2→US3→US4→US5→Polish

### Incremental Delivery

1. Setup + Foundational → payload 1.1.0 ready (CLI visible)
2. US1 → daily report MVP
3. US2 → navigation
4. US3 → timing/detail
5. US4 → technicals
6. US5 → vocabulary polish
7. Polish → quickstart + engine regression

### Suggested MVP scope

**US1 only** (View A daily report + foundational presentation fields).

---

## Notes

- [P] = different files / safe parallel
- Never reimplement classification inside Textual widgets
- Never add LLM/external narrative services
- Commit after each task or logical group
- Stop at checkpoints to validate independently
