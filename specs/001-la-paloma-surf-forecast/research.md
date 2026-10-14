# Phase 0 Research: Personalized surf forecast for La Paloma

**Date**: 2026-10-13  
**Scope**: First delivery only (US1–US3 + immutable query snapshots)  
**Verification convention**: `VERIFIED` means checked against an official
source or a live response on the date above. `UNVERIFIED` means the plan must
not depend on the claim.

## 1. Forecast data source

### Decision

Use Open-Meteo as the only access service in the MVP, with explicit model
selection:

- Marine: `https://marine-api.open-meteo.com/v1/marine`,
  `models=ncep_gfswave025`, `cell_selection=sea`.
- Wind: `https://api.open-meteo.com/v1/gfs`, GFS seamless atmospheric data.
- Marine variables:
  `wave_height`, `wave_direction`, `wave_period`,
  `swell_wave_height`, `swell_wave_direction`, `swell_wave_period`,
  `wind_wave_height`, `wind_wave_direction`, `wind_wave_period`.
- Wind variables:
  `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`.
- Request five forecast days and UTC timestamps; convert with
  `America/Montevideo` locally.

### Verified evidence

- `VERIFIED`: The official Marine API documents significant total, wind-wave,
  and swell height/direction/period as hourly variables.
- `VERIFIED`: NCEP GFS Wave 0.25° is global, approximately 25 km, hourly,
  updated every 6 hours, and covers up to 16 forecast days.
- `VERIFIED`: GFS Wave 0.16° only extends to 15°S, so it does not cover La
  Paloma at about 34.7°S.
- `VERIFIED`: The weather API provides hourly 10 m wind speed/direction and
  gusts.
- `VERIFIED`: A live five-day marine request on 2026-10-13 returned 120
  non-null hourly values for every selected marine variable.
- `VERIFIED`: A live five-day GFS wind request returned 120 hourly values for
  all selected wind variables.
- `VERIFIED`: Marine/wind response fields include valid timestamps, returned
  grid coordinates, units, timezone, and UTC offset.
- `VERIFIED`: The documented/observed response does not include exact model
  initialization time. It must remain `null`/`unavailable`, not be inferred
  from the six-hour update schedule.

### Rationale

This is the smallest viable integration: JSON over HTTP, no API key, hourly
output, all MVP variables, and enough horizon. Explicit model IDs avoid the
untraceable composition of `best_match`. It is still one provider and one
NOAA model family, so it cannot support independent confirmation and all
initial peak profiles cap confidence at medium.

### Alternatives considered

1. **NOAA NOMADS directly** — `VERIFIED` global GFS Wave and GFS atmospheric
   filters expose the needed wave and wind fields and model cycles. Rejected
   for MVP because GRIB2 subsetting/parsing adds a native/scientific dependency
   or custom decoding, URL/file-cycle logic, and substantially more failure
   handling.
2. **Copernicus Marine Global Wave Forecast** — `VERIFIED` free registration,
   global wave product, primary/secondary swell partitions, and 10-day
   forecast. Rejected for MVP because it requires an account/toolbox and
   NetCDF/Zarr-oriented access. Official pages also expose both “3-hourly”
   service fields and an “hourly” metadata description; this temporal
   ambiguity is unnecessary when GFS Wave is explicitly hourly.
3. **Open-Meteo `best_match`** — rejected because the selected underlying model
   can vary and the response does not provide enough run/model provenance for
   immutable reproducibility.

### Sources

- https://open-meteo.com/en/docs/marine-weather-api
- https://open-meteo.com/en/docs/gfs-api
- https://github.com/open-meteo/open-meteo/blob/main/openapi/marine.yml
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=gfswave
- https://nomads.ncep.noaa.gov/gribfilter.php?ds=gfs_0p25_1hr
- https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_WAV_001_027/description
- https://help.marine.copernicus.eu/en/articles/7949409-copernicus-marine-toolbox-introduction

## 2. Cost, terms, attribution, and retention

### Decision

Use the Open-Meteo free non-commercial endpoint. Show attribution in the TUI
footer/help and human-readable CLI output, and retain attribution plus
transformation metadata in every snapshot.

### Verified evidence

- `VERIFIED`: Personal/non-commercial use is free and needs no API key.
- `VERIFIED`: Limits are 600 calls/minute, 5,000/hour, 10,000/day, and
  300,000/month.
- `VERIFIED`: Data obtained through the API is provided under CC BY 4.0;
  attribution, a license link, and indication of modifications are required.
- `VERIFIED`: CC BY permits copying, redistribution, transformation, and
  derived works. Local raw caching and normalized snapshot retention are
  therefore allowed when attribution is retained.
- `VERIFIED`: NOAA server information is generally public domain unless
  annotated otherwise; attribution is requested and modified data must not be
  presented as official NOAA material.
- `UNVERIFIED`: No contractual uptime or long-term schema stability guarantee
  exists for the free endpoint. Treat availability and future compatibility as
  operational risks.

### Retention policy

