# Data Model: Personalized surf forecast for La Paloma

**Scope**: First delivery only (US1–US3 + FR-035 snapshots)  
**Canonical time**: UTC-aware instants; local decisions use
`America/Montevideo`  
**Canonical units**: meters, seconds, degrees true (direction *from*), km/h

## Modeling rules

1. Persisted identifiers and enum values are English `snake_case`.
2. Spanish labels are presentation data and never define persisted meaning.
3. Raw provider values, normalized values, and derived values remain separate.
4. Missing is `null` plus an explicit availability/incident; it is never zero.
5. Every mutable configuration entity has a version and content hash.
6. Every emitted query creates a new immutable snapshot.
7. No entity in this MVP contains observations, discrepancies, adjustments,
   reference forecasts, or days 5–10 analysis.

## Core configuration

### PeakProfile

Describes local knowledge for one surf peak.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `peak_id` | string | yes | Stable slug; unique, e.g. `la_aguada` |
| `name` | string | yes | Spanish proper name |
| `aliases` | string[] | no | Unique within profile |
| `zone_id` | string | yes | `la_paloma` in MVP |
| `latitude` / `longitude` | number | yes | WGS84 valid ranges |
| `orientation_deg` | number | yes | `[0, 360)` |
| `ideal_swell_sectors` | DirectionSector[] | yes | At least one, non-empty |
| `acceptable_swell_sectors` | DirectionSector[] | no | Estimated fields carry provenance |
| `blocked_swell_sectors` | DirectionSector[] | no | Must not overlap an ideal sector silently |
| `ideal_period_s` | NumericRange | yes | Positive, min ≤ max |
| `minimum_period_s` | number/null | no | Positive if present |
| `offshore_wind_sectors` | DirectionSector[] | no | Quality metadata, not profile completeness |
| `wind_shelter` | WindShelterRule[] | no | Direction sector + reduction class |
| `bottom_types` | enum[] | no | `sand`, `rock`, `sand_and_rock`, `unknown` |
| `status` | enum | derived/user | `incomplete`, `provisional`, `calibrated`. User may set `calibrated`; the system never writes it automatically |
| `estimated_fields` | string[] | yes | JSON paths of estimates |
| `profile_version` | semver string | yes | Changes whenever interpretation-relevant content changes |
| `schema_version` | string | yes | Profile document schema |
| `updated_at` | datetime | yes | UTC |

**Completeness**: valid location, orientation, at least one ideal swell sector,
and ideal period are essential. Missing any yields `incomplete`, even if the
file says `calibrated`. Complete essential fields with no user calibration
yield `provisional`. A user-marked `calibrated` value is honored only when
essential fields are complete.

### DirectionSector

| Field | Type | Rules |
|-------|------|-------|
| `start_deg` | number | `[0, 360)` |
| `end_deg` | number | `[0, 360)`; wrap-around is explicit |
| `label` | string/null | Optional human aid such as `S-SE` |

Boundaries are inclusive at start and exclusive at end.

### CriteriaSet

Versioned rules used for one evaluation.

| Field | Type | Initial value / rule |
|-------|------|----------------------|
| `criteria_version` | semver string | Required |
| `schema_version` | string | Required |
| `effective_from` | datetime | UTC |
| `point_k` | number | `0.5`, positive |
| `range_k_low` | number | `0.5` |
| `range_k_high` | number | `0.7`, `low ≤ point/high` |
| `surfable_threshold_m` | number | `0.5` |
| `size_bands` | GradeBand[] | Non-overlapping, contiguous above zero |
| `wind_speed_bands` | WindBand[] | `[0,10)`, `[10,20)`, `[20,35)`, `[35,∞)` |
| `max_quality_downgrade_steps` | integer | `1` |
| `quality_downgrade_min_unfavorable_factors` | integer | `2` |
| `wind_unfavorable_classes` | enum[] | `onshore`, `onshore_side` |
| `wind_unfavorable_intensities` | enum[] | `strong`, `very_strong` |
| `swell_trend_min_samples` | integer | `3` |
| `swell_trend_relative_change` | number | `0.10` |
| `swell_trend_absolute_change_m` | number | `0.1` |
| `minimum_surfable_grade` | enum | `small_but_surfable` for supported size ≥0.5 m |
| `analysis_start_local` | local time | `06:00` |
| `analysis_end_local` | local time | `20:00` |
| `minimum_window_minutes` | integer | `120` |
| `cache_fresh_minutes` | integer | `180` |
| `confidence_rules` | object | Versioned caps/degradation rules |
| `content_hash` | string | SHA-256 of canonical JSON |

