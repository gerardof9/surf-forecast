# Research: 004-tui-visual-craft

**Date**: 2026-10-15  
**Goal**: Resolve technical decisions for implementing the graphic layer under Textual without reopening frozen presentation 1.1.0 or the forecast engine.

## R1: Frame chrome — Unicode title-in-border vs Textual CSS borders

**Decision**: Custom `Frame` widget that paints Unicode box-drawing with the section title embedded in the top border (`╭─ TITLE ──╮`), focus restyles border/title color (and may use `═` on focused top edge).

**Rationale**: Clarification FR-G11; matches LazyGit / db-log-explorer professional chrome. Current CSS `border` + floating cyan titles produced the non-compliant “diagnostic dump” look in `references/detalle_capture_*.png`.

**Alternatives considered**:
- Textual CSS `border: round/tall` + inner Static title — rejected (non-compliant per FR-G11).
- Hybrid CSS for v1 — rejected; would re-ship the same failure mode.

**Implementation note**: Implement as a Textual container that owns border lines as child `Static` rows or a custom `render`/`compose` that does **not** override `Widget._render` for content population APIs named `_render` (FR-G10). Prefer composing three regions (top/body/bottom) or a dedicated paint helper. Study sibling `db-log-explorer/internal/ui/panel.go` for title-width math with Unicode width.

## R2: Peak keyboard model

**Decision**: Primary focus remains on the day `ListView`; `←→` updates `peak_index` and card selection chrome; `Enter` opens View B for the active peak (FR-G12).

**Rationale**: Preserves frozen “focus starts on days” product rule; avoids fighting Textual focus traps across a grid of cards.

**Alternatives considered**: Focusable cards / Tab dual-mode — higher complexity, more focus bugs on Windows terminals.

## R3: Iconography budget

**Decision**: Minimal Unicode — rating `★/◐/☆`, condition `●`, best-of-day `★`; optional wind arrows only if reliable on common Windows consoles. No Nerd Fonts; no wave/pin/compass (FR-G13).

**Rationale**: Scan path comes from badges + metrics columns + stars, not decorative glyphs that break across fonts.

## R4: Wide / full-day best window presentation

**Decision**: Still show `BestWindowCallout` with honest label “Ventana amplia (día completo)” (or equivalent) + local `HH:MM–HH:MM` when duration ≥ 6 h or window covers 06:00–20:00 UYT. Do not lead with `840 min` (FR-G14).

**Rationale**: Honesty without hiding engine-provided windows; avoids fake “tight peak” perception.

## R5: Visual acceptance / DoD

**Decision**: Manual VS-A1…VS-N1 screenshots vs `references/modelo.png` hierarchy **plus** Textual `run_test` smoke for hygiene strings, Enter/Esc navigation, and detectable anti-patterns. No pixel-diff CI (FR-G15).

**Rationale**: Pixel diffs are brittle on Windows font/metrics; smoke catches the float/`***--` class of regressions that made captures look broken.

## R6: Module layout inside `presentation/tui`

**Decision**: Add `formatters.py`, `theme.py`, and `components/` package; keep `app.py` / `screens.py` as composition/shell; shrink god-file `widgets.py` by moving card/rating helpers into components/formatters.

**Rationale**: Separates pure formatting (testable without Textual app) from chrome widgets; mirrors graphic-layer architecture diagram.

**Alternatives considered**: Keep everything in `widgets.py` — rejected (unmaintainable; caused prior `_render` collision).

## R7: Peak grid columns

**Decision**: Enforce graphic-layer breakpoints: ≥130 → up to 5 columns; 90–129 → 2–3; &lt;90 → 1. Hard `grid-size: 2` ceiling on wide terminals is non-compliant (FR-G03).

**Rationale**: Binding modelo composition is a five-card row on wide terminals.

## R8: Textual version / toolkit lock

**Decision**: Stay on Textual 8.x already in `pyproject.toml`. No toolkit migration.

**Rationale**: Failure was craft, not library capability; constitution simplicity.

## R9: Half-star glyph

**Decision**: Use `◐` for half steps consistently with existing presentation half-step scores; pair always with numeric `N,N / 5`.

**Rationale**: Spec already allows half-step scores; ASCII substitutes forbidden (FR-G05).

## R10: Spec Kit active feature pin

**Decision**: `.specify/feature.json` → `specs/004-tui-visual-craft`; visual baselines live under `references/`. Do not plan or implement against `specs/003-*` paths.

**Rationale**: Prior pin caused `/speckit-*` to write to the wrong feature.

## Open items for tasks (not blocking research)

- Exact Textual container strategy for `Frame` body scroll vs fixed height — choose simplest during Frame task; document in code comment.
- Whether `EvolutionTable` uses `DataTable` or monospace `Static` columns — prefer monospace Static first for density control; upgrade to DataTable only if alignment proves painful.
