# Presentation Contract — Report fields (`schema_version` 1.1.0)

**Consumers**: TUI (redesign), CLI/JSON, immutable snapshots  
**Producer**: `build_presentation` (extended) / report helpers — **not** Textual widgets  
**Engine**: unchanged evaluation thresholds

## Additive day fields

| Field | Required | Notes |
|-------|----------|-------|
| `day_rating` | no | Object or omit/null when no resolved peak |
| `day_rating_absent_reason` | when no rating | Spanish reason |
| `day_analysis` | yes | `{text, sentences, supported, method}` — `sentences[]` items `{kind, text}` with `kind` ∈ `fact` \| `interpretation` \| `limitation` |
| `display_title` | yes | Localized weekday/date |

### `day_rating`

```json
{
  "score": 4.0,
  "source_peak_id": "la_aguada",
  "caption": "Buenas condiciones en el mejor pico evaluado",
  "method": "best_resolved_grade_map_v1",
  "glyph_steps": 4.0
}
```

`score` MUST equal `glyph_steps`. Scale admits 0.5 steps on [1.0, 5.0]; **v1 emitters MUST use whole points only**. `method` MUST be `best_resolved_grade_map_v1` (ordinal `SurfGrade` map — not a multi-factor formula).

## Additive peak fields

| Field | Required | Notes |
|-------|----------|-------|
| `condition_label` | yes | FR-017 Spanish |
| `display_name` | yes | Proper capitalization |
| `peak_rating` | no | Same map when resolved |
| `peak_analysis` | no | When template can emit ≥1 evidence sentence |
| `best_of_day` | yes | bool |
| `wind_dir_label` | no | Pass-through when available |
| `wind_speed_kmh` | no | Pass-through of engine slot wind speed (km/h); null if unknown — never invent from intensity bands |
| `wind_intensity` | no | Engine intensity class when available |
| `evolution_samples` | yes | Array 0–3 (may be empty); each sample may include `wind_speed_kmh` / `wind_dir_label` / `wind_intensity` |

Full `reference_slots` remain for verification and best-window provenance. Slot wind display fields are presentation pass-through of engine inputs; evaluation thresholds stay unchanged.

## Dual timestamps

Presentation MUST expose both:

- query/reference execution time (existing `query.reference_time` + local display helper);
- meteorological data update/age when known (`sources[].downloaded_at` / age), labeled so an older update on a later selected day is not misread as a same-day model refresh.

Unavailable model run times stay `No disponible` / null — never invented.

## Compatibility

- New queries emit `1.1.0`.
- Engine replay fixtures from `001` remain valid for evaluation paths.
- Redesigned TUI/CLI human summary SHOULD target `1.1.0` fields; degrade gracefully if a field is missing during transition.

## Non-goals

- Changing grade thresholds, wind-band thresholds, or `k` formulas
- Re-deriving day/peak scores from size/wind/period in the presentation layer
- Embedding free-form LLM text
- Removing snapshot immutability
