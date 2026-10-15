# Contract: Display hygiene formatters

**Feature**: `004-tui-visual-craft`  
**Implements**: graphic-layer §5, FR-G02, FR-G05, FR-G14, SC-004, SC-005

## Pure functions (required)

All live in `src/surf_forecast/presentation/tui/formatters.py` (names may vary; behaviors MUST match).

| Function | Input | Output rule |
|----------|-------|-------------|
| `format_meters_range` / point | float \| None | One decimal, comma; `n/d` if missing |
| `format_period_s` | float \| None | Integer `N s` or `Período n/d`; **never** `0 s` for None |
| `format_wind` | dirs/intensity/kmh | Compact Spanish fragments; int km/h |
| `format_score_num` | float | `N,N` one decimal max |
| `format_stars` | float \| None | `★` `◐` `☆` only — no ASCII `*`/`-` |
| `format_hhmm_local` | ISO or datetime | `HH:MM` |
| `format_confidence` | engine level | Spanish (`media`, …) — not raw `medium` |
| `format_best_window` | window dict | Returns label + `HH:MM–HH:MM`; if wide (≥6h or full 06–20 band) → “Ventana amplia (día completo)” without leading huge minute count |

## Anti-patterns (MUST fail smoke / review)

| Pattern | Example |
|---------|---------|
| Raw multi-decimal float in primary UI | `1,3579999999999999` |
| ASCII star bar | `***--` |
| ISO-first best window | `2026-10-16T06:00:00-03:00` as primary |
| Fake zero period | `0 s` when period is null |
| Doubled absent rating copy | `Sin valoración` twice |

## Smoke assertions (`scripts/check_tui_visual_smoke.py`)

1. Load fixture `fixtures/normal` into app (`auto_query_on_mount=False`).  
2. Show payload → pause → `←→` optional → `action_open_detail` → pause → assert no `app._exception`.  
3. Esc/back → no exception.  
4. Collect primary Static/Frame text from View A and View B; assert no regex `\d+[.,]\d{4,}`.  
5. If any peak/day score present, assert `★` or `☆` appears and `***` star-bar does not.  
6. Exit 0 on pass.

Does **not** replace manual VS-* screenshot gates.
