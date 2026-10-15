# Surf Forecast — Graphic Layer Specification

**Feature**: `004-tui-visual-craft`  
**Version**: 1.0.0  
**Status**: Binding implementation guide  
**Created**: 2026-10-15  

**Binding visual references** (composition & hierarchy; numeric values illustrative only) — all under this feature:

| Artifact | Role |
|----------|------|
| `references/modelo.png` | Binding composition for View A + View B |
| `references/mock2.png` | Same binding composition family |
| `references/detalle_capture_0.png` | Current View A — **non-compliant** baseline |
| `references/detalle_capture_1.png` | Current View B — **non-compliant** baseline |
| `references/tui_actual.png` | Older non-compliant baseline |
| `references/diagnostico2.pdf` | Product diagnosis (content + hierarchy) |
| `references/detalle.pdf` | Source PDF of current TUI captures |

**Quality bar (non-pixel clones)**: LazyGit, btop, K9s, Wireshark — density, framed regions, semantic color, focus chrome, scannable columns.  
**Product rules (frozen, do not reopen in this feature)**: presentation schema 1.1.0, FR-017 vocabulary, honesty/narrative rules, and View A/B semantics already delivered. This document **replaces only the graphic/TUI rendering layer**, not the forecast engine or presentation payload contract.

**Code home**: `src/surf_forecast/presentation/tui/` (+ display formatters). Domain / evaluation / Open-Meteo MUST NOT change for visual reasons.

---

## 0. Purpose

This document defines the **graphic layer**: theme, layout geometry, component catalog, focus system, number formatting, and visual acceptance gates so the TUI reads as a **professional daily surf report**, not a diagnostic log dump.

**Acceptance rule**: code that mounts the correct section titles but fails the wireframes, component catalog, or screenshot gates in this document is **not done**.

---

## 1. Diagnosis — why the current TUI fails

Evidence: `detalle_capture_0.png`, `detalle_capture_1.png`, contrast with `modelo.png`.

### 1.1 Root cause (not libraries)

Textual is sufficient. The failure is craft:

| Failure | Symptom in captures | Model expectation |
|---------|---------------------|-------------------|
| Sections ≠ components | `Static` multiline strings in thin cyan boxes | Composed cards, badges, tables, hero rating |
| Layout betrayal | View B = vertical scroll of boxes; peak grid max 2 cols | View A: 5-card row; View B: 3-column board |
| No design system | Ad-hoc cyan / default Textual tokens | Role-based palette + focus chrome |
| Diagnostic copy elevated | Limitations / window-completed dominate | Facts first; limitations secondary |
| Broken display hygiene | `1,3579999999999999 m`, `0 s`, `***--`, ISO `840 min` | Rounded metrics, Unicode stars, local HH:MM |
| Empty space | Wide panels with 3–6 lines and black void | Density budget like LazyGit/btop |
| Weak scan path | Read paragraphs to compare peaks | Color badge → size → period → wind → score |

### 1.2 What 003 already solved (do not re-argue)

- Shared presentation 1.1.0 (analysis sentences, day/peak ratings, evolution samples, FR-017).
- View A / View B product structure and keyboard paths.
- Honesty: no invented meteorology; scores are indicators.

### 1.3 What 004 must solve

- Graphic system + component implementation fidelity to `modelo.png`.
- Display formatting layer (never leak raw floats / machine ISO into primary UI).
- Visual acceptance by screenshot, not by “widgets exist”.

---

## 2. Design intent

### 2.1 Product surface

A **terminal daily surf report** for La Paloma:

1. How is the selected day looking?
2. Which peaks look better / worse (comparable cards)?
3. When during the day (sampled evolution + best window when engine-supported)?

### 2.2 Visual personality

- Dark terminal canvas; cool cyan/blue accent (ocean), not purple-glow / generic AI theme.
- High information density without clutter.
- **Framed panels** with titles in the top border (LazyGit / K9s style).
- Semantic color for FR-017 conditions (reinforcement only; never the only signal — text label always present).
- StatusBar as dedicated footer (not a framed content panel).

