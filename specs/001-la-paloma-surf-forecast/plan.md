# Implementation Plan: Personalized surf forecast for La Paloma

**Branch**: `001-la-paloma-surf-forecast` | **Date**: 2026-10-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-la-paloma-surf-forecast/spec.md`

## Summary

Build the first delivery only (US1–US3 plus FR-035 immutable query
snapshots) as a local Python application for Windows. The same application
use cases feed two thin adapters: a Spanish full-screen Textual TUI and
non-interactive commands with stable English JSON identifiers. Open-Meteo is
the selected zero-cost access service, with explicit NOAA/NCEP GFS Wave 0.25°
and GFS atmospheric model selection. The application normalizes source data,
evaluates versioned peak/criteria configuration, writes atomic immutable JSON
snapshots, and presents uncertainty and degraded states without claiming
unsupported coastal precision.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Textual 8.x (full-screen TUI and workers), `tzdata`
(IANA timezone database on Windows); Python standard library for HTTP, JSON,
CLI parsing, file persistence, hashing, and concurrency

**External Services**: Open-Meteo Marine API with
`models=ncep_gfswave025`; Open-Meteo GFS API with explicit GFS atmospheric
selection. Both are one access service and one NOAA model family, not
independent confirmation.

**Storage**: Human-editable versioned JSON configuration; short-lived raw JSON
cache; one atomic immutable normalized JSON file per emitted query snapshot;
deterministic JSON fixtures for manual replay. No database in the MVP.

**Verification**: Manual only. Deterministic offline fixture replay with an
explicit reference time and expected-result checklists. No unit, integration,
E2E, or CI infrastructure.

**Target Platform**: Windows 10/11, Windows Terminal, PowerShell; local
filesystem and internet connection, with stored-only offline fallback

**Project Type**: Single Python package with application/domain layers and two
presentation adapters (Textual TUI + non-interactive CLI/JSON)

**Performance Goals**: A typical connected query reaches a summary in under
30 seconds in at least 90% of runs; keyboard navigation and rendering remain
responsive while network/filesystem work runs in workers; cached/stored-only
results render without network delay.

**Constraints**: Zero mandatory cost; non-commercial personal use; no API key;
Open-Meteo free limits of 600 calls/minute, 5,000/hour, 10,000/day and
300,000/month; 3-hour freshness TTL; fixed 06:00–20:00
`America/Montevideo` analysis window; Spanish human-facing UI; English
machine identifiers; no server, scheduler, telemetry, account, web UI, or
background daemon.

**Scale/Scope**: One user, five configured peaks, five local calendar days,
about 120 hourly values per requested variable and source, one marine anchor,
one regional wind anchor, and append-only snapshots produced only on demand.

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- [x] **I. Zero cost / personal use**: Open-Meteo free non-commercial API
      requires no key or card. Quotas and CC BY 4.0 attribution are documented.
- [x] **II. On-demand execution**: All work starts from a TUI/CLI action. No
      server, scheduler, daemon, or permanent process is designed.
- [x] **III. Configurable criteria**: Profiles, thresholds, `k`, `k_range`,
      wind bands, and criteria metadata are versioned JSON configuration.
- [x] **IV. Modular simplicity**: Acquisition, normalization, persistence,
      evaluation, application use cases, and presentation have narrow
      boundaries. The TUI and CLI contain no domain rules.
- [x] **V. Honest uncertainty**: The `k_range` is labeled an uncalibrated
      policy range; crossings yield Uncertain and no probability is emitted.
- [x] **VI. Inform, don't decide**: Outputs describe conditions and confidence;
      they never recommend surfing or travel.
- [x] **VII. Reality validation**: The MVP preserves reproducible snapshots and
      fixtures but makes no superiority claims; observations remain later scope.
- [x] **VIII. No invented/confused data**: Raw Hs, derived surfable range,
      model/grid identity, units, and unavailable run time remain distinct.
- [x] **IX. Traceability**: Every emitted query receives an immutable snapshot
      containing normalized inputs, provenance, effective versions, results,
      confidence, and incidents.
- [x] **X. Simplicity first**: One package, one selected source service,
      standard-library HTTP and JSON files; no database or plugin framework.
- [x] **XI. Pragmatic verification**: Manual deterministic fixture replay and
      boundary checklists match the explicitly chosen verification policy.
- [x] **XII. Graceful degradation**: Partial failure, stale cache, stored-only,
      all-source failure, and missing-variable states are contractually visible.
- [x] **XIII. Privacy / minimal scope**: No user accounts, payments, telemetry,
      or personal-data collection.
- [x] **XIV. Implementation discipline**: TUI/CLI complexity and dependencies
      are justified below; all material choices remain reversible.

### Post-design re-check

The Phase 1 model and contracts preserve all checks. No contract bypasses the
application use cases, no persistence design mutates prior snapshots, and no
later-stage observation or correction capability entered the MVP.

## Deliberate Presentation Complexity

The full-screen TUI and JSON CLI are justified against Principles IV, X, and
XIV because:

1. The user explicitly selected a keyboard-driven full-screen terminal
   experience for the first delivery.
2. Both adapters call identical application use cases and consume the same
   immutable presentation model; they do not duplicate acquisition,
   evaluation, confidence, or persistence logic.
3. JSON output is the smallest concrete boundary that allows future desktop or
   web presentation without coupling those interfaces to the TUI.
4. Textual replaces bespoke terminal control, resize handling, key dispatch,
   and worker lifecycle code. Its dependency cost is lower than maintaining
   those behaviors locally.
5. The TUI is limited to forecast, detail, profile validation, source status,
   and help. It does not include editing workflows, charts, alerts, history
   analytics, observations, or later-stage features.

## Data-source Decision

- **Marine**: Open-Meteo Marine API, explicit
  `ncep_gfswave025`, initial requested anchor `-34.70, -54.10`,
  `cell_selection=sea`. The live verification on 2026-10-13 resolved to
  `-34.75, -54.0`, elevation 0, with 120 hourly values over five days.
- **Wind**: Open-Meteo GFS endpoint, initial requested regional anchor
  `-34.66, -54.18`, 10 m sustained speed/direction and gusts. The live
  verification resolved to a coarse model cell near
  `-34.61763, -54.140625`, elevation 8 m, with 120 hourly values.
- **Identity**: Open-Meteo is the provider/access service; NOAA/NCEP GFS Wave
  0.25° and GFS atmosphere are the datasets/models. They are not independent
  confirmations.
- **Limitation**: Open-Meteo returns valid timestamps and resolved grid
  coordinates but not the exact model initialization/run time in these
  responses. `model_run_at` is therefore explicitly `null` with availability
  `unavailable`, never inferred from update cadence.
- **Attribution**: Every human display includes “Datos: Open-Meteo
  (CC BY 4.0)” and the help/about contract shows
  `https://open-meteo.com/` plus the license URL. Snapshots retain attribution
  and transformation metadata.