- Raw API payloads live only in the replaceable 3-hour cache.
- Immutable snapshots retain the normalized inputs actually used, request URL
  without secrets, provider/service/dataset/model identifiers, resolved grid
  coordinates, units, valid/download timestamps, attribution, and a
  transformation marker.
- This is sufficient to replay the evaluation without retaining redundant raw
  arrays forever.

### Sources

- https://open-meteo.com/en/terms
- https://open-meteo.com/en/licence
- https://open-meteo.com/en/pricing
- https://ospo.noaa.gov/Organization/About/use.html

## 3. Sampling coordinates and model resolution

### Decision

Use one configurable regional marine anchor and one configurable regional wind
anchor for all five peaks:

- Marine request: `-34.70, -54.10`, `cell_selection=sea`.
- Wind request: `-34.66, -54.18`.

Always store and display both requested and returned grid coordinates. Peak
differences come from explicit peak profiles, not distinct model cells.

### Verified evidence

- `VERIFIED`: The live explicit GFS Wave request resolved the marine point to
  `-34.75, -54.0` with elevation 0 and returned non-null marine values. This is
  an API-selected sea cell.
- `VERIFIED`: The live GFS wind request resolved to approximately
  `-34.61763, -54.140625`, elevation 8 m.
- `VERIFIED`: GFS Wave 0.25° has about 25 km spatial resolution, much coarser
  than the few kilometers separating the five peaks.
- `UNVERIFIED`: The selected marine cell is the optimal representation of each
  break's offshore exposure. It is merely a valid regional offshore sample and
  must be corrected only through later observations, not assumed precise.

### Rationale

Per-peak API calls would create false precision and extra quota/cache
complexity. One regional sample plus versioned peak profiles directly matches
the specification.

## 4. TUI framework

### Decision

Use Textual 8.x for the full-screen TUI. Keep Textual imports exclusively in
`presentation/tui`; application/domain layers return immutable presentation
models and know nothing about widgets.

### Verified evidence

- `VERIFIED`: Textual 8.2.8 was the current PyPI release observed on
  2026-10-13; it is MIT licensed and supports Python >=3.9,<4.
- `VERIFIED`: Official documentation supports Windows and specifically states
  that Windows Terminal runs Textual applications.
- `VERIFIED`: Textual workers run asynchronous or thread work without blocking
  message processing; blocking standard-library HTTP can use `thread=True`.
- `VERIFIED`: Thread workers must post messages or use `call_from_thread`
  rather than mutate widgets directly.

### Rationale

Textual supplies panels, focus/navigation, resizing, styles, status/footer
widgets, and worker lifecycle. Building these directly would be more complex
and less maintainable.

### Alternatives considered

- **prompt_toolkit** — `VERIFIED` full-screen layouts, key bindings, and native
  asyncio support. Rejected because it is a lower-level toolkit and would
  require more custom widget/layout/state code for the selected dashboard.
- **Raw ANSI/curses** — rejected. It would add Windows compatibility and
  terminal-control maintenance and conflicts with the “justified TUI library”
  preference.

### Sources

- https://pypi.org/project/textual/
- https://textual.textualize.io/getting_started/
- https://textual.textualize.io/guide/workers/
- https://python-prompt-toolkit.readthedocs.io/en/stable/pages/full_screen_apps.html
- https://python-prompt-toolkit.readthedocs.io/en/stable/pages/advanced_topics/asyncio.html

## 5. HTTP and concurrency

### Decision

Use `urllib.request` with explicit timeout inside concurrent Textual thread
workers. Marine and wind fetches run concurrently. Each gets a 10-second
timeout and at most one retry after a bounded short delay.

### Rationale

Two simple GET integrations do not justify another HTTP dependency.
Concurrency keeps the TUI responsive and makes two timeout/retry paths fit
inside the 30-second result target.

### Verified evidence

- `VERIFIED`: `urllib.request.urlopen(..., timeout=...)` supports timeout for
  blocking HTTPS operations.
- `VERIFIED`: Textual thread workers support cancellation and safe UI message
  delivery.

### Alternatives considered

- **httpx** — better async ergonomics, but unnecessary for two endpoints and
  would add a dependency solely for transport.
- **Sequential requests** — simpler code but unnecessarily adds source
  latencies and makes the 30-second target less robust.

## 6. Local storage

### Decision

Use plain JSON files:

- `config/peaks.json` and `config/criteria.json`: versioned human-editable
  configuration.
- `data/cache/{source-key}.json`: replaceable raw response and cache metadata.
- `data/snapshots/YYYY/MM/{snapshot-id}.json`: one immutable normalized query
  snapshot.
- `fixtures/**`: deterministic source-like input and expected-outcome
  documentation.

Write a temporary file in the target directory, flush and `fsync`, then commit
with `os.replace`. Snapshot creation fails if the final ID already exists;
snapshots are never updated in place.

### Rationale

The MVP has one writer, tiny data volumes, no relational querying, and
append-only history. JSON is inspectable and keeps configuration editable.