### 2.3 Explicit non-goals

- Pixel-perfect clone of `modelo.png` (rounded GUI pills, photo-real icons).
- Decorative wave / map-pin / compass iconography from the mock; Nerd Font requirements.
- GUI frameworks (Qt, Electron, web).
- Replacing Textual.
- Changing engine thresholds, `k`, or inventing swell/wind.
- Binding to mock numeric values in `modelo.png`.

Approximate in terminal Unicode + Textual CSS what the mock communicates: hierarchy, cards, badges, columns, density.

**Clarified (2026-10-15) — iconography**: Minimal set only — rating stars, condition `●`, best-of-day `★`, optional reliable wind arrows. No wave/pin/compass decorative icons; no Nerd Font dependency.

---

## 3. Architecture of the graphic layer

```text
presentation payload 1.1.0  (domain — unchanged contract)
            │
            ▼
   display formatters     ← round numbers, local times, stars, badges labels
            │
            ▼
   theme tokens (CSS)     ← roles: border idle/focus, body, muted, cond-*, rating
            │
            ▼
   components             ← Frame, Badge, DayChip, PeakCard, RatingHero, EvolutionTable, …
            │
            ▼
   screens View A / B     ← layout composition only (no domain logic)
```

### 3.1 Module targets (implementation mapping)

| Concern | Suggested path |
|---------|----------------|
| Theme / CSS variables & global rules | `presentation/tui/theme.py` or dedicated block in `app.py` CSS — prefer extract |
| Display formatters (pure) | `presentation/tui/formatters.py` (or tighten `widgets.py`) |
| Frame / Badge / PeakCard / … | `presentation/tui/components/` |
| View A / View B composition | `presentation/tui/screens.py` |
| App shell, bindings, workers | `presentation/tui/app.py` |

### 3.2 Hard rule

Widgets MUST NOT re-classify surf conditions. They only render presentation fields. Formatters may round/display; they MUST NOT invent missing meteorology.

---

## 4. Design tokens (mandatory semantic palette)

Colors are **roles**. Exact hex may be tuned; roles MUST remain distinguishable on black/dark backgrounds. Prefer Textual `$success` / `$warning` / `$error` mapped to these roles or explicit hex in CSS.

### 4.1 Chrome & text

| Role | Intent | Suggested treatment |
|------|--------|---------------------|
| `canvas` | App background | Near-black / deep navy |
| `body` | Primary readable text | Light warm or cool white |
| `muted` | Secondary / hints / empty | Mid gray |
| `accent` | Brand titles, section chrome | Cyan ≈ `#00d4ff` / `#00a2fa` |
| `border-idle` | Unfocused frame | Dim gray |
| `border-focus` | Focused frame / selected card | Bright cyan/blue; title same color |
| `border-selected-card` | Selected peak card | Heavy / double weight + boost fill |
| `status-bg` | StatusBar background | Distinct inverted / muted bar |
| `warning-box` | Shared-grid / provisional callout | Yellow/amber border or fg |
| `banner` | Day-level window-completed notice | Warning color; one line; not per-card spam |

### 4.2 Condition semantics (FR-017)

| FR-017 label | Role id | Color intent |
|--------------|---------|--------------|
| Buena oportunidad | `cond-good` | Green |
| Surfeable | `cond-fair` | Yellow / gold |
| Variable | `cond-variable` | Orange |
| Pocas olas | `cond-poor` | Red |
| Incierto | `cond-uncertain` | Purple / muted violet |
| Pronóstico incompleto | `cond-incomplete` | Gray |
| Ventana de análisis finalizada | `cond-window` | Gray (state, not grade) |

Badge background MAY be a dim tint of the role; foreground MUST keep contrast. Under `NO_COLOR` / limited terminals: bold / underline / prefix glyph (`●`) + full Spanish label — never color-only.

### 4.3 Rating glyphs

