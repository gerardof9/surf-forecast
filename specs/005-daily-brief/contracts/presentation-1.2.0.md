# Contract: Presentation schema 1.2.0 (DayBrief)

**Feature**: `005-daily-brief`  
**Supersedes for consumers**: presentation `1.1.0` day-board shape (5 days, `day_analysis` kinds, full peak grid expectation)

## Compatibility

| Consumer | Requirement |
|----------|-------------|
| TUI | MUST render from `days[].brief` only for home |
| CLI | MUST print the same brief fields |
| JSON | MUST emit `schema_version: "1.2.0"` with two days |

Breaking: clients that assume `len(days)==5` or `day_analysis.sentences[].kind` MUST update.

## Top-level

```json
{
  "schema_version": "1.2.0",
  "overall_status": "complete",
  "snapshot_id": "...",
  "query": { "timezone": "America/Montevideo", "...": "..." },
  "query_times": { "executed_at_local": "..." },
  "data_times": { "meteorological_updated_at_local": "...", "label": "..." },
  "criteria": { "criteria_version": "..." },
  "sources": [],
  "days": [ /* exactly two Day objects when horizon available */ ],
  "profiles": [],
  "incidents": [],
  "attribution": {},
  "shared_regional_input": {}
}
```

## Day object

```json
{
  "local_date": "2026-10-15",
  "display_title": "Miércoles 15/10",
  "state": "resolved",
  "brief": {
    "label": "Hoy",
    "condition": "fair",
    "condition_label": "Surfeable",
    "headline": "Oleaje usable; mejor temprano.",
    "body": "Condiciones razonables en La Paloma. ...",
    "caution": null,
    "height": {
      "minimum_m": 0.8,
      "maximum_m": 1.2,
      "display": "0,8–1,2 m",
      "kind": "derived"
    },
    "go_window": {
      "start_local": "06:00",
      "end_local": "09:00",
      "wide": false,
      "display": "Mejor entre 06:00–09:00",
      "source_peak_id": "la_aguada"
    },
    "worth_spots": [
      {
        "peak_id": "la_aguada",
        "display_name": "La Aguada",
        "condition": "good",
        "condition_label": "Buena oportunidad",
        "reason_short": "Mejor ventana"
      }
    ],
    "empty_spots_message": null
  }
}
```

### Empty worth-spots example

```json
{
  "brief": {
    "label": "Mañana",
    "condition": "no_surfable_waves",
    "condition_label": "Pocas olas",
    "headline": "Día flojo para surfar.",
    "body": "...",
    "caution": null,
    "height": null,
    "go_window": null,
    "worth_spots": [],
    "empty_spots_message": "Ningún pico claro para ir."
  }
}
```

## Invariants (checkers MUST enforce)

1. `schema_version == "1.2.0"`
2. On a normal complete report with ≥2 engine days: `len(days) == 2`
3. Each day has `brief` with `headline`, `body`, `worth_spots` (array), `label` in `{Hoy, Mañana}`
4. `len(worth_spots) ≤ 3`
5. Every `worth_spots[].condition` ∈ `{fair, good, very_good}`
6. If `worth_spots` empty ⇒ `height is null` ∧ `go_window is null` ∧ `empty_spots_message` non-empty
7. If `worth_spots` non-empty ⇒ `height` and `go_window` present; `go_window.source_peak_id == worth_spots[0].peak_id`
8. `go_window.display` MUST NOT lead with a large minute count; MUST include `HH:MM` when times exist
9. No required `Tiempo` / `Energía` fields
10. Advisory copy MAY recommend when/where; MUST NOT claim guaranteed surfable waves or safety

## Explicitly out of contract

- Peak detail / evolution samples as interactive requirements
- FR-017 legend rail
- Five comparable peak cards on home
