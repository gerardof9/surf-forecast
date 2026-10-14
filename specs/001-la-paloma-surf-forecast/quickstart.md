# Quickstart: First delivery

This guide describes the planned Windows workflow after implementation. It is
also the manual acceptance procedure. It does not define an automated test
suite or CI pipeline.

## Prerequisites

- Windows 10 or 11
- Windows Terminal and PowerShell
- Python 3.12 or newer
- Internet access for live queries; fixture and stored-only workflows work
  offline

The application uses `tzdata` so `ZoneInfo("America/Montevideo")` works on
Windows installations that do not ship the IANA database.

## Install

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

If PowerShell blocks activation, the equivalent commands can use
`.\.venv\Scripts\python.exe` directly. No account, API key, server, scheduler,
or background service is required.

## Configure and validate profiles

Edit these UTF-8 JSON files:

- `config/peaks.json`: five versioned peak profiles.
- `config/criteria.json`: size/wind bands, `k`, plausible-range policy,
  confidence rules, cache TTL, and analysis window.

Do not translate enum identifiers. Names and display labels may be Spanish;
identifiers such as `small_but_surfable` remain English.

Validate without modifying either file:

```powershell
python -m surf_forecast profiles validate
python -m surf_forecast profiles validate --json
python -m surf_forecast profiles list
```

An invalid essential location, orientation, ideal swell sector, or ideal period
makes the profile `incomplete`. Complete initial profiles remain
`provisional`; this delivery cannot promote them to `calibrated`.

## Use the TUI

```powershell
python -m surf_forecast
```

The full-screen interface is in Spanish. Use `?` for help, arrows or `j`/`k`
to move, `Enter` for detail, `r` to force refresh, `o` for stored-only mode,
`p` for profile status, and `q` to quit.

The footer always identifies loading, cache age, stale data, partial failure,
or unavailability. It also displays:

`Datos: Open-Meteo (CC BY 4.0)`.

## Non-interactive queries

Normal human-readable forecast:

```powershell
python -m surf_forecast forecast
```

Stable machine-readable output:

```powershell
python -m surf_forecast forecast --json |
  Set-Content -Encoding utf8 forecast.json
```

Force a network refresh:

```powershell
python -m surf_forecast forecast --refresh
```

Forbid network access:

```powershell
python -m surf_forecast forecast --stored-only
```

`--refresh` and `--stored-only` cannot be combined. Every command that emits a
new forecast first commits an immutable snapshot. Exit code `1` means a valid
but degraded forecast was emitted; it is not malformed output.

## Inspect source and snapshot traceability

Show current source state and exact model/grid metadata:

```powershell
python -m surf_forecast sources status
```

Use the snapshot ID shown in a forecast:

```powershell
python -m surf_forecast snapshots show SNAPSHOT_ID
python -m surf_forecast snapshots show SNAPSHOT_ID --json
python -m surf_forecast sources status --snapshot SNAPSHOT_ID
```

Snapshots are under `data/snapshots/YYYY/MM/`. Never edit these files. Each
contains stable identifiers, normalized inputs, requested/resolved coordinates,
source/model provenance, incidents, effective criteria/profile copies and
versions, emitted results, and a canonical result hash. Exact model run time is
stored as unavailable when the source did not provide it.

Replay the saved normalized inputs and embedded configuration:

```powershell
python -m surf_forecast snapshots replay SNAPSHOT_ID --json
```

A matching replay exits `0`; a canonical-result mismatch exits `5`. Showing or
replaying an existing snapshot never overwrites it or creates a replacement.

## Deterministic offline fixture replay

Fixture replay uses the normal acquisition-normalization-evaluation path but
replaces network responses. Always supply an aware reference time:

```powershell
python -m surf_forecast fixtures replay fixtures\normal `
  --now 2026-10-13T15:00:00-03:00 --json