| Score step | Glyph contract |
|------------|----------------|
| Full star | `★` (U+2605) |
| Half star | `◐` or `⯨` — pick one and use consistently; MUST match numeric score |
| Empty | `☆` (U+2606) |
| Forbidden | ASCII `*`, `-`, `#` as star substitutes in primary UI |

Numeric form ALWAYS shown beside glyphs: `2,5 / 5` (comma decimal, Spanish locale).

---

## 5. Display formatting contract (hygiene)

Primary UI MUST apply these rules. Violations seen in `detalle_capture_1.png` are **defects**.

| Field | Rule | Reject |
|-------|------|--------|
| Size meters | 1 decimal, comma: `0,9–1,4 m` | Raw float `1,3579999999999999` |
| Period | Integer seconds or `n/d`; never `0 s` unless engine truly returned 0 — if missing, `Período n/d` | Showing `0 s` for null/absent |
| Wind speed | Integer `km/h` | Excess decimals |
| Scores | One decimal max, comma: `2,5` | `2.500000` |
| Local clock | `HH:MM` UYT in evolution / best window | Full ISO-8601 in primary panels |
| Best window duration | Tight windows: human `2 h` / `120 min` OK secondary; wide windows: honesty label, not `840 min`-led | Dominating with `(840 min)` for full-day spans as if tight |
| Timestamps in header | Split labels: `Datos meteorológicos:` vs `Consulta:` | Single ambiguous “Datos …” |
| Confidence | Spanish map of engine level (`media`, etc.) | Raw `medium` English in primary UI |

Technical details (collapsed) MAY show higher precision and ISO if labeled as technical.

---

## 6. Component catalog (mandatory)

Shared-container layouts with only floating cyan titles are **non-compliant**. Prefer bordered frames.

### 6.1 `Frame`

**Clarified (2026-10-15)**: Implementation MUST be a **custom `Frame` widget** that paints Unicode box-drawing with the title embedded in the top border (same approach as db-log-explorer / LazyGit). Approximating frames with Textual CSS `border` plus an inner or floating title is **non-compliant** for primary content regions.

```text
╭─ ANÁLISIS DEL DÍA ──────────────────────────────╮
│ body…                                           │
╰─────────────────────────────────────────────────╯
```

| Property | Rule |
|----------|------|
| Border | Full 4 sides; Unicode rounded corners (`╭╮╰╯`); custom widget, not CSS-only |
| Title | Embedded in top border (painted into the top edge string) |
| Focus | `border-focus` + title same color; idle uses `border-idle`; focused top edge MAY use `═` |
| Padding | ≥ `(0, 1)` |
| Empty | In-frame muted message + next action hint |

**Rejected**: title above a bare region with only a horizontal rule; text on raw canvas outside frames (except StatusBar / Header brand line as specified); CSS `border: solid/tall/round` as the sole frame chrome for catalog `Frame` regions.

### 6.2 `StatusPill` / `Badge`

Compact label for data-state or FR-017 condition.

```text
┌ Datos disponibles ┐     or     [ Buena oportunidad ]
```

- Always includes readable Spanish text.
- Color role from §4.
- Used in header (data state) and on every `PeakCard` / View B summary.

### 6.3 `HeaderBar` (View A)

Two logical rows max:

1. Brand `SURF · LA PALOMA` + horizon (`Pronóstico hoy + 4 días` / date range).
2. `Datos meteorológicos: …` · `Consulta: …` · `StatusPill`.

Must not dump a single undifferentiated cyan paragraph.

### 6.4 `DayRail` + `DayChip`

Left column:

- Title `DÍAS` in frame or section chrome.
- Each chip: `Mié 14/10` + score `3,5` or `—`.
- Selected: solid selection background (`border-focus` / boost).
- Compact weekday abbreviations (as current `format_day_chip`).

Optional under-rail: mini condition legend **or** defer full legend to right rail / Help (see layout).

### 6.5 `RatingHero`