### Alternatives considered

- **SQLite** — atomic and suitable for future queries/relationships, but adds
  schema migrations and opaque manual inspection before those benefits are
  needed. Revisit when observations and performance reporting require joins.
- **JSONL** — compact append-only history, but one interrupted append can
  complicate recovery and individual snapshots are less directly inspectable.

### Verified evidence

- `VERIFIED`: Python `os.replace` supports cross-platform replacement and is
  available on Windows. Keeping temporary and final paths in the same directory
  avoids cross-filesystem behavior.

## 7. Timezone and reference time

### Decision

Use aware UTC instants internally and `ZoneInfo("America/Montevideo")` for all
local-day/window decisions. Declare the first-party `tzdata` package because
Windows normally lacks a system IANA database. The CLI/replay contract accepts
an explicit ISO-8601 `--now`.

### Verified evidence

- `VERIFIED`: Python `zoneinfo` falls back to the first-party `tzdata` package.
- `VERIFIED`: Python documentation recommends declaring `tzdata` for Windows;
  without either system data or the package, `ZoneInfo` raises
  `ZoneInfoNotFoundError`.
- `VERIFIED`: Open-Meteo can return `America/Montevideo` and `-10800`, but the
  application still converts from UTC locally so historical/future policy is
  not tied to a fixed offset assumption.

### Source

- https://docs.python.org/3/library/zoneinfo.html

## 8. Provisional size uncertainty

### Decision

Version the following initial policy:

- Point estimate: `estimated_size_m = 0.5 × Hs`.
- Range: `[0.5 × Hs, 0.7 × Hs]`.
- Range wholly below 0.5 m: `no_surfable_waves`.
- Range crossing 0.5 m: `uncertain`.
- Range wholly at/above 0.5 m: grade ceiling from the point estimate, with
  `small_but_surfable` as the minimum.

### Rationale

The user selected 0.5 as the conservative initial point factor and identified
0.6–0.75 as the observed range implied by other surf presentations. Using 0.7
as a configurable upper policy factor protects the threshold from a hard false
negative while remaining simple. It is not a statistical interval, probability,
or physical calibration. Both factors and the resulting range are visible.

### Alternatives considered

- **Point estimate only** — rejected because it creates false precision at the
  0.5 m boundary.
- **Symmetric absolute margin** — rejected because one absolute margin scales
  poorly across small and large Hs.
- **Model spread** — deferred; the MVP intentionally selects one model family
  and cannot claim independent spread.

## 8b. Quality downgrade

### Decision

Count swell direction, period, and wind. Downgrade one step only when at
least two are unfavorable, using the classification table in `spec.md` and
`data-model.md`. One unfavorable factor is recorded, not applied. Unknown
is omitted.

### Rationale

The specification forbids a single factor from being decisive and forbids
falling below Small but surfable when size is supported at or above 0.5 m.
Requiring two unfavorable factors is the smallest explicit rule that matches
that constraint without inventing weights.

### Alternatives considered

- **Any single unfavorable factor** — rejected; contradicts “not decisive
  alone.”
- **Weighted score** — rejected for the MVP as an uncalibrated composite.

## 8c. Swell trend

### Decision

Use hourly tercile means of `swell_height_m`, falling back to
`wave_height_m`, with a 10% or 0.1 m change threshold and a middle-third
peak test. Otherwise `unsupported`.

### Rationale

Open-Meteo GFS Wave is hourly, so a three-sample trend is supported without
interpolation. Coarser or short series must not invent building or dropping.

## 9. Verification strategy

### Decision

No automated tests or CI. Provide deterministic JSON fixtures, explicit
reference time, commands that replay the normal application path, and a manual
matrix with exact expected outcomes.

### Required fixture groups

- Every size and wind boundary, including exactly 0.5 m.
- Quality-floor downgrade and range crossing 0.5 m.
- Cache ages immediately below/at/above 3 hours.
- Reference times immediately before/at/after 20:00 local.
- Hourly two-hour window and unsupported coarse input.
- Marine failure, wind failure, both fail, stale cache, no cache.
- One-source/provisional profile confidence caps.
- Snapshot creation, collision refusal, immutability, and replay.

### Risk acceptance

The absence of executable assertions increases regression risk. The accepted
mitigation is reproducible fixtures plus expected outcomes and snapshot/criteria
versions. This is a deliberate user decision allowed by Constitution Principle
XI, not a claim that tests have no value.

## 10. Language and stable identifiers

### Decision

- TUI/help/human text: Spanish.
- JSON property names and enum identifiers: stable English `snake_case`.
- Optional `*_label` fields: Spanish display strings.
- Snapshots: identifiers only, plus `schema_version`; no localized text as
  persisted meaning.

### Rationale

Machine contracts remain stable while the first presentation meets FR-043 and
future adapters can localize independently.

## Resolved unknowns

All Technical Context unknowns are resolved. Items marked `UNVERIFIED` above
are explicit product limitations, not hidden planning assumptions.
