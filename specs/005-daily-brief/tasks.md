# Tasks: Daily brief (Hoy / Mañana)

**Input**: Design documents from `/specs/005-daily-brief/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Spec/plan require updating `scripts/check_report_presentation.py` (schema 1.2.0 + DayBrief invariants) and `scripts/check_tui_visual_smoke.py` (two cards; no PICOS/LEYENDA/View B). Manual prose reads per `quickstart.md`. No complex CI. Do **not** change evaluation grade/`best_window` formulas in `domain/evaluation.py` / `domain/windows.py`.

**Organization**: Tasks grouped by user story (US1–US4). Shared DayBrief assembly (schema slice, worth filter, narrative `template_v2`) is foundational and blocks all stories.

**Constitution notes**: Principle VI (constitution 1.1.0) allows personal advisory when/where briefs. Keep honesty (no invented spots; derived height; no wave/safety guarantees). Personal / zero-cost / on-demand only.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1…US4 for story phases only
- Include exact file paths in descriptions

## Path Conventions

- Domain/presentation: `src/surf_forecast/domain/`, `src/surf_forecast/presentation/`
- TUI: `src/surf_forecast/presentation/tui/`
- Feature docs: `specs/005-daily-brief/`
- Checks: `scripts/check_report_presentation.py`, `scripts/check_tui_visual_smoke.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align agent context and stub check expectations without shipping product behavior yet

- [ ] T001 Confirm active feature pin is `specs/005-daily-brief` in `.specify/feature.json` and `.cursor/rules/specify-rules.mdc` points at `specs/005-daily-brief/plan.md`
- [ ] T002 [P] Verify `specs/005-daily-brief/contracts/presentation-1.2.0.md` is linked from `specs/005-daily-brief/quickstart.md` — **do not** add early/placeholder asserts in `scripts/check_report_presentation.py` (all 1.2.0 enforcement is T010 only)
- [ ] T003 [P] Document DayBrief smoke expectations in `specs/005-daily-brief/quickstart.md` (commands already present — verify paths match repo entrypoints)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared presentation 1.2.0 DayBrief builder — slice Hoy/Mañana, worth filter, height/go-window from best spot, plain narrative. **Blocks all user stories.**

**⚠️ CRITICAL**: Do not modify grade/`best_window` selection formulas; only presentation assembly + narrative templates

- [ ] T004 Implement worth-spot ranking helper (fair+ only, max 3, stable tie-break) used by presentation in `src/surf_forecast/domain/presentation.py` (or small helper module next to it) per `data-model.md`
- [ ] T005 Implement GoWindow + HeightSummary mapping from a peak’s `best_window` / size (wide-window honesty; `HH:MM`; null when no best) in `src/surf_forecast/domain/presentation.py` and reuse display hygiene from `src/surf_forecast/presentation/tui/formatters.py` where appropriate (pure functions preferred; depends on T004 ranking)
- [ ] T006 Rewrite day narrative to `template_v2` plain Spanish `headline` + `body` (+ optional `caution`) in `src/surf_forecast/domain/narrative.py` — no `≈`/`◇`/`!` lead voice; advisory when/where allowed with estimate disclaimer
- [ ] T007 Assemble nested `brief` object (DayBrief fields) from day + worth spots + narrative in `src/surf_forecast/domain/presentation.py`
- [ ] T008 Slice presentation `days` to Hoy/Mañana only and set `schema_version` to `1.2.0` in `src/surf_forecast/domain/presentation.py` per `contracts/presentation-1.2.0.md` (engine may still compute longer horizon)
- [ ] T009 Remove/replace home-facing dependency on old `day_analysis` kind bags for presented days in `src/surf_forecast/domain/presentation.py` (brief replaces it on the wire)
- [ ] T010 Update `scripts/check_report_presentation.py` to enforce 1.2.0 invariants (2 days, brief required, worth ≤3 fair+, empty ⇒ null height/window, **no** `tiempo`/`energia`/`Tiempo`/`Energía` keys on days/brief)
- [ ] T011 [P] Adapt `src/surf_forecast/presentation/json_output.py` if it hard-codes old schema metadata so JSON emits the shared 1.2.0 payload
- [ ] T012 [P] Adapt `src/surf_forecast/presentation/cli.py` to print DayBrief fields for the two presented days (headline, body, height, go_window, worth names)
- [ ] T036 Handle incomplete/missing Mañana (or single-day engine horizon): second presented day MUST show explicit limited/missing brief state and MUST NOT clone Hoy silently — implement in `src/surf_forecast/domain/presentation.py` + assert in `scripts/check_report_presentation.py`

