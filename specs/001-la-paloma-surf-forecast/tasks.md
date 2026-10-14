---
description: "Task list for the first delivery of the La Paloma surf forecast"
---

# Tasks: Personalized surf forecast for La Paloma

**Input**: Design documents from `/specs/001-la-paloma-surf-forecast/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Scope**: First delivery only — US1, US2, US3, and the immutable query snapshots required by FR-035. Do not implement US4–US9, observation entry, discrepancy workflows, criteria correction, days 5–10 outlook, reference forecasts, change summaries, or additional zones.

**Tests**: Verification is manual. Do not add `tests/`, pytest, CI, or automated unit, integration, or end-to-end tasks. Deterministic fixtures and `specs/001-la-paloma-surf-forecast/quickstart.md` are the verification path.

**Organization**: Tasks are grouped by user story so each story can be checked with a fixture replay or command. Shared files (`domain/evaluation.py`, `domain/confidence.py`, `presentation/cli.py`, `presentation/tui/screens.py`) make the story phases sequential.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: User-story phase only (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the installable single-package skeleton from plan.md

- [ ] T001 [P] Create `pyproject.toml` for Python >=3.12 with runtime dependencies `textual>=8.2,<9` and `tzdata`, a `src` layout for package `surf_forecast`, and no test or CI extras
- [ ] T002 [P] Add `.gitignore` entries for `.venv/`, `__pycache__/`, `*.pyc`, and `data/` while keeping `config/` and `fixtures/` tracked
- [ ] T003 [P] Create the package skeleton `src/surf_forecast/__init__.py`, `src/surf_forecast/__main__.py`, `src/surf_forecast/application/__init__.py`, `src/surf_forecast/domain/__init__.py`, `src/surf_forecast/sources/__init__.py`, `src/surf_forecast/storage/__init__.py`, `src/surf_forecast/presentation/__init__.py`, and `src/surf_forecast/presentation/tui/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types, configuration, persistence, and adapter boundaries required before any user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Define English `snake_case` enums and dataclasses in `src/surf_forecast/domain/models.py` for surf grades, `uncertain` and `incomplete_forecast` states, quality classes, `DirectionSector`, `PeakProfile`, `CriteriaSet`, `GradeBand`, `SourceDescriptor`, `SourceFetch`, `SwellTrend`, `DaySummary`, normalized marine and wind hours, `Incident`, and `QueryRequest` per `specs/001-la-paloma-surf-forecast/data-model.md`
- [ ] T005 Implement `America/Montevideo` conversion with `zoneinfo` and `tzdata`, the fixed 06:00–20:00 analysis window, the today-through-day-+4 horizon, and the at-or-after-20:00 `analysis_window_completed` flag in `src/surf_forecast/domain/windows.py`
- [ ] T006 Create versioned `config/criteria.json` (`point_k` 0.5, range multipliers 0.5 and 0.7, non-overlapping size and wind bands, two-factor one-step quality downgrade, swell-trend thresholds, 180-minute freshness) and load, validate, and hash it in `src/surf_forecast/storage/config.py`
- [ ] T007 Define the swappable source request/result boundary and normalized forecast bundle in `src/surf_forecast/sources/base.py` without importing Open-Meteo or Textual
- [ ] T008 [P] Implement the replaceable raw JSON cache, 3-hour expiry, and atomic temp-file plus `os.replace` writes in `src/surf_forecast/storage/cache.py`, creating `data/cache/` at runtime
- [ ] T009 Implement append-only snapshot create and read in `src/surf_forecast/storage/snapshots.py` with `schema_version` `1.0.0`, fsync, collision failure, and the fields required by `specs/001-la-paloma-surf-forecast/contracts/schemas/query-snapshot.schema.json`, creating `data/snapshots/YYYY/MM/` at runtime
- [ ] T010 Define the immutable `ForecastPresentation` consumed by both adapters, including `shared_regional_input`, day headlines, best-peak IDs, reason codes, and the separate Spanish display labels, in `src/surf_forecast/domain/presentation.py`
- [ ] T011 Parse subcommands and `--json`, aware `--now`, `--fixture`, and mutually exclusive `--refresh` and `--stored-only` in `src/surf_forecast/presentation/cli.py`, and dispatch them from `src/surf_forecast/__main__.py` using the exit codes in `specs/001-la-paloma-surf-forecast/contracts/cli.md`
- [ ] T012 Serialize `ForecastPresentation` to one schema-versioned JSON document in `src/surf_forecast/presentation/json_output.py` per `specs/001-la-paloma-surf-forecast/contracts/schemas/forecast-output.schema.json`, sending diagnostics to stderr