### GradeBand

`minimum_m` is inclusive; `maximum_m` is exclusive or `null` for infinity.
Canonical grades:

1. `no_surfable_waves`
2. `small_but_surfable`
3. `fair`
4. `good`
5. `very_good`

`uncertain` and `incomplete_forecast` are evaluation states, not grades.

## Source and normalized data

### SourceDescriptor

| Field | Type | Example |
|-------|------|---------|
| `source_id` | string | `open_meteo_gfs_wave_025` |
| `provider` | string | `Open-Meteo` |
| `service` | string | `Marine API` |
| `dataset` | string | `NCEP GFS Wave 0.25°` |
| `model` | string | `ncep_gfswave025` |
| `model_family` | string | `noaa_ncep_gfs` |
| `independence_group` | string | `noaa_ncep_gfs` |
| `terms_url` | URI | Open-Meteo terms |
| `license` | string | `CC-BY-4.0` |
| `attribution` | string | Required display text |
| `native_temporal_resolution_minutes` | integer | `60` |
| `spatial_resolution_km` | number | Approximate, `25` |
| `model_run_time_available` | boolean | `false` |

### SourceFetch

Records one source attempt.

| Field | Type | Rules |
|-------|------|-------|
| `fetch_id` | UUID/string | Unique |
| `source_id` | string | FK-like reference |
| `requested_at` / `completed_at` | datetime | UTC |
| `request_url` | URI | No secrets |
| `requested_coordinate` | GeoPoint | Required |
| `resolved_coordinate` | GeoPoint/null | From response |
| `model_run_at` | datetime/null | Null for Open-Meteo response |
| `model_run_availability` | enum | `available`, `unavailable`, `unknown` |
| `valid_from` / `valid_to` | datetime/null | From returned hourly range |
| `status` | enum | `success`, `fresh_cache`, `stale_cache`, `failed` |
| `http_status` | integer/null | If available |
| `payload_sha256` | string/null | Raw cache payload hash |
| `incident_ids` | string[] | Any fetch incidents |

### RawCacheEntry

Replaceable cache object, not historical truth.

| Field | Type | Rules |
|-------|------|-------|
| `cache_key` | string | Hash of source + model + coordinate + variables |
| `fetched_at` | datetime | UTC |
| `expires_at` | datetime | `fetched_at + 3h` |
| `request` | object | Reconstructable request |
| `response` | object | Raw JSON payload |
| `payload_sha256` | string | Integrity |

### NormalizedMarineHour

| Field | Type | Availability |
|-------|------|--------------|
| `valid_at` | datetime | Required, UTC |
| `wave_height_m` | number/null | Raw model Hs |
| `wave_direction_deg` | number/null | Direction from |
| `wave_period_s` | number/null | Mean period |
| `swell_height_m` | number/null | Primary swell Hs |
| `swell_direction_deg` | number/null | Direction from |
| `swell_period_s` | number/null | Mean period |
| `wind_wave_height_m` | number/null | Local wind sea |
| `wind_wave_direction_deg` | number/null | Direction from |
| `wind_wave_period_s` | number/null | Mean period |
| `source_fetch_id` | string | Required |

### NormalizedWindHour

| Field | Type | Availability |
|-------|------|--------------|
| `valid_at` | datetime | Required, UTC |
| `speed_kmh` | number/null | Sustained 10 m |
| `direction_deg` | number/null | Direction from |
| `gust_kmh` | number/null | Source hourly gust definition |
| `source_fetch_id` | string | Required |

