# Research: 005-daily-brief

**Date**: 2026-10-15  
**Goal**: Resolve design choices for DayBrief presentation (schema 1.2.0), plain narrative, worth-spot filter, and TUI home without View B — without changing evaluation formulas.

## R1: Schema version and day slicing

**Decision**: Bump presentation `schema_version` from `1.1.0` to `1.2.0`. In `build_presentation`, after evaluating all engine days, emit `days` with **only** the first two local calendar days relative to the report (Hoy, Mañana). Document `query.horizon_*` as presentation horizon (2 days) vs engine may still hold more internally if needed later.

**Rationale**: Clarify Q3 option B; shared contract parity (Q1). Breaking change is honest — consumers expecting five days must adapt.

**Alternatives considered**:
- Keep 1.1.0 and add optional `briefs[]` — rejected (two narratives / drift).
- Cut engine to 2 days — rejected (clarify A; lose optional future reuse).

## R2: Worth-spot filter

**Decision**: Include a peak if `condition` grade rank ≥ `SurfGrade.FAIR` (fair / good / very_good). Sort by grade rank desc, then existing score/peak_rating if present, then `peak_id` for stability. Cap at **3**. Exclude unresolved / no-condition peaks from the list.

**Rationale**: Spec FR-008; `GRADE_ORDER` / `GRADE_TO_SCORE` already encode fair=3.0.

**Alternatives considered**: Score ≥ 3.0 only — equivalent for resolved grades; prefer explicit grade threshold for clarity. Include `small_but_surfable` — rejected (user wants “vale la pena”, not every marginal peak).

## R3: Height and go-window from best worth-spot

**Decision**: After ranking worth spots, `brief.height` and `brief.go_window` come **only** from `worth_spots[0]` (best). If empty list → height `null` / display `n/d`; go-window omitted with empty-state copy. Wide-window honesty reuses 004 FR-G14 rule (≥6 h or full analysis day → “ventana amplia” wording + `HH:MM–HH:MM`, never lead with minute counts).

**Rationale**: Clarify Q4/Q5.

**Alternatives considered**: Min–max across worth spots or all peaks — rejected (dilutes the story; uses discarded peaks).

## R4: Narrative rewrite (template_v2)

**Decision**: Replace home-facing `day_analysis` fact/interpretation/limitation bags (with `≈◇!`) with a DayBrief narrative object: `headline` (1 line) + `body` (3–6 plain Spanish sentences) + optional single `caution` string. Method id `template_v2`. Templates consume: day condition/trend, best worth-spot name(s), wind rotation intensity, go-window text, empty-state. No LLM.

**Rationale**: Spec FR-005; constitution X; existing `narrative.py` is the right module.

**Alternatives considered**: Keep kind-tagged sentences and restyle in TUI — rejected (CLI/JSON would stay technical). LLM — rejected (cost/complexity/constitution).

## R5: Legacy peak payloads

**Decision**: Presentation days **do not** require a full five-`peaks[]` board for home. Prefer DayBrief as primary; keep minimal peak records only if needed for traceability/debug **or** omit `peaks` from 1.2.0 day objects and keep full peak detail only in engine/internal. **Chosen**: Day objects in 1.2.0 carry `brief` as required and may omit interactive peak grids; optional compact `peaks_debug` is **out of scope** — ship `brief` + day-level meta; drop shipping full evolution samples on the interactive path.

**Rationale**: No View B (clarify Q2); shipping evolution tables with nowhere to show them is noise. Checks assert brief invariants, not five PeakCards.

**Alternatives considered**: Keep full 1.1.0 peak arrays under each day — possible for debugging but fights “presentation only Hoy/Mañana brief”; defer unless a check needs them. Plan default: **do not require** `peaks` array for 1.2.0 compliance; if kept temporarily for migration, TUI must ignore it.

## R6: TUI home chrome

**Decision**: `DailyReportScreen` composes header (dual timestamps) + horizontal/stacked **two** `DayBriefCard` widgets + StatusBar. Remove: day ListView rail, PICOS grid, LEYENDA, PeakDetailScreen registration, Enter→detail, ←→ peak index. Focus: optional focus between Hoy/Mañana cards or none (both always visible). Reuse `Frame` / `Badge` / formatters from 004.

**Rationale**: Spec FR-001/002/013; reuse craft without modelo 5-card layout.

**Alternatives considered**: Keep View B via chip Enter — rejected (clarify A).

## R7: CLI / JSON

**Decision**: JSON dumps the 1.2.0 payload as-is. CLI prints for each of two days: title, condition, height, headline, body, go-window, worth spot names — same fields as TUI, plain text.

**Rationale**: Clarify Q1.

## R8: Constitution VI exception

**Decision**: Document in plan Complexity Tracking; narrative may say “conviene priorizar {playa} entre {HH:MM}–{HH:MM}” with a fixed disclaimer line that conditions are estimates, not guarantees. Do **not** amend constitution in this feature unless user runs `/speckit-constitution` later.

**Rationale**: Spec Constitution Constraints; planning prompt.

## R9: Verification

**Decision**: Extend `check_report_presentation.py` for `schema_version == 1.2.0`, `len(days)==2`, brief required fields, worth cap ≤3, grades ≥ fair, height/window null when no worth spots. Update TUI smoke: assert two cards; assert strings PICOS DEL DÍA / LEYENDA absent; assert PeakDetailScreen not pushed. Manual SC-004 prose review on ≥5 fixture days.

**Rationale**: Constitution XI; SC-002/003/006.