For `VALORACIÓN DEL DÍA` and peak rating block:

```text
★★★◐☆
3,5 / 5
Condiciones buenas, con limitaciones
```

- Large visual weight vs body text.
- Caption optional; MUST match documented mapping when present.
- `Sin valoración` once + reason once — no redundant doubled phrases.

### 6.6 `AnalysisPanel`

Renders `sentences[]` with **kind** distinction:

| kind | Visual prefix / style |
|------|------------------------|
| `fact` | `≈` or muted bullet + body color |
| `interpretation` | `◇` + slightly accented |
| `limitation` | `!` + warning color |

Order: facts and interpretations first; limitations last or in a thinner warning strip.  
**Forbidden**: filling the panel with only limitation lines when facts exist in the payload.

Day-level `analysis_window_completed` → single `Banner` above analysis, not repeated on every peak card.

### 6.7 `PeakCard` (critical)

Not a multiline `Static` dump. Structured regions:

```text
╭─ La Aguada ★ ─────────────╮
│ [Buena oportunidad]       │
│ 0,9–1,2 m   ·  10–12 s    │
│ Viento S-SE  12 km/h      │
│ ★★★★☆  4,0                │
╰───────────────────────────╯
```

Required fields when available from presentation:

- Name (+ best-of-day marker on exactly one resolved best peak)
- FR-017 badge
- Size range m
- Period s
- Wind dir + intensity/speed
- Peak 1–5 when resolved; else honest absent (`Sin nota` / state label)

Selected card: stronger border + background boost; keyboard `←→` moves selection; `Enter` opens View B.

**Clarified (2026-10-15)**: Primary focus stays on the **day list**. Peak cards are **selection-highlighted**, not a separate focus trap / Tab cycle among cards. This preserves 003’s “focus starts on days” rule while still making the active peak obvious.

### 6.8 `PeakGrid`

- Wide (≥ 130 cols): **up to 5 columns** (one row of peaks) when 5 peaks — match model density.
- Medium (90–129): 2–3 columns.
- Narrow (< 90): 1 column stack; scroll OK.

`grid-size: 2` as a hard ceiling on wide terminals is **non-compliant**.

### 6.9 `LegendRail`

Right rail on wide terminals:

- Condition dots + FR-017 labels + score bands (4–5, 3, 2, 1, uncertain…).
- Metric legend (size / period / wind) in one short block.
- Shared-grid note (warning style).

On medium: may hide; content available via `?` Help.  
On narrow: Help only.

### 6.10 `EvolutionTable` (View B)

Columnar, header row, 3 sampled bands:

```text
Hora    Tamaño   Viento              Condición
06:00   1,0 m    S 18 km/h           ● Surfeable
12:00   …
18:00   …
```

Condition column uses colored `●` + label. Alignment via fixed columns / Textual DataTable / monospace pads — not “looks like a table by accident”.

### 6.11 `BestWindowCallout`

- Show only when engine provides `best_window`.
- Primary line: local `HH:MM–HH:MM` (+ duration humanized when the window is genuinely tight).
- Emphasized border (warning/accent).
- **Clarified (2026-10-15)**: If duration ≥ 6 h **or** the window covers the full analysis band (06:00–20:00 UYT), still show the callout with honest label **“Ventana amplia (día completo)”** (or equivalent) + `HH:MM–HH:MM`. MUST NOT lead with huge minute counts (e.g. `840 min`) as the primary emphasis. Do not hide the callout solely because the span is wide.

### 6.12 `TechnicalDetails`

- Collapsed by default; toggle `D`.
- Collapsed label without Textual markup hazards: `DETALLES TÉCNICOS (plegado — D)`.
- Expanded: models, Hs→derived, ages, snapshot id, shared-cell warning.
- MUST NOT dominate first paint of View B.

### 6.13 `StatusBar`

