# Data Model: 004-tui-visual-craft (display / view-model)

**Scope**: Display-only entities. **No** changes to forecast domain models or presentation 1.1.0 JSON schema.

Source of truth for payload fields remains the frozen presentation layer. This document describes **view-models and format rules** consumed by TUI components.

## Entities

### ThemeTokens

| Field | Type | Notes |
|-------|------|-------|
| canvas / body / muted / accent | color role | CSS variables or Textual token map |
| border_idle / border_focus | color role | Frame chrome |
| border_selected_card | color role | Active peak card |
| status_bg | color role | StatusBar |
| cond_good … cond_window | color role | FR-017 semantic map (graphic-layer §4.2) |

Validation: roles must remain distinguishable on dark backgrounds; color never sole signal.

### FrameModel

| Field | Type | Notes |
|-------|------|-------|
| title | str | Embedded in top border |
| focused | bool | Idle vs focus chrome |
| body | Widget/str | Inner content |
| width / height | int | Outer dimensions |

### BadgeModel

| Field | Type | Notes |
|-------|------|-------|
| text | str | Spanish FR-017 or data-state label |
| role | enum | cond-* or status |

### PeakCardModel

Derived from presentation `peak` dict via formatters:

| Field | Type | Notes |
|-------|------|-------|
| name | str | display_name |
| condition_label | str | FR-017 Spanish |
| condition_role | str | cond-* |
| size_text | str | e.g. `0,9–1,4 m` or `n/d` |
| period_text | str | e.g. `12 s` or `Período n/d` |
| wind_text | str | dir + intensity + km/h |
| score_glyphs | str | Unicode stars |
| score_num | str | `2,5` |
| best_of_day | bool | marker |
| selected | bool | ←→ selection |

### RatingHeroModel

| Field | Type | Notes |
|-------|------|-------|
| glyphs | str | Unicode stars matching score |
| numeric | str | `N,N / 5` |
| caption | str \| None | from presentation |
| absent_reason | str \| None | single “Sin valoración” path |

### EvolutionRowModel

| Field | Type | Notes |
|-------|------|-------|
| local_hhmm | str | `HH:MM` |
| size_text | str | formatted |
| wind_text | str | formatted |
| condition_label | str | FR-017 |
| condition_dot | str | `●` + role color |

### BestWindowModel

| Field | Type | Notes |
|-------|------|-------|
| start_hhmm / end_hhmm | str | local |
| wide | bool | ≥6h or full 06–20 band |
| label | str | normal vs “Ventana amplia (día completo)” |
| duration_secondary | str \| None | humanized only if not wide-led |

### AnalysisLineModel

| Field | Type | Notes |
|-------|------|-------|
| kind | fact \| interpretation \| limitation | from sentences[] |
| text | str | Spanish |
| prefix | str | ≈ / ◇ / ! |

## Relationships

```text
presentation payload 1.1.0
        │ formatters (pure)
        ▼
 PeakCardModel / RatingHeroModel / EvolutionRowModel / BestWindowModel
        │ components
        ▼
 Frame / PeakCard / RatingHero / EvolutionTable / BestWindowCallout
        │ screens
        ▼
 View A / View B
```

## State transitions (UI only)

| State | Trigger | Result |
|-------|---------|--------|
| day_index | ↑↓ / ListView | Rebind View A day content; peak_index → 0 |
| peak_index | ←→ | Reselect PeakCard chrome; no day focus steal |
| View B open | Enter | Push PeakDetailScreen(day_index, peak_index) |
| View B close | Esc | Pop; restore day+peak indices |
| tech_expanded | D | Toggle TechnicalDetails |
| width class | on_resize | narrow / medium / wide grid + legend visibility |

## Validation rules (display)

See [contracts/display-hygiene.md](./contracts/display-hygiene.md) and graphic-layer §5.

- Meters: 1 decimal, comma separator  
- Period: integer or `n/d`; never fake `0 s` for null  
- Scores: Unicode stars + matching numeric  
- Confidence: Spanish labels in primary UI  
- Times: `HH:MM` in primary panels  
