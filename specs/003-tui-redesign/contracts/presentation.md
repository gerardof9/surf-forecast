# Presentation Contract — Report fields (`schema_version` 1.1.0)

**Consumers**: TUI (redesign), CLI/JSON, immutable snapshots  
**Producer**: `build_presentation` (extended) / report helpers — **not** Textual widgets  
**Engine**: unchanged evaluation thresholds

## Additive day fields

| Field | Required | Notes |
|-------|----------|-------|
| `day_rating` | no | Object or omit/null when no resolved peak |
| `day_rating_absent_reason` | when no rating | Spanish reason |
| `day_analysis` | yes | `{text, sentences?, supported, method}` |
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

`score` MUST equal `glyph_steps`. `score` MUST be in 0.5 steps on [1.0, 5.0].

## Additive peak fields

| Field | Required | Notes |
|-------|----------|-------|
| `condition_label` | yes | FR-017 Spanish |
| `display_name` | yes | Proper capitalization |
| `peak_rating` | no | Same map when resolved |
| `peak_analysis` | no | When template can emit ≥1 evidence sentence |
| `best_of_day` | yes | bool |
| `evolution_samples` | yes | Array 0–3 (may be empty) |

Full `reference_slots` remain for verification and best-window provenance.

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

- Changing grade thresholds or `k` formulas
- Embedding free-form LLM text
- Removing snapshot immutability