**Checkpoint**: Configuration, timezone, cache, snapshots, and both output adapters exist, but no forecast is evaluated yet

---

## Phase 3: User Story 1 - Conditions today and coming days (Priority: P1)

**Goal**: One query returns a five-day summary for every complete peak, with confidence, source incidents, and an immutable snapshot

**Independent Test**: `python -m surf_forecast fixtures replay fixtures/normal --now 2026-10-13T15:00:00-03:00 --json` emits today through day +4, stable English condition identifiers, Spanish labels, a new snapshot ID, and does not access the network

### Implementation for User Story 1

- [ ] T013 [P] [US1] Author the five provisional profiles (La Aguada, Zanja Honda, Los Botes, La Serena, La Balconada) in `config/peaks.json` and load them by `peak_id` in `src/surf_forecast/storage/config.py`
- [ ] T014 [P] [US1] Implement Open-Meteo marine `ncep_gfswave025` and GFS wind acquisition, hourly normalization, attribution, a 10-second timeout, and one bounded retry in `src/surf_forecast/sources/open_meteo.py`
- [ ] T015 [P] [US1] Implement the day-level `k × Hs` point and 0.5–0.7 range, size-band ceiling, two-or-more unfavorable-factor one-step downgrade, Small-but-surfable floor, range-crossing `uncertain` state, missing-input `incomplete_forecast` state, rule-based `reason_codes`, day headline, wind rotation, and `best_peak_ids` in `src/surf_forecast/domain/evaluation.py`
- [ ] T016 [P] [US1] Cap confidence at medium for the single NOAA/NCEP GFS family and for provisional profiles, keep that cap for user-marked calibrated profiles while only one model family is in use, and reduce it to low for stale or missing required inputs in `src/surf_forecast/domain/confidence.py`
- [ ] T017 [US1] Orchestrate normal, forced-refresh, stored-only, partial-failure, stale-cache, and all-source-failure flows in `src/surf_forecast/application/forecast_service.py`, committing the snapshot before reporting success
- [ ] T018 [US1] Run that same evaluation path against fixture payloads and an explicit reference time in `src/surf_forecast/application/replay_service.py`, marking the snapshot mode `fixture_replay`
- [ ] T019 [US1] Implement `forecast`, `sources status`, and `fixtures replay` in `src/surf_forecast/presentation/cli.py` with Spanish human output and `--json` output from the shared presentation model
- [ ] T020 [P] [US1] Add a network-free normal marine/wind fixture and its expected five-day outcome in `fixtures/normal/` and `fixtures/README.md`
- [ ] T021 [P] [US1] Build the Spanish status/help bar, source freshness line, and `Datos: Open-Meteo (CC BY 4.0)` attribution in `src/surf_forecast/presentation/tui/widgets.py`
- [ ] T022 [P] [US1] Build the main day, peak, and selected-detail panels from `ForecastPresentation` in `src/surf_forecast/presentation/tui/screens.py`, including headline, best-peak highlighting, short Spanish reason labels, and the shared-grid warning on the main forecast screen
- [ ] T023 [US1] Launch the full-screen app, start the normal query in a Textual thread worker, and keep the shell responsive in `src/surf_forecast/presentation/tui/app.py` for both no-subcommand and `tui`

**Checkpoint**: A fixture query and the main TUI both show the US1 five-day forecast without duplicating domain rules in the TUI

---

## Phase 4: User Story 2 - Detail by peak and time slot (Priority: P1)

