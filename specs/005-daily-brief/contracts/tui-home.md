# Contract: TUI home (two DayBrief cards)

**Feature**: `005-daily-brief`  
**Depends on**: [presentation-1.2.0.md](./presentation-1.2.0.md)

## Layout

```text
┌─ Header (dual timestamps + status) ─────────────────────┐
│                                                         │
│  ┌─ DayBriefCard Hoy ──┐  ┌─ DayBriefCard Mañana ─┐   │
│  │ condition pill       │  │ condition pill        │   │
│  │ height (or n/d)      │  │ height (or n/d)       │   │
│  │ headline             │  │ headline              │   │
│  │ body (scroll if need)│  │ body                  │   │
│  │ go_window display    │  │ go_window / empty     │   │
│  │ worth spot chips     │  │ worth spot chips      │   │
│  └──────────────────────┘  └───────────────────────┘   │
│                                                         │
└─ StatusBar (shortcuts; attribution) ────────────────────┘
```

Narrow terminal (&lt; ~90 cols): stack cards vertically.

## MUST

- Show exactly two day cards from `payload["days"]`
- Bind fields only from `day["brief"]` (+ header timestamps from payload)
- Reuse Frame/Badge/formatters hygiene (comma meters, `HH:MM`, wide-window label)
- Update StatusBar/Help: no “Enter detalle”, no “←→ pico”, no leyenda FR-017 rail

## MUST NOT

- Day ListView / 5-day rail
- Section title `PICOS DEL DÍA`
- PeakCard grid of all peaks
- `LEYENDA` rail / `LEGEND_LINES` on home
- Push `PeakDetailScreen` / View B on any key
- Show Tiempo or Energía blocks

## Navigation

- Esc / quit / help as today
- Optional: focus toggle Hoy↔Mañana; **no** peak selection model
- Enter does **not** open detail

## Components

| Widget | Role |
|--------|------|
| `DayBriefCard` | NEW — one day brief |
| `Frame` | Optional chrome around card |
| `Badge` / condition pill | Condition label |
| `StatusBar` | Shortcuts |
| `PeakCard`, `EvolutionTable`, `BestWindowCallout` (detail), `TechnicalDetails` | Unused on home; may remain in tree unused or deleted in implement tasks |

## Smoke assertions

- After load: two widgets/cards identifiable as Hoy and Mañana
- Screen text does not contain `PICOS DEL DÍA` or `LEYENDA`
- App has no live route that mounts peak detail after keypress Enter on home