```

`--now 2026-10-13T15:00:00` is invalid because it has no UTC offset. Fixture
replay writes a normally immutable snapshot marked `fixture_replay`.

Each fixture directory must include:

- source-like marine and wind JSON;
- source status/cache metadata;
- the effective criteria and profiles or their fixture references;
- a README section listing the expected human and machine outcomes.

These files are manual verification aids, not executable assertions.

## Manual verification checklist

Run each fixture command, compare its result with the expected outcome below,
inspect the Spanish TUI equivalent where applicable, and record the snapshot
ID. Do not change criteria merely to make a fixture pass.

### Size boundaries and quality floor

1. Replay exact estimated point sizes immediately below, exactly at, and
   immediately above `0.5`, `0.8`, `1.2`, and `1.8` m.
2. Expect the inclusive lower boundaries to map respectively to
   `small_but_surfable`, `fair`, `good`, and `very_good`; expect values just
   below them to remain in the preceding band.
3. At exactly `0.5` m with a plausible range wholly at/above `0.5`, expect
   surfable status. It must never become `no_surfable_waves`.
4. Apply one unfavorable quality factor to a supported `fair` or higher
   result. Expect no downgrade and a recorded reason.
5. Apply two unfavorable quality factors to a supported `0.5–0.8` m result.
   Expect at most one downgrade and a floor of `small_but_surfable`.
6. Replay a plausible range with `minimum_m < 0.5` and `maximum_m >= 0.5`.
   Expect state `uncertain`, a visible range, no forced condition grade, and no
   probability.

### Wind boundaries

1. Replay sustained speeds immediately below, exactly at, and immediately
   above `10`, `20`, and `35` km/h, plus `0`.
2. Expect `[0,10)` `light`, `[10,20)` `moderate`, `[20,35)` `strong`, and
   `[35,+∞)` `very_strong`.
3. Repeat with direction sectors on both sides of a sector boundary. Expect
   start-inclusive/end-exclusive classification.
4. Confirm that no wind result alone changes wave existence and that a single
   unfavorable factor does not lower the grade. Combined unfavorable factors
   lower quality by no more than one step.

### Cache boundary

Use the same response with download ages one second below, exactly at, and one
second above three hours.

- Below three hours: expect `fresh_cache`.
- At and above three hours: expect a live attempt in normal mode; if that
  attempt fails, expect explicit `stale_cache`, low confidence, incident, and
  exit code `1`.
- With `--refresh`: expect a live attempt even below three hours.
- With `--stored-only`: expect no live attempt.

### Local-time boundary

Replay with `--now` just before 20:00 and at/after 20:00
`America/Montevideo`.

- Before 20:00: today's best window may use only remaining complete hours
  within 06:00–20:00.
- At and after 20:00: expect today's state
  `analysis_window_completed`, no condition and no best window.
- In every case: expect exactly today through day +4, never an added day +5.

### Two-hour window precision

- With consecutive hourly slots: expect a best window only when at least 120
  contiguous minutes are supported inside 06:00–20:00.
- With fewer than two valid hours: expect no best window and never infer
  `no_surfable_waves`.
- With only three-hour samples: expect no silent interpolation and a window
  marked unavailable/Uncertain with reason `unsupported_temporal_resolution`.

### Source failures

- Marine failure with wind available: expect `incomplete_forecast`, source
  incident, low confidence, snapshot, and exit code `1`.
- Wind failure with marine available: expect the same degraded semantics; do
  not treat missing wind as favorable.
- All live sources fail with stale cache: expect visibly stale, low-confidence
  output and exit code `1`.
- All sources fail with no usable cache or stored snapshot: expect no forecast,
  error `forecast_unavailable`, exit code `3`, and no forecast snapshot.
- Stored-only with a prior snapshot: expect its exact age/origin and no network
  access.

### Confidence caps

- With the selected single NOAA/NCEP GFS model family, expect confidence no
  higher than `medium`.
- With every initial profile still `provisional`, expect confidence no higher
  than `medium`.
- With a user-marked calibrated complete profile, expect status `calibrated`
  and confidence still no higher than `medium` while only one model family is
  in use.
- With stale or required missing data, expect `low`.
- Confirm that multiple products from Open-Meteo do not appear as independent
  model confirmation.

### Snapshot immutability and reproducibility

1. Run the same fixture twice with the same `--now`. Expect two distinct
   snapshot IDs and two files with equivalent canonical results.
2. Capture the first file hash and modification time, then run show/replay and
   a later forecast. Expect both values to remain unchanged.
3. Replay the first snapshot. Expect exit `0` and the same canonical result
   hash using its embedded criteria/profile versions.
4. Change the current criteria version and replay the first snapshot. Expect
   the replay still to use the embedded old version.
5. Attempt a duplicate-path write. Expect a collision/persistence failure,
   never replacement of the original.
6. Simulate snapshot write failure. Expect no successful forecast response and
   exit code `4`.

## Live smoke check

After fixture verification, run one normal and one forced-refresh query. Check
that:

- the horizon contains five Uruguay-local dates;
- resolved marine/wind grid coordinates are visible;
- data age and valid/download times are visible;
- model run time is `unavailable`, not guessed;
- effective `k = 0.5`, range multipliers `0.5–0.7`, profile version, criteria
  version, incidents, confidence, and snapshot ID are visible;
- human text is Spanish while JSON property names and enums remain English;
- navigation stays responsive during loading and terminal resizing;
- the shared-grid warning is visible on the main result, not only in help;
- day headlines, best-peak highlighting, swell trend, and reason labels are
  visible;
- record elapsed time for the connected query and note whether it finished
  in under 30 seconds (SC-001). Do not treat a single slower run as a
  criteria change.

The first delivery is manually accepted only when every checklist item has an
observed result recorded against its fixture and unexpected differences are
resolved or explicitly documented.