- Full width, dock bottom, **not** a `Frame`.
- Grouped shortcuts: `Navigate: ↑↓ ←→ Enter` · `Data: R o` · `D Técnicos` · `?` · `Q`.
- Distinct background.
- Context line may include short status; attribution `Open-Meteo` may live here or muted footer secondary — must not crowd primary shortcuts.

### 6.14 `HelpModal`

- Overlay; dim workspace behind.
- Includes legend + how-to-read when right rail hidden.
- Esc closes.

### 6.15 Naming collision ban

Never name user methods `_render` on Textual `Widget` / `Static` subclasses (collides with internal Visual `_render`). Use `_populate`, `_apply`, `_refresh_content`.

---

## 7. Layout contracts

### 7.1 Minimum terminal

- Supported: **100×30** preferred; **80×24** minimum with degradation (§6.8, legend→Help).
- Below 80×24: show blocking message to enlarge terminal (optional but recommended).

### 7.2 View A — Daily report (binding wireframe)

```text
╭─ SURF · LA PALOMA · Pronóstico hoy + 4 días ──────── [Datos disponibles] ─╮
│ Datos meteorológicos: 14/10 23:15 UYT  ·  Consulta: 15/10 11:40 UYT         │
╰────────────────────────────────────────────────────────────────────────────╯

╭─ DÍAS ────╮ ╭─ VIERNES 16/10 ──────────────────────────────────────────────╮╭─ LEYENDA ─╮
│ Mié 14/10 │ │ (! banner ventana finalizada — at most one line, if needed)  ││ ● Buena…  │
│ Jue 15/10 │ │╭─ ANÁLISIS DEL DÍA ─────────────╮╭─ VALORACIÓN ──────────────╮││ ● Surf…   │
│▸Vie 16/10 │ ││ facts / interpretations…      ││  ★★◐☆☆                   │││ …         │
│ Sáb 17/10 │ ││ limitations last              ││  2,5 / 5                  │││ Shared…   │
│ Dom 18/10 │ │╰───────────────────────────────╯│  caption                  ││╰───────────╯
│           │ │                                 ╰───────────────────────────╯│
│           │ │ PICOS DEL DÍA                                                 │
│           │ │╭ Card 1 ╮╭ Card 2 ╮╭ Card 3 ╮╭ Card 4 ╮╭ Card 5 ╮            │
│           │ │╰────────╯╰────────╯╰────────╯╰────────╯╰────────╯            │
╰───────────╯ ╰──────────────────────────────────────────────────────────────╯
█ Navigate: ↑↓ día  ←→ pico  Enter detalle │ R actualizar │ o guardado │ ? │ Q █
```

**Height budget** (approx., terminal height `H`):

| Region | Rule |
|--------|------|
| Header | 2–3 rows |
| StatusBar | 1 row |
| Body | `H - header - status` |
| Days rail width | 18–26 cols |
| Legend rail width | 22–30 cols (hidden &lt; 130) |
| Analysis row | ~30–40% of body height |
| Peak grid | remaining body; cards min-height ~6–8 |

**Space budget**: unstructured empty (no border, no content) SHOULD NOT exceed ~30% of the main body at 120×40 with a full payload.

### 7.3 View B — Peak detail (binding wireframe)

```text
╭─ ← La Aguada · Vie 16/10 · 06:00–20:00 UYT ──────── Perfil: provisional ───╮
╰────────────────────────────────────────────────────────────────────────────╯

╭─ RESUMEN ─────────────╮╭─ EVOLUCIÓN / VENTANA / ANÁLISIS ─────────────────╮╭─ TÉCNICOS* ─╮
│ [Surfeable]           ││ EvolutionTable (3 rows)                          ││ collapsed   │
│ 0,9–1,4 m   10–12 s   ││ BestWindowCallout                                ││ or expanded │
│ Viento …              ││ Peak AnalysisPanel                               ││ via D       │
│ ★★◐☆☆ 2,5 / 5         ││                                                   ││             │
│ Confianza: media      ││                                                   ││             │
╰───────────────────────╯╰───────────────────────────────────────────────────╯╰─────────────╯

█ Esc volver │ ←→ pico │ D técnicos │ R │ ? │ Q █
```