**Goal**: A selected peak and day shows reference slots and the best supported window of at least two hours

**Independent Test**: Detail for a fixture peak and date shows 06:00, 12:00, and 18:00 when those hours remain inside the analysis window, a contiguous window of at least 120 minutes when hourly data supports it, and an explicit unavailable window for coarser samples. The command does not create a snapshot

### Implementation for User Story 2

- [ ] T024 [P] [US2] Add hourly slot evaluation, wind direction and intensity bands, per-factor quality classes, swell building/peaking/dropping/steady/unsupported trend, and 06:00/12:00/18:00 reference slots in `src/surf_forecast/domain/evaluation.py`, using morning, midday, or afternoon labels from day +2 through day +4
- [ ] T025 [P] [US2] Calculate the best contiguous window of at least 120 minutes inside 06:00–20:00 local time in `src/surf_forecast/domain/windows.py`, refusing silent interpolation when samples are coarser than hourly, and emitting no window (never `no_surfable_waves`) when fewer than two valid hours exist
- [ ] T026 [US2] Implement read-only `detail --date --peak [--snapshot]` in `src/surf_forecast/presentation/cli.py` and `src/surf_forecast/application/forecast_service.py`
- [ ] T027 [US2] Add day/peak drill-in and the detail panel content required by `specs/001-la-paloma-surf-forecast/contracts/tui.md` in `src/surf_forecast/presentation/tui/screens.py`
- [ ] T028 [P] [US2] Add hourly-window and unsupported three-hour-sample fixtures, with expected outcomes, in `fixtures/boundaries/` and `fixtures/README.md`

**Checkpoint**: US1 summaries remain unchanged, and US2 detail is available from both the command and the TUI

---

## Phase 5: User Story 3 - Profile for each peak (Priority: P1)

**Goal**: Each peak is validated as incomplete, provisional, or user-marked calibrated, and only complete profiles receive a condition

**Independent Test**: `python -m surf_forecast profiles validate` reports the five initial profiles as provisional, reports an incomplete fixture with its missing essential fields and no condition, reports incoherent sectors, honors a user-marked calibrated complete profile, treats a calibrated-but-incomplete file as incomplete, and never rewrites the JSON or promotes a profile to calibrated

### Implementation for User Story 3

- [ ] T029 [P] [US3] Validate essential fields, numeric ranges, direction-sector coherence, and unique `peak_id` values without editing files in `src/surf_forecast/application/profile_service.py`, honoring user-marked `calibrated` only when essential fields are complete
- [ ] T030 [P] [US3] Apply the provisional-profile medium confidence ceiling, keep the medium cap for calibrated profiles while only one model family is in use, and ignore any attempt to promote a profile to calibrated automatically in `src/surf_forecast/domain/confidence.py`
- [ ] T031 [US3] Implement read-only `profiles list` and `profiles validate` in `src/surf_forecast/presentation/cli.py` using Spanish text and stable English JSON status identifiers
- [ ] T032 [US3] Add the read-only profile screen, including missing and estimated fields and the editable JSON path, in `src/surf_forecast/presentation/tui/screens.py`
- [ ] T033 [P] [US3] Add complete, incomplete, incoherent, user-marked calibrated, and calibrated-but-incomplete profile fixtures with expected statuses in `fixtures/boundaries/` and `fixtures/README.md`

**Checkpoint**: Profile status is visible before evaluation, and incomplete peaks never receive a surf condition

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete the shared operational and manual-acceptance behavior across US1–US3

