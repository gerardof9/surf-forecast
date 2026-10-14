# Research: Surfer-friendly TUI redesign

**Feature**: `003-tui-redesign`  
**Date**: 2026-10-14  
**Code inspected**: `src/surf_forecast/presentation/tui/*`, `domain/presentation.py`, `domain/evaluation.py`, `domain/models.py`, `application/forecast_service.py`, `specs/001-*/contracts/*`, mockups `mock1.jpg` / `mock2.png`

## Inspection summary (as-found)

| Area | Current state |
|------|----------------|
| TUI library | Textual `>=8.2,<9` (`pyproject.toml`) |
| Entry | `SurfForecastApp` in `presentation/tui/app.py`; default `ForecastScreen` |
| Layout | Three `DataTable`/`Static` panes (days / peaks / detail) — **not** View A/B |
| Profiles | `ProfileScreen` + binding `p` — **conflicts** with FR-026 (remove interactive profiles UI) |
| Labels | `CONDITION_LABELS` / `STATE_LABELS` in `domain/presentation.py` — **conflicts** with FR-017 compact map |
| Engine | `evaluation.py` ranks peaks via `GRADE_ORDER`; `best_peak_ids` / `highlighted` already exist |
| Presentation | Shared `ForecastPresentation.payload` for TUI + JSON; `schema_version` `1.0.0` |
| Tests | No `tests/` tree; verification is fixture/manual per `001` |
| Mockups | `mock2.png` binding hierarchy; `mock1.jpg` non-binding (imperial / secondary swell / air / multi-day chart) |

## Discrepancies and resolutions

| Discrepancy | Resolution (constitution-aligned) |
|-------------|-----------------------------------|
| 3-pane comparator vs daily report | Replace TUI composition with View A / View B per `mock2.png` + `spec.md`; keep same `run_forecast` use case |
| Labels `Aceptable`/`Buena`/… vs FR-017 | Change **display** labels and presentation mapping only; do not change `SurfGrade` thresholds |
| `SPOTS RECOMENDADOS` in mock | Use neutral `PICOS DEL DÍA` / `SPOTS EVALUADOS` (clarify) |
| Profile screen present | Remove from TUI; keep JSON path in Help; keep `list_profiles` for non-TUI if needed |
| `mock1.jpg` dense chart product | Out of scope; do not fabricate secondary swell / °F / ft |
| Spec mentions “presentation tests”; repo has none | Add **focused** pure-Python checks for rating/narrative/sampling transforms (Principle XI); TUI visuals remain manual checklist |
| New presentation fields vs schema `1.0.0` | Additive bump to `1.1.0`; old fixtures remain readable for engine replay; new fields required for redesigned adapters |

---

## Decision: Keep Textual; no new UI dependency

- **Decision**: Continue with Textual 8.x only. No Rich dashboard rewrite, no alternative TUI kit.
- **Rationale**: Already integrated with workers, screens, bindings; constitution forbids unjustified deps (XIV). Existing app structure maps cleanly to Screen A / Screen B (or one screen with mode).
- **Alternatives considered**: Raw curses / blessed (higher maintenance); web UI (constitution/out of scope).

## Decision: Interpretation layer beside presentation builder (not inside Textual)

- **Decision**: Add pure domain/application helpers (e.g. `domain/day_rating.py`, `domain/narrative.py`, sampling helper) invoked from `build_presentation` (or a thin `build_report_presentation` wrapper). TUI only renders payload fields.
- **Rationale**: FR-023/024; Principles IV/VIII; CLI/JSON/snapshots stay consistent; deterministic fixture checks without Textual.
- **Alternatives considered**: Generate narrative inside widgets (rejected: duplicates logic, breaks JSON parity); LLM/free-form text (rejected: invents meteorology).

## Decision: Vocabulary is display-only mapping

- **Decision**: Replace user-facing label tables with FR-017 map; keep English machine ids (`fair`, `good`, …) in payload `condition` / `state`.
- **Rationale**: Spec clarify; no engine rewrite.
- **Alternatives considered**: Rename enums (rejected: breaks snapshots/engine).

