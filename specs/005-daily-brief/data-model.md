# Data Model: 005-daily-brief

**Date**: 2026-10-15  
**Schema**: presentation `1.2.0`  
**Source of truth for evaluation**: existing `DaySummary` / `PeakDayForecast` / `BestWindow` / `SurfGrade` (unchanged formulas)

## Entities (presentation)

### DayBrief

Primary home/CLI/JSON day object (one per presented day).

| Field | Type | Rules |
|-------|------|--------|
| `local_date` | string `YYYY-MM-DD` | Local UYT calendar day |
| `label` | string | `"Hoy"` \| `"Mañana"` (relative to report reference) |
| `display_title` | string | Existing weekday + date title |
| `condition` | string \| null | Peak/day grade id or day-level resolved condition |
| `condition_label` | string | FR-017 Spanish label (day-facing) |
| `headline` | string | One short Spanish line |
| `body` | string | Multi-sentence plain Spanish analysis |
| `caution` | string \| null | Optional single honesty caution (not the lead voice) |
| `height` | object \| null | See HeightSummary; null if no worth spot |
| `go_window` | object \| null | See GoWindow; null if no worth spot |
| `worth_spots` | WorthSpot[] | 0–3 items; fair+ only; best-first |
| `empty_spots_message` | string \| null | Required copy when `worth_spots` empty |

Derived from: engine day + ranked peaks + `build_day_brief` narrative.

### WorthSpot

| Field | Type | Rules |
|-------|------|--------|
| `peak_id` | string | Stable id |
| `display_name` | string | Beach name |
| `condition` | string | Grade id ≥ fair |
| `condition_label` | string | Spanish label |
| `reason_short` | string \| null | Optional ≤ ~8 words |

### HeightSummary

From **best** worth-spot’s derived size only.

| Field | Type | Rules |
|-------|------|--------|
| `minimum_m` | number | Derived |
| `maximum_m` | number | Derived |
| `display` | string | e.g. `0,8–1,2 m` (comma decimal) |
| `kind` | `"derived"` | Never claim offshore Hs as breaking |

### GoWindow

From **best** worth-spot’s `best_window` only. (Wire field name: `go_window`.)

| Field | Type | Rules |
|-------|------|--------|
| `start_local` | string | `HH:MM` |
| `end_local` | string | `HH:MM` |
| `wide` | boolean | True if ≥6 h or full analysis day |
| `display` | string | Human phrase; if `wide`, honest “ventana amplia…” + times |
| `source_peak_id` | string | Best worth-spot id |

### ForecastPresentationPayload (1.2.0)

| Field | Change vs 1.1.0 |
|-------|-----------------|
| `schema_version` | `"1.2.0"` |
| `days` | Length **2** (Hoy, Mañana); each day embeds `brief` (DayBrief fields may be nested under `brief` or flattened — contract picks nested `brief`) |
| `days[].peaks` | **Not required** for compliance; TUI MUST NOT render a five-peak grid |
| `days[].day_analysis` | **Removed/replaced** by `brief` narrative (`headline`/`body`) |

## Worth filter algorithm

```text
candidates = peaks where condition in {fair, good, very_good}
sort by (GRADE_RANK desc, peak_rating.score desc if any, peak_id asc)
worth_spots = candidates[:3]
best = worth_spots[0] if any else None
height, go_window ← from best only
```

## Relationships

```text
ForecastResult (engine)
  └── DaySummary[] (may be >2)
        └── PeakDayForecast[] + BestWindow
              │
              ▼
        build_presentation (slice first 2 days)
              │
              ▼
        DayBrief × 2  →  TUI DayBriefCard / CLI / JSON
```

## Validation rules

- `len(days) == 2` on successful normal reports (when engine has ≥2 days; if engine has 1, second day is explicit incomplete — edge case in spec)
- `len(worth_spots) ≤ 3`
- Every worth spot grade ≥ fair
- If `worth_spots` empty ⇒ `height is null` and `go_window is null`
- No Tiempo/Energía fields