**Checkpoint**: Fixture → presentation payload is 1.2.0 with two briefs; CLI/JSON show plain brief — TUI may still be old until US1

---

## Phase 3: User Story 1 — Open and know when/where today and tomorrow (Priority: P1) 🎯 MVP

**Goal**: TUI home shows exactly two DayBrief cards (Hoy/Mañana) with condition, height, headline, body, go-window, worth spots — no 5-day rail, no PICOS grid, no LEYENDA

**Independent Test**: Load normal fixture in TUI → two cards; can answer worth / time / beaches from Hoy alone; chrome titles PICOS DEL DÍA and LEYENDA absent

### Implementation

- [ ] T013 [US1] Create `DayBriefCard` widget binding `brief` fields in `src/surf_forecast/presentation/tui/components/day_brief_card.py` (reuse Frame/Badge/formatters)
- [ ] T014 [P] [US1] Export `DayBriefCard` from `src/surf_forecast/presentation/tui/components/__init__.py`
- [ ] T015 [US1] Rewrite `DailyReportScreen` compose/populate in `src/surf_forecast/presentation/tui/screens.py` to header + two `DayBriefCard`s + StatusBar; remove day ListView rail, PICOS grid, and LEYENDA
- [ ] T016 [US1] Update CSS / layout breakpoints for two-card row vs stack in `src/surf_forecast/presentation/tui/app.py` (drop peak-grid `cols-5` home rules)
- [ ] T017 [US1] Remove home legend/peaks section constants usage from `src/surf_forecast/presentation/tui/theme.py` (or stop importing `LEGEND_LINES` / `SECTION_PEAKS` on home)
- [ ] T018 [US1] Update StatusBar / Help copy for two-card home (no compare-five-peaks / no legend) in `src/surf_forecast/presentation/tui/components/status_bar.py` and Help screen in `src/surf_forecast/presentation/tui/screens.py`
- [ ] T019 [US1] Extend `scripts/check_tui_visual_smoke.py` to assert two day cards render and strings `PICOS DEL DÍA` / `LEYENDA` are absent
- [ ] T037 [US1] Assert dual honesty timestamps remain visible on home (query/consultation time and meteorological data-update time) in `scripts/check_tui_visual_smoke.py` and/or home populate in `src/surf_forecast/presentation/tui/screens.py` per FR-014

**Checkpoint**: MVP demoable — two-card home from shared brief

---

## Phase 4: User Story 2 — Only beaches that are worth the trip (Priority: P1)

**Goal**: Worth spots list shows only fair+ (max 3); empty-state message when none; chips not full PeakCards

**Independent Test**: Fixture with one fair+ peak → one chip; all-poor → empty message and no invented names; never five equal peak cards

### Implementation

- [ ] T020 [US2] Render worth-spot chips / short list (name + optional reason) inside `src/surf_forecast/presentation/tui/components/day_brief_card.py` from `brief.worth_spots`
- [ ] T021 [US2] Render `empty_spots_message` when `worth_spots` is empty in `src/surf_forecast/presentation/tui/components/day_brief_card.py`
- [ ] T022 [US2] Add/extend asserts in `scripts/check_report_presentation.py` for single-worth and zero-worth fixtures (or synthetic payload cases) covering FR-007–FR-009
- [ ] T023 [P] [US2] Ensure CLI empty/worth listing matches brief in `src/surf_forecast/presentation/cli.py`

**Checkpoint**: US2 filter behavior visible on cards and in checks

---

## Phase 5: User Story 3 — Plain “when to go” without fake precision (Priority: P2)

**Goal**: Day timing line uses best worth-spot window as `HH:MM–HH:MM`; wide windows labeled honestly; no minute-count lead

**Independent Test**: Tight window vs wide window fixtures — wording differs; primary text uses local clock times

### Implementation

- [ ] T024 [US3] Surface `brief.go_window.display` prominently on `DayBriefCard` in `src/surf_forecast/presentation/tui/components/day_brief_card.py`
- [ ] T025 [US3] Harden wide-window display helper (reuse/extend `format_best_window` or presentation mapper) in `src/surf_forecast/presentation/tui/formatters.py` and/or `src/surf_forecast/domain/presentation.py` per FR-G14 / FR-006
- [ ] T026 [US3] When no worth spots, omit fake times and show honest empty timing aligned with `go_window is null` in `src/surf_forecast/presentation/tui/components/day_brief_card.py`
- [ ] T027 [P] [US3] Assert go_window display rules (no leading large minute counts; `HH:MM` present when window exists) in `scripts/check_report_presentation.py` and/or `scripts/check_tui_visual_smoke.py`