## Decision: Day/peak 1–5 from resolved grade (candidate — confirm before implement)

- **Decision (proposed default)**: Map resolved `SurfGrade` → score; day score = score of best resolved peak (existing `GRADE_ORDER` / `best_peak_ids` semantics). Non-resolved → no numeric score / `Sin valoración` for the day when none resolve.

| Grade | Score |
|-------|------:|
| `no_surfable_waves` | 1.0 |
| `small_but_surfable` | 2.0 |
| `fair` | 3.0 |
| `good` | 4.0 |
| `very_good` | 5.0 |

- **Rationale**: Deterministic, mirrors engine ranking already used for `highlighted` / `best_peak_ids`, uses full 1–5 span, no arbitrary multi-peak blend (clarify Option A). Half-steps unused in v1 unless a later confirmed within-band rule is added.
- **Alternatives considered**: Multi-peak composite (rejected in clarify); include uncertain peaks (rejected); invent continuous regression on Hs (rejected: arbitrary vs engine grades).
- **PENDING CONFIRMATION**: Stakeholder must accept this table (or supply another documented table) before coding. Plan MUST NOT invent alternate weights silently.

## Decision: Template narrative (no generative model)

- **Decision**: Spanish sentences from fixed templates filled only when facts exist: swell trend label, dominant direction/period if present, wind rotation/intensity summary, best-peak exposure notes from profiles, size range text, explicit limitation clauses for missing pieces / single source / shared grid / provisional profiles.
- **Rationale**: Spec + user guidance; Principles V/VIII.
- **Alternatives considered**: LLM (cost/invention risk); hand-written static blurbs (not data-linked).

## Decision: Sampled evolution display

- **Decision (proposed default)**: View B shows up to three rows — first available slot in bands `06:00–10:59`, `11:00–14:59`, `15:00–20:00` America/Montevideo within the analysis window. Omit empty bands. Best window remains engine field, not inferred from samples.
- **Rationale**: Clarify Option A + mock density; full `reference_slots` stay in payload for verification.
- **PENDING CONFIRMATION**: Exact band edges may be adjusted in tasks if stakeholder prefers different clocks; must remain documented.

## Decision: Technical details collapsed; profiles out; stored-only stays

- **Decision**: `D` toggles collapsed-by-default technical section; remove `p`/ProfileScreen; keep `o` stored-only; update Help.
- **Rationale**: Clarify answers.

## Decision: Schema / snapshot compatibility

- **Decision**: Bump presentation `schema_version` to `1.1.0` with additive fields (`day_rating`, `day_analysis`, `peak_rating`, `peak_analysis`, `evolution_samples`, display labels, dual timestamps). Engine evaluation outputs unchanged. Replay of old `1.0.0` snapshots remains for engine/path tests; redesigned TUI targets `1.1.0` payloads from new queries.
- **Rationale**: Traceability + shared presentation without breaking engine.
- **Alternatives considered**: Overwrite 1.0.0 in place (harder for old fixtures); TUI-only ephemeral fields (rejected by FR-024).

## Decision: Verification approach

- **Decision**: (1) Pure-Python deterministic checks for grade→score, narrative omission rules, sampling bands, label map. (2) Manual quickstart checklist for View A/B, keyboard, narrow/wide, incomplete/uncertain/provisional/window-completed. (3) Existing engine fixture replay must still pass.
- **Rationale**: Principle XI; no CI mandate.

## Open decisions (must resolve before implementation tasks that depend on them)

1. Confirm grade→1.0–5.0 table above (or replace with stakeholder table).
2. Confirm qualitative captions per score (optional FR-008) — proposed short Spanish phrases in `data-model.md`.
3. Confirm evolution sample band edges.
4. Confirm canonical section title string: `PICOS DEL DÍA` vs `SPOTS EVALUADOS` (both allowed; pick one for UI copy consistency).

These are **not** engine changes; they are presentation-policy confirmations required by the user’s plan constraints.
