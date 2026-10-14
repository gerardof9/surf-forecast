# Implementation Plan: Surfer-friendly TUI redesign

**Branch**: `003-tui-redesign` | **Date**: 2026-10-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-tui-redesign/spec.md` plus planning prompt to redesign the existing Textual TUI into a daily surf report without rewriting the forecast engine.

**Visual refs**: [mock2.png](./mock2.png) (binding hierarchy), [mock1.jpg](./mock1.jpg) (non-binding)

## Summary

Replace the current three-pane comparator TUI with a **daily surf report** (View A) and **peak detail** (View B) that answer day conditions, best spots/why, timing, and confidence—while keeping acquisition/evaluation/snapshots untouched. Extend the shared presentation payload (`schema_version` `1.1.0`) with template-based Spanish analysis, documented best-resolved-peak 1–5 ratings, FR-017 labels, sampled evolution rows, and dual timestamps. Textual remains the only UI dependency; interpretation logic lives outside widgets so CLI/JSON/snapshots stay consistent.

## Technical Context

**Language/Version**: Python 3.12+ (existing)

**Primary Dependencies**: Textual 8.x (existing); stdlib + current Open-Meteo stack unchanged. **No new UI dependency.**

**Storage**: Existing JSON config, cache, immutable snapshots; presentation schema bump `1.0.0` → `1.1.0` (additive)

**Testing**: Focused pure-Python checks for rating/narrative/sampling/labels (Principle XI); manual TUI checklist in `quickstart.md`; existing engine fixture replay must pass. No CI mandate.

**Target Platform**: Windows 10/11, Windows Terminal, PowerShell (unchanged)

**Project Type**: Single Python package; presentation adapters only for this feature

**Performance Goals**: Keep TUI responsive during workers (<30s typical query unchanged); navigation/render of report views without blocking

**Constraints**: Zero cost; on-demand; no favorites/alerts/preferences; no engine threshold changes for visuals; no invented meteorology; inform ≠ recommend; mock1 fields not fabricated

**Scale/Scope**: Five days × five peaks; two primary views; one collapsible technical section; remove profiles TUI screen

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- [x] **I. Zero cost / personal use**: No paid services; Open-Meteo attribution retained
- [x] **II. On-demand execution**: Worker-driven queries only; no daemons/alerts
- [x] **III. Configurable criteria**: Engine criteria unchanged; rating map is versioned presentation method string
- [x] **IV. Modular simplicity**: Engine / interpretation / Textual remain separated
- [x] **V. Honest uncertainty**: Ratings not probabilities; incomplete ≠ no waves; limitations visible
- [x] **VI. Inform, don't decide**: Neutral `PICOS DEL DÍA`; no “recomendados” advice framing
- [x] **VII. Reality validation**: No superiority claims; mock numbers not treated as truth
- [x] **VIII. No invented/confused data**: Template narratives; Hs vs derived size in technicals; dual times
- [x] **IX. Traceability**: Snapshots include shared 1.1.0 presentation fields
- [x] **X. Simplicity first**: Extend presentation + rewrite TUI screens; no alternate UI kit
- [x] **XI. Pragmatic verification**: Focused transforms tests + manual checklist; no enterprise CI
- [x] **XII. Graceful degradation**: Existing degraded/stored-only paths retained in UI status
- [x] **XIII. Privacy / minimal scope**: No accounts/telemetry/preferences persistence
- [x] **XIV. Implementation discipline**: Presentation policies confirmed; Textual retained with justification below

### Post-design re-check

Phase 1 artifacts keep ratings/narratives out of widgets and preserve engine contracts. Pending presentation-policy items were **confirmed 2026-10-14** (see below and `research.md`).

## Pre-/tasks gate review (stakeholder)

| # | Criterion | Verdict |
|---|-----------|---------|
| 1 | Global 1–5 must be **defined and justified**, not an opaque invented formula | **Pass**. Score = ordinal encoding of existing engine `SurfGrade` (`no_surfable_waves`→1.0 … `very_good`→5.0). Day rating = score of best resolved peak via existing `GRADE_ORDER` / `best_peak_ids`. Does **not** recompute size/quality/confidence. Method `best_resolved_grade_map_v1`. Half-steps unused in v1. |
| 2 | Narrative from **available structured data**; no LLM / external generative service | **Pass**. Fixed Spanish templates in `domain/narrative.py`; omit or limitation when facts missing. Explicitly forbids LLM/paid NLP APIs. |
| 3 | TUI **reuses** engine classifications/calculations; no second rule engine in UI | **Pass**. Widgets only render `ForecastPresentation` fields. Grades, windows, confidence stay in `evaluation.py`. Helpers map/display only. |
| — | Mockups | **Pass** for `mock2.png` hierarchy; `mock1.jpg` non-binding. |

**Ready for `/speckit-tasks`** after this confirmation.

## Deliberate Presentation Complexity

Reworking the full-screen TUI is justified against Principles IV, X, and XIV because:

1. Spec `003` explicitly requires View A/B daily-report UX replacing the comparator layout.
2. Both TUI and CLI/JSON continue to share one presentation builder; interpretation is not duplicated in widgets.
3. Textual already owns workers, screens, resize, and bindings—switching kits would add cost without benefit.
4. Scope excludes favorites, alerts, preferences, profiles browser, and mock1-only meteorology fields.

## Architecture

```text
application/forecast_service.run_forecast
        │
        ▼