- [ ] T034 [P] Re-evaluate an existing snapshot from its embedded inputs and configuration, then compare canonical result hashes without writing a new snapshot, in `src/surf_forecast/application/replay_service.py`
- [ ] T035 Implement read-only `snapshots show` and `snapshots replay` in `src/surf_forecast/presentation/cli.py`, returning exit code 5 on a hash mismatch
- [ ] T036 [P] Add cache-boundary, before-20:00, at-or-after-20:00, fewer-than-two-valid-hours, one-unfavorable-factor (no downgrade), two-unfavorable-factor (one-step downgrade with floor), swell-trend, partial-failure, all-source-failure, stale-cache, and snapshot-immutability fixtures with expected outcomes in `fixtures/boundaries/`, `fixtures/failures/`, and `fixtures/README.md`
- [ ] T037 Complete loading, partial-failure, stale, unavailable, and analysis-window-completed states, plus Help/About and the key bindings in `specs/001-la-paloma-surf-forecast/contracts/tui.md`, in `src/surf_forecast/presentation/tui/app.py` and `src/surf_forecast/presentation/tui/screens.py`
- [ ] T038 Walk `specs/001-la-paloma-surf-forecast/quickstart.md` manually, including the live sub-30-second observation for SC-001, and record each observed outcome in `fixtures/README.md` without adding an automated test suite or CI workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational
- **User Story 2 (Phase 4)**: Depends on US1 because it extends `domain/evaluation.py`, `presentation/cli.py`, and `presentation/tui/screens.py`
- **User Story 3 (Phase 5)**: Depends on US1 because it extends `domain/confidence.py`, `presentation/cli.py`, and `presentation/tui/screens.py`; it does not require US2 detail behavior
- **Polish (Phase 6)**: Depends on US1–US3

### User Story Dependencies

- **US1**: First runnable forecast increment; no dependency on US2 or US3
- **US2**: Adds slot and window detail to the US1 forecast; independently checkable through `detail` and window fixtures
- **US3**: Adds profile validation and status presentation; independently checkable through `profiles validate` and profile fixtures
- **US4–US9**: Out of scope for this task list

### Within Each User Story

- Domain rules before the application service that calls them
- Application service before the CLI or TUI task that dispatches it
- A fixture task may be written alongside its domain task because it lives in `fixtures/`
- No story is complete until its command and TUI surface consume the same presentation model

### Parallel Opportunities

- T001, T002, and T003 can run together
- After T004, T005, T006, T007, T009, T010, and T011 proceed in file order; T008 can run with them; T012 follows T010
- In US1, T013, T014, T015, T016, T020, T021, and T022 can run together after Phase 2
- In US2, T024 and T025 can run together, and T028 can be written at the same time
- In US3, T029 and T030 can run together, and T033 can be written at the same time
- T034 and T036 can run together during polish

---

## Parallel Example: User Story 1

```text
# After Phase 2, independent files can proceed together:
T013 config/peaks.json and src/surf_forecast/storage/config.py
T014 src/surf_forecast/sources/open_meteo.py
T015 src/surf_forecast/domain/evaluation.py
T016 src/surf_forecast/domain/confidence.py
T020 fixtures/normal/ and fixtures/README.md
T021 src/surf_forecast/presentation/tui/widgets.py
T022 src/surf_forecast/presentation/tui/screens.py

# Then, in order:
T017 src/surf_forecast/application/forecast_service.py
T018 src/surf_forecast/application/replay_service.py
T019 src/surf_forecast/presentation/cli.py
T023 src/surf_forecast/presentation/tui/app.py
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3
3. Stop and run the US1 fixture replay and a stored snapshot inspection
4. Continue only after the five-day summary, degraded states, and snapshot ID are visible

### Incremental Delivery

1. Setup plus Foundational produces the package, configuration, and storage boundaries
2. US1 produces the first runnable forecast command, fixture replay, and main TUI
3. US2 adds peak/time detail without a second forecast calculation
4. US3 adds profile validation and the provisional confidence ceiling
5. Polish completes snapshot replay, the remaining manual fixtures, and the quickstart checklist

### Sequential Story Strategy

US2 and US3 both extend files created for US1. Implement the stories in phase order rather than assigning those files to parallel implementers.

---

## Notes

- Tasks T001–T038 are the complete first-delivery list
- [P] tasks use different files and do not wait on another incomplete [P] task
- Fixture tasks document expected outcomes; they are not executable assertions
- Commit after each completed phase or logical group
- Stop at each checkpoint and verify that story through the command in its Independent Test section
