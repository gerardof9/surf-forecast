# Contract: TUI chrome & components

**Feature**: `004-tui-visual-craft`  
**Binding detail**: [`../graphic-layer.md`](../graphic-layer.md)  
**Code home**: `src/surf_forecast/presentation/tui/`

## Module boundaries

| Module | May import | Must not |
|--------|------------|----------|
| `formatters.py` | stdlib, typing | Textual, domain.evaluation |
| `theme.py` | stdlib | domain |
| `components/*` | Textual, formatters, theme | domain.evaluation, forecast_service |
| `screens.py` | components, formatters, app bindings | re-classify grades |
| `app.py` | screens, application services | paint Frame internals |

## Required components (v1)

| Component | Responsibility | Key FR |
|-----------|----------------|--------|
| `Frame` | Unicode title-in-border panel; focus chrome | FR-G11 |
| `Badge` / `StatusPill` | FR-017 or data-state label + role color | FR-G06 |
| `PeakCard` | Structured peak metrics card | FR-G01, FR-G03 |
| `RatingHero` | Stars + numeric + caption | FR-G05 |
| `AnalysisPanel` | sentences[] kind styling | FR-G01 |
| `EvolutionTable` | Sampled HH:MM rows | FR-G04 |
| `BestWindowCallout` | Local times; wide-window honesty | FR-G14 |
| `TechnicalDetails` | Collapsed default; toggle D | FR-G04 |
| `StatusBar` | Footer bar, not a Frame | FR-G07 |

## Keyboard contract (View A)

| Key | Behavior |
|-----|----------|
| ↑↓ | Change day (focus stays on day list) |
| ←→ | Change active peak selection chrome |
| Enter | Open View B for active peak |
| Esc (View B) | Return preserving day+peak |
| D | Toggle technical details (View B) |
| R / o / ? / Q | Existing refresh / stored / help / quit |

## Layout breakpoints

| Width | View A peaks | Legend |
|-------|--------------|--------|
| ≥ 130 | up to 5 columns | visible |
| 90–129 | 2–3 columns | hidden → Help |
| &lt; 90 | 1 column | Help |

## Non-goals

- Changing presentation JSON schema  
- Engine thresholds  
- Pixel-perfect modelo clone / Nerd Font icons  