domain/evaluation  (UNCHANGED thresholds / windows / confidence)
        │
        ▼
domain/presentation.build_presentation  ──► calls
        ├── domain/day_rating.py          (NEW) grade→score, best resolved day rating
        ├── domain/narrative.py           (NEW) template day/peak analysis
        └── domain/evolution_samples.py   (NEW) band sampling for View B
        │
        ▼
ForecastPresentation.payload  schema 1.1.0
        ├── presentation/cli.py           (UPDATE human summary)
        └── presentation/tui/
                ├── app.py                (bindings: remove profiles; keep o/R/?)
                ├── screens.py            (DailyReportScreen + PeakDetailScreen)
                └── widgets.py            (stars, cards, legend, status, technicals)
```

### View responsibilities

| View | Responsibility |
|------|----------------|
| **View A** `DailyReportScreen` | Day list focus, analysis, day rating glyphs, ranked peak cards, legend, dual-time header |
| **View B** `PeakDetailScreen` | Peak summary, samples, best window, peak analysis, collapsed technicals |
| **Help** | Keys, honesty, FR-017 meanings, config path for profiles JSON |
| **App** | Workers, refresh/stored-only, screen push/pop |

## Confirmed functional decisions (2026-10-14)

1. **Grade→score**: `no_surfable_waves` 1.0 · `small_but_surfable` 2.0 · `fair` 3.0 · `good` 4.0 · `very_good` 5.0; day = best resolved peak; method `best_resolved_grade_map_v1`.
2. **Captions**: as listed in `data-model.md` (optional FR-008 accompaniment).
3. **Evolution bands**: first slot in `06:00–10:59`, `11:00–14:59`, `15:00–20:00` UYT; omit empty; best window from engine only.
4. **Section title**: `PICOS DEL DÍA`.

## Project Structure

### Documentation (this feature)

```text
specs/003-tui-redesign/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── spec.md
├── mock1.jpg
├── mock2.png
├── contracts/
│   ├── tui.md
│   └── presentation.md
├── checklists/requirements.md
└── tasks.md                 # NOT created by /speckit-plan
```

### Source Code (repository)

```text
src/surf_forecast/
├── domain/
│   ├── presentation.py          # extend labels + wire report fields
│   ├── day_rating.py            # NEW
│   ├── narrative.py             # NEW
│   ├── evolution_samples.py     # NEW
│   ├── evaluation.py            # DO NOT change thresholds for UI
│   └── models.py                # only if tiny DTO helpers needed
├── application/
│   └── forecast_service.py      # usually untouched; snapshot still stores presentation
├── presentation/
│   ├── cli.py                   # show analysis/ratings
│   ├── json_output.py           # schema 1.1.0 awareness if any
│   └── tui/
│       ├── app.py               # bindings / remove ProfileScreen
│       ├── screens.py           # View A/B rewrite
│       └── widgets.py           # stars, cards, legend, technical block
└── … sources/storage unchanged for this feature
```

**Structure Decision**: Single package; additive domain report helpers + TUI rewrite. No new top-level apps.

## Implementation order (small, verifiable slices)

1. **Label map + schema 1.1.0 fields** in `presentation.py` (condition_label, display_name) with focused checks.
2. **Day/peak rating helpers** + wire into payload; CLI smoke print.
3. **Narrative templates** (day then peak) with omission rules + checks.
4. **Evolution sampling** helper + payload `evolution_samples`.
5. **Dual timestamps** in payload/header helpers.
6. **View A TUI** (days, analysis, rating, cards, legend, focus/bindings).
7. **View B TUI** (detail, samples, best window, peak analysis, collapsed technicals).
8. **Remove ProfileScreen**; update Help; keep stored-only `o`.
9. **Manual quickstart** matrix + ensure engine fixture replay still green.

## Files affected (expected)

| Path | Change |
|------|--------|
| `src/surf_forecast/domain/presentation.py` | FR-017 labels; assemble 1.1.0 fields |
| `src/surf_forecast/domain/day_rating.py` | **NEW** |
| `src/surf_forecast/domain/narrative.py` | **NEW** |
| `src/surf_forecast/domain/evolution_samples.py` | **NEW** |
| `src/surf_forecast/presentation/tui/screens.py` | Replace ForecastScreen layout with A/B |
| `src/surf_forecast/presentation/tui/app.py` | Bindings; drop profiles action |
| `src/surf_forecast/presentation/tui/widgets.py` | Stars, cards, legend, technical panel |
| `src/surf_forecast/presentation/cli.py` | Print analysis/ratings |
| `specs/001-.../contracts/schemas/forecast-output.schema.json` | Optional follow-up: document 1.1.0 additive props **or** add `forecast-output-1.1.0.schema.json` under `003/contracts/` in tasks—prefer **new 003 schema file** to avoid rewriting `001` history silently |
| Focused check module/script | **NEW** under `scripts/` or `src/.../checks` as tasks decide |

## Testing strategy

1. **Pure transforms**: label map, score map, best-peak selection, narrative omission, sampling bands.
2. **Engine regression**: existing fixture replay / manual engine scenarios from `001` quickstart still pass.
3. **Manual TUI**: `quickstart.md` scenarios (good / mixed / incomplete / provisional / window completed / dual time / narrow width).
4. **Stars**: numeric and glyph always agree; half-step glyph fallback if a half score is ever emitted.

## Risks and incompatibilities

| Risk | Mitigation |
|------|------------|
| Score misread as calibrated skill | Documented ordinal map + method id + Help honesty; never recompute grades in TUI |
| Narrative invents weather | Templates + unit checks on missing-fact fixtures |
| Schema break for old snapshots | Additive 1.1.0; keep engine replay on 1.0.0 |
| mock2 vs terminal width | Responsive stack; scroll analysis |
| Removing profiles UI surprises | Help shows JSON path; FR-026 explicit |
| Sampling hides hours | Best window still from engine; full slots retained in payload |
| Branch name detector shows `004` | Feature dir/branch of record: `003-tui-redesign` |

## Complexity Tracking

> No constitution violations requiring exceptions. Textual retention and presentation-layer rating/narrative are justified in Deliberate Presentation Complexity and research.md.

## Phase outputs

| Artifact | Path |
|----------|------|
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| TUI contract | [contracts/tui.md](./contracts/tui.md) |
| Presentation contract | [contracts/presentation.md](./contracts/presentation.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

**Next command**: `/speckit-tasks`. **Do not implement in this phase.**
