# TUI Contract

**Adapter**: Textual full-screen terminal UI  
**Language**: Spanish human-facing text; stable English internal identifiers  
**Scope**: US1–US3, source status, and immutable snapshot visibility only

## Launch

```powershell
py -m surf_forecast
py -m surf_forecast tui
```

Both commands open the same full-screen application. Startup immediately
displays the shell and begins a normal forecast query in a worker; the terminal
must never appear frozen while data loads.

## Shared adapter boundary

The TUI receives `ForecastPresentation` objects from application services. It
MUST NOT:

- fetch or normalize provider data directly;
- calculate size, quality, confidence, or best windows;
- write snapshots directly;
- translate Spanish labels back into machine identifiers.

All actions dispatch application commands also exposed by the non-interactive
adapter.

## Main forecast screen

### Layout

```text
┌ Surf Forecast La Paloma ─ query time ─ data freshness ─ confidence ┐
│ Days (left)      │ Peaks (center)        │ Selected detail (right) │
│ today … day +4   │ condition / range     │ swell / wind / reasons  │
│                  │ confidence / state    │ best window / versions  │
├──────────────────┴───────────────────────┴─────────────────────────┤
│ source status / incidents / snapshot ID / Open-Meteo attribution  │
├────────────────────────────────────────────────────────────────────┤
│ key hints and transient status/help                               │
└────────────────────────────────────────────────────────────────────┘
```

The implementation may stack the detail panel below the lists on narrow
terminals, but it must retain all information and keyboard access. At 80×24,
use compact labels and scrolling rather than clipping values silently.

### Required content

- Local query/reference time and mode.
- Today through day +4, with today marked `Ventana de análisis finalizada`
  when applicable.
- Every complete peak; incomplete profiles listed separately with missing
  fields.
- Day headline, wind rotation, swell trend, and highlighted best peaks.
- Condition grade or explicit `Incierto` / `Pronóstico incompleto`.
- Estimated point and range, raw Hs, swell period/direction, wind
  speed/direction/class/intensity.
- Short Spanish reason labels from stable `reason_codes`.
- Best supported window or why it is unavailable.
- Confidence and each cap/degradation reason.
- Visible notice that all peaks share one regional marine cell and one
  regional wind cell.
- Data age and live/fresh-cache/stale-cache/failed state per source.
- Requested and resolved model coordinates.
- Provider/service/dataset/model identity and missing model run time as
  `No disponible`.
- Effective criteria/profile versions, effective `k` and range factors.
- Snapshot identifier.
- `Datos: Open-Meteo (CC BY 4.0)`; Help/About shows provider and license URLs.

## Profile screen

Read-only in the MVP.

- List five profiles with name/alias/status/version.
- Show essential and optional fields.
- Mark estimated/unknown fields explicitly.
- Show all validation errors and warnings.
- Never promote a profile to calibrated.
- Provide the path to the editable JSON configuration.

## Help/About overlay

Contains:

- Key bindings.
- Meanings of conditions, uncertainty, confidence, stale data, and incomplete
  forecast.
- Warning that model Hs is not beach breaking height and `k × Hs` is
  provisional.
- Warning that the five peaks share coarse regional model inputs.
- Open-Meteo and license URLs.
- Application/schema/criteria versions.

## Key bindings

| Key | Context | Action |
|-----|---------|--------|
| `↑`/`↓` or `k`/`j` | lists | Move selection |
| `←`/`→` or `h`/`l` | main | Move between day/peak/detail panels |
| `Tab` / `Shift+Tab` | all | Cycle focus |
| `Enter` | list | Open/focus selected day or peak detail |
| `Esc` | overlay/detail | Return/close |
| `r` | main | Force refresh after confirmation/status feedback |
| `o` | main | Run stored-only query |
| `p` | main | Open profile screen |
| `s` | main | Focus source/incident status |
| `?` or `F1` | all | Help/About |
| `q` | all | Quit; cancel active worker cleanly |

Repeated refresh actions cancel/replace an earlier refresh worker rather than
allow out-of-order results to overwrite newer state.

## Display states

### Loading

- Shell and previous result remain navigable.
- Status says `Actualizando datos…`.
- Per-source progress is visible.
- Refresh is not duplicated; quit/help/navigation remain active.

### Complete

- All required inputs available.
- Condition/confidence presented normally.
- Snapshot ID appears after persistence succeeds.

### Partial failure

- Valid source data remain visible.
- Failed source and missing fields are explicit.
- A condition requiring missing marine or wind data becomes
  `Pronóstico incompleto`.
- Confidence never increases.

### Fresh cache

- Show `Datos guardados` and exact age (<3 h).
- Display original fetch and current query times.

### Stale fallback

- Persistent high-visibility `Datos antiguos` indicator.
- Show exact age and failed refresh incident.
- Confidence is low.

### All sources unavailable

- If stale data or a prior snapshot is available, offer stored-only display.
- Otherwise show `No hay datos suficientes para generar un pronóstico`.
- Never fabricate a condition.

### Uncertain threshold

- Show range crossing 0.5 m.
- State `Incierto`.
- Explain that `k × Hs` is provisional and not a probability.

### Analysis window completed

- Today remains in the five-date list.
- No condition or best window is shown for today.
- Tomorrow through day +4 remain unchanged.

### Snapshot failure

An evaluated forecast is not presented as durably recorded until snapshot
commit succeeds. Show a persistence error and allow retry; do not silently
claim reproducibility.

## Responsiveness contract

- Network and blocking file operations run outside the Textual message loop.
- Thread workers post messages or use `call_from_thread`; they do not mutate
  widgets directly.
- Resize, navigation, help, and quit remain responsive during work.
- Cancelled/older workers cannot replace results from a newer query.

## Localization contract

- All visible prose and condition labels are Spanish.
- Internal enum identifiers remain English and are never displayed without a
  Spanish label where user-facing.
- Color is supplementary; every status also has text and/or a symbol.