\* On first paint, técnicos stay **collapsed** in the bottom of the center column or a slim bottom frame — MUST NOT steal the left summary + center evolution priority. Optional right help column (“Cómo leer”) on very wide terminals; otherwise Help modal.

**Non-compliant** (current capture): single vertical stack of equally weighted cyan boxes with ISO dump and float garbage.

### 7.4 Focus & selection

| Focus target | Chrome |
|--------------|--------|
| Day list | Selected chip fill; focus on ListView |
| Peak card | `border-selected-card` |
| View B | Summary frame focused on entry; `D` expands tech |
| Modal | Modal focused; background dimmed |

StatusBar SHOULD indicate context: `Vista: informe` / `Vista: detalle · La Aguada`.

---

## 8. Content presentation rules (graphic + copy)

Inherited from 003; enforced visually here:

1. **Facts before limitations** in analysis panels.
2. **Window-completed** is a day banner, not a substitute for peak metrics — cards keep size/period/wind/condition when present in payload.
3. **Best-of-day** marker on one card only; never hide poor peaks.
4. Neutral section title: `PICOS DEL DÍA` (never “recomendados”).
5. Color reinforces FR-017; label text always present.
6. Dual timestamps always labeled.

---

## 9. Responsive behavior

| Width | View A | View B |
|-------|--------|--------|
| ≥ 130 | Days + main + legend; peak grid up to 5 cols | Summary \| center \| tech/help |
| 90–129 | Days + main; legend hidden | Summary \| center (tech collapsed below) |
| &lt; 90 | Vertical stack; 1-col cards; scroll | Vertical stack; preserve order summary→evo→window→analysis→tech |

Never silently truncate analysis; scroll inside panels instead.

---

## 10. Hard anti-patterns (reject on review)

1. Multiline string “cards” without badge / metric structure.
2. `grid-size` capped at 2 on wide terminals when 5 peaks exist.
3. View B as only `VerticalScroll` of homogeneous panels with no column hierarchy.
4. Raw Python floats in UI.
5. ASCII stars (`*`, `-`) as primary rating glyphs.
6. Full ISO-8601 as the primary best-window label.
7. Repeating “ventana finalizada” on every peak line.
8. Doubled `Sin valoración` copy.
9. Floating titles without frames for primary content.
10. English machine tokens (`medium`, `fair`) as primary labels.
11. Overriding Textual `Widget._render`.
12. Re-implementing grade logic inside widgets.
13. Shipping without screenshot gate (§12).
14. Empty canvas &gt; ~30% of body with full data.
15. Treating “section titles exist” as visual acceptance.

---

## 11. Relationship to Spec Kit / prior work

| Layer | Owner |
|-------|-------|
| Forecast engine, criteria, honesty | `001` + constitution |
| Presentation 1.1.0 fields, FR-017, narratives, ratings math | **Frozen** (already shipped; do not reopen under `004`) |
| **Graphic layer, components, layout, visual QA** | **`004-tui-visual-craft` (this doc) — active feature** |