## Uncertainty Decision

The initial point estimate is `k × Hs` with `k = 0.5`. The initial plausible
range uses configurable `k_low = 0.5` and `k_high = 0.7`, producing
`[k_low × Hs, k_high × Hs]`. This is an explicit conservative stakeholder
policy range, not a statistical confidence interval or validated physical
conversion. It prevents the point estimate alone from creating hard false
negatives near 0.5 m. A range crossing 0.5 m is Uncertain; a range wholly
below is No surfable waves; a supported range wholly at/above uses the point
estimate for the ceiling grade. All values are versioned and shown.

## Quality-downgrade Decision

Swell direction, period, and wind are each classified as favorable, neutral,
unfavorable, or unknown using the versioned criteria in `data-model.md`. The
grade falls by at most one step only when two or more of those factors are
unfavorable. One unfavorable factor is a visible reason, not a downgrade.
Unknown never counts. A supported size at or above 0.5 m never falls below
Small but surfable.

## Swell-trend Decision

When at least three hourly swell-height samples exist in the analysis window
(else total wave height), compare first-third and last-third means. A change
of at least 10% or 0.1 m, whichever is larger, is building or dropping; a
middle-third maximum with both ends lower is peaking; otherwise steady.
Fewer samples or coarser input is `unsupported`. This is a labeled derived
series, not an arrival-time forecast.

## Day-summary Decision

Each local day includes a rule-based headline, size range, dominant swell,
wind rotation from the first to last analysis-window slot (not a daily
average), swell trend, and `best_peak_ids`: complete peaks that share the
highest resolved grade. Uncertain and incomplete peaks are never “best.”
Every result also carries `shared_regional_input` so the coarse shared grid
is visible on the main forecast, not only in Help.

## Reliability Policy

- Marine and wind requests run concurrently in cancellable Textual thread
  workers using `urllib.request` with a 10-second timeout.
- One retry per failed request uses a short bounded delay; both attempts fit
  inside the 30-second target because sources run concurrently.
- Cache entries younger than 3 hours may be reused. Normal connected mode
  attempts a refresh when older.
- On request failure, fresh cache is used normally with age visible; stale
  cache may be used only as a clearly stale fallback with low confidence.
- Missing marine or wind data produces Incomplete forecast, never No surfable
  waves. No data and no stored snapshot produces an explicit unavailable state.
- TUI workers post presentation-model messages to the UI thread; they never
  mutate widgets directly.

## Project Structure

### Documentation (this feature)

```text
specs/001-la-paloma-surf-forecast/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── plan-prompt.md
├── checklists/
│   └── requirements.md
└── contracts/
    ├── tui.md
    ├── cli.md
    └── schemas/
        ├── forecast-output.schema.json
        └── query-snapshot.schema.json
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── surf_forecast/
    ├── __init__.py
    ├── __main__.py
    ├── application/
    │   ├── forecast_service.py
    │   ├── profile_service.py
    │   └── replay_service.py
    ├── domain/
    │   ├── models.py
    │   ├── evaluation.py
    │   ├── confidence.py
    │   ├── windows.py
    │   └── presentation.py
    ├── sources/
    │   ├── base.py
    │   └── open_meteo.py
    ├── storage/
    │   ├── cache.py
    │   ├── config.py
    │   └── snapshots.py
    └── presentation/
        ├── cli.py
        ├── json_output.py
        └── tui/
            ├── app.py
            ├── screens.py
            └── widgets.py
config/
├── peaks.json
└── criteria.json
fixtures/
├── README.md
├── normal/
├── boundaries/
└── failures/
data/                       # local runtime data; ignored by Git
├── cache/
└── snapshots/
```

