# Data Model: Surfer-friendly TUI redesign

**Feature**: `003-tui-redesign`  
**Depends on**: `001` domain entities (`ForecastResult`, `DaySummary`, `PeakDayForecast`, `SlotEvaluation`, …) unchanged.

This feature extends the **shared presentation payload** and adds pure derived report objects. It does not mutate engine evaluation thresholds.

## Schema

- Current emitted presentation: `schema_version = "1.0.0"`
- Redesign target: `schema_version = "1.1.0"` (additive fields below)

## Entities

### ReportPresentation (shared payload root)

Extends `001` presentation with:

| Field | Type | Rules |
|-------|------|-------|
| `schema_version` | string | `"1.1.0"` for redesigned emitters |
| `query.reference_time` | datetime | Query execution / analysis reference (existing) |
| `query_times.executed_at_local` | string | Uruguay-local display of query execution |
| `data_times.meteorological_updated_at_local` | string/null | Best-effort data update/age display; null if unknown |
| `data_times.label` | string | Distinguishes data update from query time in UI copy |
| `days[]` | DayReport | See below |

### DayReport (extends day object)

| Field | Type | Rules |
|-------|------|-------|
| Existing `001` day fields | … | Preserved (`local_date`, `state`, `headline`, `best_peak_ids`, `swell_trend`, `wind_rotation`, `peaks`) |
| `day_rating` | DayRating/null | Present only if ≥1 resolved-grade peak; else null |
| `day_rating_absent_reason` | string/null | Required when `day_rating` is null |
| `day_analysis` | DayAnalysis | Always present; may be limitation-only |
| `display_title` | string | e.g. `Miércoles 14/10` |

### DayRating

| Field | Type | Rules |
|-------|------|-------|
| `score` | number | ∈ {1.0, 1.5, …, 5.0}; v1 proposed map uses whole points only |
| `source_peak_id` | string | Best resolved peak used |
| `caption` | string/null | Optional qualitative caption consistent with score |
| `method` | string | e.g. `best_resolved_grade_map_v1` |
| `glyph_steps` | number | Same numeric value for star renderer |

**Validation**: `glyph_steps == score`. Never emit score for uncertain/incomplete/analysis_window_completed peaks as source.

### PeakReport (extends peak object)

| Field | Type | Rules |
|-------|------|-------|
| Existing `001` peak fields | … | Preserved |
| `condition_label` | string | FR-017 Spanish label (replaces old Spanish map) |
| `display_name` | string | Capitalized profile name (`La Aguada`, …) |
| `peak_rating` | PeakRating/null | Same map as day rating when resolved; else null |
| `peak_analysis` | PeakAnalysis/null | Present when ≥1 evidence-bound sentence possible |
| `peak_analysis_absent_reason` | string/null | When omitted |
| `best_of_day` | bool | True iff this peak is the day rating source / top resolved highlight |
| `evolution_samples` | EvolutionSample[] | 0–3 sampled slots for View B |
| `reference_slots` | array | Full hourly slots retained for verification / best window |

### PeakRating

Same shape as `DayRating` but `source_peak_id` is self.

### DayAnalysis / PeakAnalysis

| Field | Type | Rules |
|-------|------|-------|
| `text` | string | Spanish multi-sentence or short limitation |
| `sentences` | object[] | Optional structured parts: `{kind, text}` where `kind` ∈ `fact` \| `interpretation` \| `limitation` |
| `supported` | bool | False when limitation-only / insufficient |
| `method` | string | e.g. `template_v1` |

**Validation**: No sentence may introduce facts not backed by payload/profile fields. `interpretation` kind only for profile-derived exposure notes.

### EvolutionSample

| Field | Type | Rules |
|-------|------|-------|
| `band` | enum | `morning` \| `midday` \| `afternoon` |
| `local_hour` | string | `HH:MM` |
| `size_point_m` | number/null | |
| `wind_dir_label` | string/null | |
| `wind_speed_kmh` | number/null | if available in slot/presentation enrichment |
| `wind_intensity` | string/null | |
| `condition_label` | string/null | FR-017 or state label |
| `incomplete_or_uncertain` | bool | |

**Proposed band rule** (confirm before implement): first slot in `[06:00,11:00)`, `[11:00,15:00)`, `[15:00,20:00]` within analysis window.

## Label map (FR-017)

| Machine id | Spanish label |
|------------|---------------|
| `very_good`, `good` | Buena oportunidad |
| `fair` | Surfeable |
| `small_but_surfable` | Variable |
| `no_surfable_waves` | Pocas olas |
| `uncertain` | Incierto |
| `incomplete_forecast` | Pronóstico incompleto |
| `analysis_window_completed` | Ventana de análisis finalizada |

Do not show `resolved` as a primary user condition; prefer condition label when present.

## Proposed score captions (optional; confirm)

| Score | Caption |
|------:|---------|
| 5.0 | Condiciones muy favorables en el mejor pico evaluado |
| 4.0 | Buenas condiciones en el mejor pico evaluado |
| 3.0 | Condiciones surfeables, con limitaciones |
| 2.0 | Oportunidad limitada / variable |
| 1.0 | Pocas olas en el mejor pico evaluado |

## Relationships

```text
ForecastResult (engine, unchanged)
    └── build_presentation / build_report_presentation
            ├── DayRating ← best resolved PeakDayForecast.condition
            ├── DayAnalysis ← day facts + profiles + templates
            └── PeakReport[]
                    ├── PeakRating ← peak.condition
                    ├── PeakAnalysis ← peak facts + profile
                    └── EvolutionSample[] ← sample(reference_slots)
```

## State rules

- Incomplete profile / missing essentials → peak not recommended; no peak_rating; card shows incomplete/not evaluable.
- Analysis window completed (today) → no best window; day/peak ratings absent if no resolved grades; analysis states limitation.
- Mixed day → day_rating from best resolved only; weaker cards keep honest labels.