### NormalizedForecastBundle

Contains sorted, deduplicated marine and wind series, source descriptors,
fetch records, units, requested/resolved coordinates, normalization version,
and explicit missing-variable incidents. It covers exactly local today through
day +4 for the reference time.

## Evaluation

### QueryRequest

| Field | Type | Values |
|-------|------|--------|
| `mode` | enum | `normal`, `force_refresh`, `stored_only`, `fixture_replay` |
| `reference_time` | datetime | Explicit or system clock; UTC-aware |
| `timezone` | string | `America/Montevideo` |
| `peak_ids` | string[] | All five by default |
| `fixture_path` | path/null | Replay only |
| `output_mode` | enum | `tui`, `human`, `json` |

### SurfableSizeEstimate

| Field | Type | Derivation |
|-------|------|------------|
| `raw_hs_m` | number | Source wave height |
| `point_m` | number | `point_k × Hs` |
| `minimum_m` | number | `range_k_low × Hs` |
| `maximum_m` | number | `range_k_high × Hs` |
| `point_k` / `range_k_low` / `range_k_high` | number | Effective criteria |
| `method` | enum | `provisional_k_times_hs` |
| `calibrated` | boolean | Always `false` in MVP |

### WindAssessment

| Field | Type |
|-------|------|
| `relative_class` | enum: `offshore`, `offshore_side`, `cross_shore`, `onshore_side`, `onshore`, `unknown` |
| `intensity` | enum: `light`, `moderate`, `strong`, `very_strong`, `unknown` |
| `quality_class` | enum: `favorable`, `neutral`, `unfavorable`, `unknown` |
| `favorable` | boolean/null; true only when `quality_class` is `favorable` |
| `reasons` | ReasonCode[] |

### SlotEvaluation

One peak at one hourly slot.

| Field | Type |
|-------|------|
| `peak_id` / `valid_at` | string / datetime |
| `size` | SurfableSizeEstimate/null |
| `wind` | WindAssessment/null |
| `swell_favorability` | enum: `ideal`, `acceptable`, `blocked`, `unknown` |
| `period_favorability` | enum: `ideal`, `usable`, `below_minimum`, `unknown` |
| `swell_quality_class` / `period_quality_class` | `favorable`, `neutral`, `unfavorable`, `unknown` |
| `ceiling_grade` | grade/null |
| `unfavorable_factor_count` | integer; unknown factors excluded |
| `quality_downgrade_steps` | `0` or `1` |
| `condition_grade` | grade/null |
| `state` | `resolved`, `uncertain`, `incomplete_forecast` |
| `reason_codes` | ReasonCode[] |

Rules:

- A plausible size range crossing 0.5 m yields `uncertain`.
- A range wholly below 0.5 m yields `no_surfable_waves`.
- `quality_downgrade_steps` is `1` only when
  `unfavorable_factor_count >= quality_downgrade_min_unfavorable_factors`
  (initial 2). A single unfavorable factor does not lower the grade.
- A supported size at/above 0.5 m cannot be downgraded below
  `small_but_surfable`.
- Any required marine or wind input missing yields `incomplete_forecast`.

### BestWindow

| Field | Type | Rules |
|-------|------|-------|
| `start_at` / `end_at` | datetime | Local interval converted to UTC |
| `duration_minutes` | integer | At least 120 |
| `condition_grade` | grade | Best contiguous supported interval |
| `support` | enum | `hourly`, `derived`, `unsupported` |
| `slot_ids` | string[] | Consecutive source slots |

No interpolation is performed in MVP. Non-hourly input makes a precise
two-hour window unavailable/Uncertain. Fewer than two valid hours inside
the analysis window yields no best window and MUST NOT by itself produce
`no_surfable_waves`.

### SwellTrend

| Field | Type | Rules |
|-------|------|-------|
| `state` | enum | `building`, `peaking`, `dropping`, `steady`, `unsupported` |
| `sample_count` | integer | Hours used |
| `variable` | enum | `swell_height_m` or `wave_height_m` fallback |
| `method` | enum | `hourly_tercile_means` |