**Structure Decision**: A single installable package keeps domain and
application logic independent of adapters without creating separate projects.
No `tests/` tree is planned because verification is explicitly manual;
deterministic inputs live under `fixtures/`.

## Incremental MVP Phases

### Phase A — Runnable offline vertical slice

- Package entry point, JSON config loading/validation, domain types.
- Fixture replay with explicit `--now`.
- Minimal `forecast --fixture ... --json` command.
- Atomic snapshot creation and inspection.
- **Runnable outcome**: deterministic JSON forecast from a checked-in fixture.

### Phase B — Live acquisition and resilience

- Open-Meteo marine/wind adapters, normalization, attribution.
- Concurrent requests, timeouts/retry, 3-hour cache, stored-only fallback.
- Source incidents and freshness/confidence caps.
- **Runnable outcome**: live or degraded non-interactive forecast with snapshot.

### Phase C — Complete evaluation

- Size range, two-factor quality downgrade, surfability/quality bands, wind
  classification, swell trend, day headlines, best peaks, and best windows.
- Five-day horizon, fewer-than-two-valid-hours, and after-20:00 behavior.
- Peak detail, profile validation, and honor of user-marked calibrated
  profiles without automatic promotion.
- **Runnable outcome**: complete US1–US3 JSON/text command workflow.

### Phase D — Thin full-screen TUI

- Dashboard/detail/profile screens, key bindings, status/help bar.
- Non-blocking workers and all loading/failure/stale/completed states.
- Spanish labels over the shared presentation model.
- **Runnable outcome**: user-selected TUI with no duplicated domain logic.

### Phase E — Manual acceptance pass

- Run the quickstart fixture matrix and live smoke checks.
- Confirm snapshot immutability/replay and JSON schemas.
- Record observed limitations without changing criteria silently.
- **Runnable outcome**: clean first-delivery candidate.

## Technical Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No automated tests or CI | Boundary regressions can escape notice | Deterministic fixtures, explicit `--now`, expected-result checklist, documented JSON contracts, criteria-version traceability |
| Coarse model grid vs nearby peaks | False local precision | One regional marine/wind input, resolved grid coordinates shown, profiles identified as the source of peak differences, confidence capped |
| `k` and range are uncalibrated | False positive/negative surfability | Visible/versioned `k` and range, crossing → Uncertain, no probability language, future observation calibration |
| Free API outage or changed terms | Missing forecast | Cache/stored-only modes, explicit incidents, source boundary, terms metadata, no automatic paid fallback |
| Missing model run timestamp | Reduced provenance | Store valid/download times and explicit `unavailable`; never infer run time |
| Windows terminal/timezone differences | Wrong local windows or broken rendering | Textual Windows support, `tzdata`, `America/Montevideo`, ASCII-safe identifiers, resize contract |
| Immutable JSON accumulation | Disk growth over long personal use | Small normalized snapshots, documented size inspection; no automatic deletion in MVP to preserve history |
| TUI and CLI drift | Inconsistent results | Shared application services and presentation model; adapters only serialize/render |

## Pragmatic Simplifications

- One provider/access service and one explicit model family; no ensemble or
  model consensus.
- One marine anchor and one regional wind anchor; no per-peak model fetches.
- JSON configuration and storage; no SQLite, migrations, ORM, or repository
  framework.
- Standard-library HTTP in Textual thread workers; no async HTTP dependency.
- Snapshot normalized inputs, provenance, and transformations; raw API payload
  remains only in the TTL cache because normalized snapshots are sufficient
  and smaller.
- No in-app profile editor: edit JSON and validate through TUI/CLI.
- No sunrise calculation, tide, maps, charts, alerts, narrative generation,
  observations, automatic adjustment, alternative-method engines (FR-045),
  or days 5–10 outlook.
- No localization framework: stable English identifiers plus Spanish display
  labels in the presentation mapping.

## Clean MVP Recommendation

Deliver Phases A–E with Open-Meteo GFS, atomic JSON snapshots, Textual, and
`tzdata`. Resist adding a second weather provider, SQLite, a profile editor,
plugin loading, automated adjustment, or web-serving capability until real
usage and observations demonstrate the need. The clean MVP is successful when
one PowerShell command opens a responsive Spanish TUI, the equivalent commands
emit schema-versioned JSON, all degraded states are explicit, and any emitted
forecast can be replayed from its snapshot.

## Complexity Tracking

No constitution violations require exceptions. The deliberate TUI/CLI adapter
cost is justified above and contained behind one shared application boundary.