**Checkpoint**: Timing copy meets SC-005

---

## Phase 6: User Story 4 — Home is the only interactive surface (Priority: P3)

**Goal**: Remove peak-detail View B from interactive product; no Enter→detail path

**Independent Test**: After load, Enter/arrows/listed shortcuts never open PeakDetailScreen; Help does not advertise detail

### Implementation

- [ ] T028 [US4] Remove `PeakDetailScreen` routing and Enter→detail bindings from `src/surf_forecast/presentation/tui/app.py` and `src/surf_forecast/presentation/tui/screens.py`
- [ ] T029 [US4] Strip peak-index `←→` navigation and detail-related StatusBar shortcuts from home in `src/surf_forecast/presentation/tui/screens.py` and `src/surf_forecast/presentation/tui/components/status_bar.py`
- [ ] T030 [US4] Update Help screen text to remove View B / peak-detail instructions in `src/surf_forecast/presentation/tui/screens.py`
- [ ] T031 [US4] Extend `scripts/check_tui_visual_smoke.py` to assert Enter on home does not push peak detail (and optionally that `PeakDetailScreen` is not registered)

**Checkpoint**: Interactive app is two-card-only

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Parity, cleanup, manual validation

- [ ] T032 [P] Grep/remove dead home imports of PeakCard grid / legend from `src/surf_forecast/presentation/tui/screens.py` and `src/surf_forecast/presentation/tui/widgets.py`
- [ ] T033 [P] Decide keep-or-delete unused View-B-only components (`evolution_table.py`, detail `best_window.py` callout usage, `technical_details.py`) — if kept, ensure unused on home; document choice in a short note under `specs/005-daily-brief/plan.md` or commit message
- [ ] T034 Run full `specs/005-daily-brief/quickstart.md` validation (presentation check + TUI smoke + manual SC-001/SC-004 read on ≥1 normal and ≥1 empty-worth case)
- [ ] T035 [P] Spot-check JSON vs TUI vs CLI field parity for headline/body/go_window/worth names on one fixture

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: Depends on Foundational — MVP
- **US2 (Phase 4)**: Depends on Foundational; best after US1 card shell exists (T013) for chip UI
- **US3 (Phase 5)**: Depends on Foundational go_window fields; best after US1 card shell
- **US4 (Phase 6)**: Can start after US1 home rewrite (avoid fighting Enter→detail while rebuilding compose); ideally after US1
- **Polish (Phase 7)**: After desired stories complete

### User Story Dependencies

- **US1 (P1)**: After Phase 2 — no story deps — **MVP**
- **US2 (P1)**: After Phase 2; UI chips need US1 `DayBriefCard`
- **US3 (P2)**: After Phase 2; display on card needs US1
- **US4 (P3)**: After US1 home exists (remove detail cleanly)

### Parallel Opportunities

- T002/T003 in Setup
- T004 → T005 → T006 → T007 → T008 sequence for presentation (T005 is **not** parallel)
- T011/T012 after T008 in parallel; T036 with T010 after T008
- T014 parallel once T013 file exists; T037 after T015/T019
- T023 / T027 / T032 / T033 / T035 marked [P] where noted

---

## Parallel Example: After Foundational

```text
# Once T008–T010 green:
T011 Adapt json_output.py
T012 Adapt cli.py

# Once T013 DayBriefCard exists:
T014 Export DayBriefCard
# then T015 screens rewrite (sequential on screens.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 Setup  
2. Phase 2 Foundational (1.2.0 DayBrief)  
3. Phase 3 US1 (two-card TUI)  
4. **STOP** — validate quickstart home read (SC-001)  
5. Then US2 → US3 → US4 → Polish  

### Incremental Delivery

1. Foundational → CLI/JSON already useful  
2. US1 → TUI MVP  
3. US2 → worth chips/empty states  
4. US3 → timing polish  
5. US4 → delete View B  
6. Polish → parity + cleanup  

---

## Notes

- [P] = different files, no incomplete-task dependency
- Do not reopen evaluation formulas
- Advisory prose is allowed; guarantees are not
- Commit after each task or logical group
- Suggested MVP = Phase 1–3 (T001–T019 + T036–T037 as applicable)
- Analyze remediation 2026-10-15: C1 constitution 1.1.0; I1 Input; A1 T002; I3 T005; U1 T036; U2 T037; G1 T010; I2 GoWindow naming
