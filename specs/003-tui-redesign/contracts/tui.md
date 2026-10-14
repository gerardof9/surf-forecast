# TUI Contract — Daily surf report redesign

**Adapter**: Textual full-screen terminal UI  
**Library**: Textual 8.x (existing)  
**Language**: Spanish human-facing text; English machine identifiers in payload only  
**Visual reference**: `specs/003-tui-redesign/mock2.png` (hierarchy, not pixel parity)  
**Spec**: `../spec.md`

## Launch

Unchanged:

```powershell
py -m surf_forecast
py -m surf_forecast tui
```

Startup shows the shell immediately and runs a normal forecast query in a worker.

## Adapter boundary

The TUI consumes `ForecastPresentation.payload` (`schema_version` `1.1.0`). It MUST NOT:

- fetch/normalize provider data;
- compute grades, sizes, confidence, best windows, day/peak ratings, or narratives;
- write snapshots;
- reintroduce an interactive profiles browser.

All query actions call existing application services (`run_forecast` modes).

## View A — Daily surf report

### Composition (wide)

```text
┌ SURF · LA PALOMA ─ horizonte ─ Actualizado (datos) UYT ─ estado ─────────────┐
│ DÍAS          │  Título día                                                  │
│ (focus)       │  ANÁLISIS DEL DÍA                                            │
│ rating chip   │  VALORACIÓN DEL DÍA  ★…  n,n / 5  [caption]                  │
│ legend        │  PICOS DEL DÍA  (cards/rows ranked)                          │
│               │  [optional narrow: legend moves here / Help]                 │
├───────────────┴──────────────────────────────────────────────────────────────┤
│ footer hints: ↑↓ día  ←→ pico  Enter detalle  R  o  ?  Q                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Required content

- Title `SURF · LA PALOMA`
- Selected weekday/date, horizon today+4
- Meteorological update/age distinct from query execution time
- `day_analysis.text` (scrollable; no silent truncation)
- `day_rating` or `Sin valoración` + reason
- Neutral section `PICOS DEL DÍA` (or confirmed synonym); never “recomendados”
- Cards: display_name, FR-017 label, size range m, period s, wind, peak_rating when present, best_of_day marker
- Compact day list with focus on load

### Narrow terminals

Stack vertically: header → days → analysis → rating → peaks. Scroll; no overlap.

## View B — Peak detail

### Composition

```text
┌ ← Pico · fecha · ventana 06:00–20:00 UYT · condición · tamaño ───────────────┐
│ Condiciones / viento / swell / confianza / peak_rating                         │
│ Evolución (evolution_samples)                                                  │
│ MEJOR VENTANA ESTIMADA | o mensaje de ausencia                                 │
│ Peak analysis (si existe)                                                      │
│ [DETALLES TÉCNICOS]  ← collapsed by default; D toggles                         │
├────────────────────────────────────────────────────────────────────────────────┤
│ Esc volver  D técnicos  ←→ pico?  ?  Q                                         │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Technical details (expanded)

Source/model, update/age, raw Hs vs derived size, k/range, profile/criteria versions, confidence reasons, snapshot id, shared-cell warning. No third diagnostic screen.

## Key bindings

| Key | Context | Action |
|-----|---------|--------|
| `↑` / `↓` | View A | Change day (initial focus on day list) |
| `←` / `→` | View A | Move among spot cards |
| `Enter` | View A spot | Open View B |
| `Esc` | View B | Back to View A (same day) |
| `D` | View B | Toggle technical details |
| `R` | A/B | Force refresh (existing rules) |
| `o` | A/B | Stored-only query |
| `?` | A/B | Help/About |
| `Q` | A/B | Quit |

Removed: `p` profiles screen.

## Display honesty

- Never show English enums as primary labels
- Never present incomplete as “few waves”
- Color secondary to text
- Stars must match numeric score; numeric always shown
- Hs ≠ surfable size (technical section / help)

## Workers / responsiveness

Unchanged from `001`: network/filesystem off UI thread; cancel/replace refresh workers; quit/help remain active while loading.