Requires at least three hourly samples in the analysis window. Change
threshold is the larger of 10% of the first-third mean and 0.1 m.

### DaySummary

| Field | Type |
|-------|------|
| `local_date` | date |
| `headline` | Spanish display string generated from codes |
| `headline_code` | stable English identifier |
| `size_range` | min/max estimated size among complete peaks, or null |
| `dominant_swell` | period and direction of the selected regional swell, or null |
| `wind_rotation` | start and end wind class/intensity in the analysis window |
| `swell_trend` | SwellTrend |
| `best_peak_ids` | complete peaks sharing the highest resolved grade; empty if none resolved |
| `peaks` | PeakDayForecast[] |

### PeakDayForecast

| Field | Type |
|-------|------|
| `peak_id` / `local_date` | string / date |
| `state` | `resolved`, `uncertain`, `incomplete_forecast`, `analysis_window_completed` |
| `condition_grade` | grade/null |
| `best_window` | BestWindow/null |
| `reference_slots` | SlotEvaluation[] for 06:00/12:00/18:00 when applicable |
| `confidence` | ConfidenceAssessment |
| `reason_codes` | ReasonCode[] |
| `highlighted` | boolean | True when `peak_id` is in the day's `best_peak_ids` |

At/after 20:00, today's state is `analysis_window_completed` with no grade or
window. The horizon still ends at day +4.

### ConfidenceAssessment

| Field | Type |
|-------|------|
| `level` | `high`, `medium`, `low` |
| `caps` | string[] |
| `degradations` | string[] |
| `components_available` | object |
| `explanation_code` | string |

In MVP, provisional profiles and the single model family cap confidence at
medium. A user-marked calibrated profile does not lift that cap while only one
model family is in use. Missing/stale/insufficient data reduces it to low;
absence never raises confidence.

### Incident

| Field | Type |
|-------|------|
| `incident_id` | string |
| `code` | stable enum identifier |
| `severity` | `info`, `warning`, `error` |
| `source_id` / `variable` | string/null |
| `occurred_at` | datetime |
| `details` | object with non-localized values |

## Presentation and persistence

### ForecastPresentation

Immutable resolved object consumed by both TUI and serializers:

- schema/version and snapshot ID
- reference/query time, mode, horizon
- day summaries and peak-day forecasts
- source statuses, data age, incidents, attribution
- `shared_regional_input` notice that all peaks share one marine and one wind cell
- effective profile/criteria versions and `k`/range
- stable reason codes plus Spanish labels generated at presentation time

No presentation adapter may recalculate a grade, confidence, or window.

### QuerySnapshot

| Field group | Contents |
|-------------|----------|
| Identity | `snapshot_id`, `schema_version`, `created_at`, content hash |
| Request | QueryRequest without local-only display preferences |
| Provenance | Source descriptors and fetches; requested/resolved coordinates |
| Inputs | Complete NormalizedForecastBundle used |
| Configuration | Effective CriteriaSet and PeakProfiles or exact immutable copies |
| Results | SlotEvaluation, PeakDayForecast, summaries, ConfidenceAssessment |
| Operations | Incidents, cache/stale decisions, application version |
| Attribution | Provider/license URLs and transformation notice |

The snapshot is self-contained for evaluation replay. Replaying creates a new
result for comparison only if explicitly requested; it never mutates the
original file.

## State transitions

### Query execution

```text
requested
  → loading
  → resolved | partial | unavailable | cancelled
  → snapshot_written (for every emitted resolved/partial forecast)
```

`unavailable` without an emitted forecast does not create a forecast snapshot;
the operational incident may be logged separately.

### Source fetch

```text
pending
  → live_success
  → fresh_cache
  → stale_cache
  → failed
```

Transitions follow fallback order; a later state does not erase earlier
attempt incidents.

### Profile

```text
incomplete → provisional → calibrated
```

The MVP ships the five known peaks as `provisional`. It may detect
`incomplete` and MUST honor a user-marked `calibrated` profile whose essential
fields are complete. It never promotes to `calibrated` automatically.