Active Spec Kit commands (`/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, …) MUST target `specs/004-tui-visual-craft` only (see `.specify/feature.json`).

If frozen presentation rules and this doc conflict on **pixels/layout/components**, this doc wins for TUI chrome.  
If they conflict on **meteorology / rating derivation / honesty**, constitution + frozen presentation rules win.

---

## 12. Visual acceptance gates

**Clarified (2026-10-15)**: Sign-off = **manual screenshots** (VS-* vs `references/modelo.png` hierarchy) **plus** Textual `run_test` smoke for hygiene/navigation/anti-pattern strings. Pixel-diff CI is out of scope.

Code complete ≠ feature complete. Before sign-off, capture screenshots (120×40 and 80×24) for:

| ID | State | Must show |
|----|-------|-----------|
| VS-A1 | View A, resolved day with ratings | Header dual times + pill; day rail; analysis+hero; **5 peak cards** comparable; legend or Help |
| VS-A2 | View A, window-completed / no day score | Single banner; cards still show peak fields; `Sin valoración` once |
| VS-B1 | View B peak with samples | 3-zone hierarchy; EvolutionTable; local times; formatted meters; Unicode stars |
| VS-B2 | View B tech expanded | Tech readable; primary path still recognizable when collapsed |
| VS-N1 | Narrow 80×24 View A | Usable stack; no crash; scroll OK |

**SC-V01**: A new user identifies in ≤ 5 seconds: selected day, day score, and best-looking peak card.

Compare VS-* to `references/modelo.png` hierarchy (not mock numbers). Any mismatch in frame structure, missing badges, float leaks, or View B vertical dump → fix before done.

### Manual checklist

- [ ] Peak cards scannable without reading paragraphs  
- [ ] Wide terminal shows multi-card row (not 2-col max)  
- [ ] View B not a uniform vertical dump  
- [ ] No raw floats / `0 s` for missing period / ASCII stars  
- [ ] Best window uses `HH:MM` (wide windows: honest label)  
- [ ] StatusBar distinct from content frames  
- [ ] Enter detail / Esc back preserves day+peak  
- [ ] `D` toggles tech; default collapsed  

### Automated smoke (required)

- [ ] `run_test`: open View A with fixture → `←→` peak → Enter View B → Esc back; no exception  
- [ ] Assert primary render text has no raw multi-decimal float pattern (e.g. `\d+,\d{4,}`)  
- [ ] Assert Unicode star glyphs present when a score exists (no ASCII `***--` pattern)  
- [ ] Existing `scripts/check_report_presentation.py` still passes  

---

## 13. Implementation phases (guide)

Ordered for risk reduction:

1. **Hygiene formatters** — meters, period, stars, local time, confidence Spanish (fixes capture defects immediately).  
2. **Theme tokens + Frame + StatusBar chrome**.  
3. **PeakCard + PeakGrid columns** (View A biggest visual win).  
4. **RatingHero + AnalysisPanel kind styling + Banner**.  
5. **View B 3-zone layout + EvolutionTable + BestWindowCallout**.  
6. **LegendRail / Help parity + responsive**.  
7. **Screenshot gates VS-*** + rebuild exe.

Do not mark the feature complete after phase 1 alone.

---

## 14. Reference quality bar (interpretive)

| App | Steal this | Do not steal |
|-----|------------|--------------|
| LazyGit | Frames, focus border, StatusBar groups | Git-specific panels |
| btop | Density, clear metric blocks | Graphs unless engine supports |
| K9s | Selection chrome, professional ops feel | Cluster metaphors |
| Wireshark | Detail vs list hierarchy, readable columns | Packet hex dumps as primary UI |
| db-log-explorer (sibling) | `theme` package + Panel title-in-border + visual contracts | Purple Rain palette literally |

---

## 15. Success criteria

- **SC-G01**: Side-by-side with `references/modelo.png`, an observer recognizes the same region hierarchy for View A and View B without reading this doc.  
- **SC-G02**: Zero raw multi-decimal floats in primary View A/B fields on fixture `fixtures/normal`.  
- **SC-G03**: At width ≥ 130, five peaks render as five comparable cards in one row (or wrap only if terminal height forces).  
- **SC-G04**: View B first paint prioritizes summary + evolution + window over technical ISO.  
- **SC-G05**: SC-V01 (5-second identify) passes for VS-A1.  
- **SC-G06**: Existing presentation checks (`scripts/check_report_presentation.py`) and engine fixture replay still pass — graphic layer must not regress domain honesty.

---

## 16. Document control

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2026-10-15 | Initial binding graphic layer from modelo vs detalle captures + 003 diagnosis |

**Authors / reviewers**: use this file as the single graphic-layer source of truth during `/speckit-plan` and `/speckit-implement` for `004-tui-visual-craft`.
