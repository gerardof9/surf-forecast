# Feature Specification: Surfer-friendly TUI redesign

**Feature Branch**: `003-tui-redesign`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Complete redesign of the Surf Forecast La Paloma terminal interface into two surfer-oriented views (daily summary + peak detail), with a grounded Spanish day narrative, a documented global day rating (1–5), comparable spot cards, hourly evolution, and secondary technical details—without rewriting the forecast engine or inventing conditions."

## Scope Summary

**Primary goal**: Redesign the interactive terminal experience so a surfer without technical meteorology background can quickly answer:

1. How will surf conditions look each day?
2. Which beaches/peaks offer the best opportunities that day, and why?
3. When within the day are the best conditions expected?

**In scope**:

- Two primary views: **Daily summary (View A)** and **Peak detail (View B)**.
- Interpreted Spanish presentation of existing forecast results (narrative day analysis, global day rating, comparable spot cards, hourly evolution, optional technical details).
- Explicit condition vocabulary mapping for user-facing Spanish labels.
- Keyboard navigation, help footer, responsive layout for different terminal widths.
- Traceability and honesty about uncertainty retained (technical details secondary, not removed).

**Out of scope**:

- Rewriting the forecast engine, spot profiles, surfability thresholds, or size/quality formulas (except display mapping and any *new* documented day-rating rule that consumes existing outputs).
- Favorites, alerts/notifications, user preference persistence.
- A third independent diagnostic screen.
- Interactive read-only profiles screen inside the TUI (profiles remain file-based configuration outside this UI).
- Paid data sources or new external services.
- Expanding forecast horizon, peaks, or zones beyond the existing product.
- Presenting the day rating as a statistical probability or empirically validated skill score.

**Relationship to `001`**: This feature redesigns presentation and adds derived, documented interpretation layers on top of the existing forecast outputs. Engine grade thresholds and classification rules remain those defined in `001` unless a separate, justified change is approved.

## Clarifications

### Session 2026-10-14

- Q: Exact Spanish display vocabulary mapping from engine grades/states? → A: Compact map (Option A): `very_good`/`good` → Buena oportunidad; `fair` → Surfeable; `small_but_surfable` → Variable; `no_surfable_waves` → Pocas olas; `uncertain` → Incierto; `incomplete_forecast` → Pronóstico incompleto; `analysis_window_completed` → Ventana de análisis finalizada. Engine identifiers and thresholds unchanged; only user-facing labels merge `very_good` and `good`.
- Q: Are day narrative and global day rating shared with CLI/JSON or TUI-only? → A: Shared across TUI and machine-readable presentation/CLI/JSON (Option A), so adapters stay thin and snapshots retain the same interpretation layer.
- Q: Keep profiles screen and stored-only action? → A: Keep stored-only query as a secondary action; remove the interactive read-only profiles screen from the TUI (Option B). Profiles remain editable as versioned JSON on disk outside this UI.

## User Scenarios & Testing *(mandatory)*

The product informs; it does not recommend or discourage surfing or traveling. Incomplete data MUST NOT be shown as “no waves.” Color may reinforce status but MUST never be the only signal.

### User Story 1 - Daily summary at a glance (Priority: P1)

As a La Paloma surfer, I want a daily summary with a short Spanish analysis, a global day rating, and comparable spot cards so I can grasp the day’s picture without reading raw model fields.

**Why this priority**: Directly answers questions 1 and 2; is the default landing experience.

**Independent Test**: With a complete sample forecast for five days, open the app and verify View A shows header, analysis, rating (or explicit “Sin valoración”), and ordered spot cards for the selected day; changing the day updates those sections.

**Acceptance Scenarios**:

1. **Given** a successful forecast query with enough data for a selected day, **When** the user opens the main interface, **Then** View A shows: application title `SURF · LA PALOMA`, selected local date with weekday (e.g. `Miércoles 14/10`), horizon `Hoy + 4 días`, data-update time in Uruguay local time when available, and a discrete data-state indicator when needed.
2. **Given** View A for a day with sufficient inputs, **When** the user reads `ANÁLISIS DEL DÍA`, **Then** they see a multi-sentence Spanish summary covering available facts about swell evolution, relevant direction/period, wind evolution, spot-exposure interpretation only when profiles support it, and estimated surfable size variation—without inventing unsupported phenomena (cyclones, probabilities, model disagreement with a single source, “series mayores,” etc.).
3. **Given** insufficient inputs for a grounded analysis, **When** View A renders, **Then** the analysis section explains the limitation briefly instead of fabricating a narrative.
4. **Given** enough peak evaluations for a global day judgment, **When** View A renders, **Then** a day rating from 1.0 to 5.0 in 0.5 steps appears with both a visual indicator and a mandatory numeric form (e.g. `4,5 / 5`) that always match; if insufficient, show `Sin valoración` with the reason.
5. **Given** multiple evaluated peaks, **When** View A lists spots, **Then** cards are ordered by the engine’s real evaluation, show comparable fields (name, Spanish condition, size range m, period s, wind direction/speed km/h when available), do not repeat the full day narrative, and never present incomplete profiles as recommended.
6. **Given** a day whose peaks include both favorable and unfavorable conditions, **When** a favorable global rating is shown, **Then** unfavorable spots remain visibly unfavorable on their cards (global rating MUST NOT hide poor spots).

---

### User Story 2 - Navigate days and open peak detail (Priority: P1)

As a surfer, I want to move across the five forecast days and open a peak’s detail so I can compare days and inspect when conditions look best.

**Why this priority**: Completes the core browse loop for questions 1–3.

**Independent Test**: From View A, change days with keyboard, select a peak, open View B, and return to View A without losing the selected day context unexpectedly.

**Acceptance Scenarios**:

1. **Given** five local forecast days, **When** the user moves day selection (↑/↓ or documented equivalents), **Then** the selected day is visually highlighted and View A content switches to that day; the day list stays compact (rating/summary chip allowed; no long headlines duplicated in the list).
2. **Given** a selected day and focus on a spot card, **When** the user presses Enter (or documented open action), **Then** View B opens for that peak and day.
3. **Given** View B, **When** the user presses Esc (or documented back action), **Then** they return to View A for the same day.
4. **Given** View A or B, **When** the user requests help (`?`), **Then** key bindings and meaning of conditions/uncertainty are available; a footer always shows contextual key hints.
5. **Given** an active forecast session, **When** the user requests refresh (`R`), **Then** data refresh follows existing cache/force-refresh rules and the UI remains usable (no frozen shell).

---

### User Story 3 - Peak detail, hourly evolution, and best window (Priority: P1)

As a surfer, I want peak detail with hourly evolution and a best window only when evidence exists so I can judge timing within the day.

**Why this priority**: Answers question 3 without inventing an optimal entry time.

**Independent Test**: Open View B for a peak with hourly slots and, separately, for a peak/day without a supported best window; verify both presentations.

**Acceptance Scenarios**:

1. **Given** View B, **When** it opens, **Then** the header shows peak name, selected day/date, analysis window `06:00–20:00` UYT, overall condition, and estimated size.
2. **Given** available peak inputs, **When** conditions section renders, **Then** it shows surfable size range, swell direction/period, wind direction/intensity, wind evolution when available, confidence, and a brief limitation explanation.
3. **Given** hourly slots in the analysis window, **When** hourly evolution renders, **Then** each slot shows local time, estimated surfable size, wind (direction, intensity, relative evaluation), estimated condition, and uncertainty/incomplete markers when applicable, in a compact readable form.
4. **Given** the engine identified a best window meeting the project’s minimum duration with sufficient hourly support, **When** View B renders, **Then** `MEJOR VENTANA ESTIMADA` appears with that window; otherwise the UI explicitly states that no clear window exists and does not invent one.
5. **Given** today after the analysis window ended, **When** View B (or View A for today) renders, **Then** the existing rule applies: analysis window completed; no new surf best window for today.

---

### User Story 4 - Secondary technical details without a third screen (Priority: P2)

As a careful user, I want technical provenance available inside peak detail so I can verify sources, conversion factors, and snapshot identity without leaving the surfer-oriented flow.

**Why this priority**: Preserves honesty/traceability without dominating the default view.

**Independent Test**: In View B, toggle technical details on and off; confirm required provenance fields appear only when expanded.

**Acceptance Scenarios**:

1. **Given** View B with technical section collapsed, **When** the user views the screen, **Then** technical identifiers/logs do not dominate the primary content.
2. **Given** View B, **When** the user toggles details (`D` or documented equivalent), **Then** `DETALLES TÉCNICOS` shows source/model identity, update time and data age, raw Hs and derived estimated size, conversion factor and uncertainty range, peak-profile and criteria versions, confidence/limitation reasons, snapshot id, and shared regional-cell warnings when relevant.
3. **Given** this feature, **When** navigating the product, **Then** there is no separate third diagnostic screen for the same technical content.

---

### User Story 5 - Consistent Spanish vocabulary and honest states (Priority: P2)

As a surfer, I want consistent Spanish condition language and non-color-only states so I am never forced to decode English machine identifiers or ambiguous mixed labels.

**Why this priority**: Prevents misreading “surfeable” as “excellent” and keeps degraded states honest.

**Independent Test**: Review labels across View A/B for normal, uncertain, incomplete, and analysis-window-completed cases against the approved vocabulary map.

**Acceptance Scenarios**:

1. **Given** any user-facing screen in this redesign, **When** conditions/states are shown, **Then** Spanish labels follow FR-017 and raw machine identifiers (e.g. `fair`, `resolved`) are not shown as primary labels.
2. **Given** incomplete essential data or an incomplete profile, **When** a spot is listed, **Then** it is marked as not evaluable / incomplete—not as “few waves” and not as a recommendation.
3. **Given** any color-coded status, **When** the user cannot rely on color, **Then** a textual label (and/or non-color symbol) still communicates the state.
4. **Given** engine grades `good` and `very_good`, **When** displayed, **Then** both use `Buena oportunidad` without changing underlying thresholds or identifiers.

---

### Edge Cases

- Selected day with mixed peak quality while global rating is mid/high: poor spots remain visibly poor.
- Single data source only: analysis MUST NOT claim model disagreement.
- Missing model run / update time: do not display a fake model update time; distinguish query execution time from meteorological data age; if sources differ in age, do not pretend they share one age.
- Narrow terminal width: stack/compact layout without silent truncation of important analysis text (scroll instead).
- Wide terminal width: multi-panel layout allowed if all required information and keyboard access remain.
- Half-star glyph unsupported by terminal: numeric rating remains fully understandable; alternate half-step glyph allowed.
- Refresh while previous refresh is in flight: follow existing cancel/replace behavior so older results cannot overwrite newer ones.
- Snapshot persistence failure: do not claim durable reproducibility until persistence succeeds (existing honesty rule).
- Provisional profiles: never presented as calibrated; evaluation limits remain visible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide exactly two primary interactive views for this redesign: Daily summary (View A) and Peak detail (View B).
- **FR-002**: View A MUST show header content: `SURF · LA PALOMA`, selected local weekday/date, `Hoy + 4 días`, Uruguay-local data update time when known, and a discrete data-state indicator when relevant.
- **FR-003**: System MUST distinguish query execution time from meteorological data age/update time and MUST NOT present unavailable model-run times as if known.
- **FR-004**: View A MUST include `ANÁLISIS DEL DÍA`: a Spanish natural-language summary generated only from available forecast facts, peak profiles, and documented rules.
- **FR-005**: Day analysis MUST NOT invent unsupported weather evolution, probabilities, multi-model disagreement without evidence, or other unsupported claims; when evidence is insufficient, it MUST state the limitation and reduce content.
- **FR-006**: Day analysis MUST visually/typographically distinguish forecast facts from profile-derived interpretations when both appear.
- **FR-007**: System MUST compute a global day rating on a 1.0–5.0 scale in 0.5 increments using a documented deterministic rule based on available engine outputs (estimated size, wind quality, period, swell direction, hourly evolution, and uncertainty as available)—or output `Sin valoración` with reason when insufficient.
- **FR-008**: Day rating presentation MUST include a mandatory numeric form that exactly matches any star/glyph visualization; rating MUST NOT be described as a probability or validated skill metric.
- **FR-009**: View A MUST list spot cards ordered by the engine’s evaluation, with comparable fields when available, without duplicating the full day narrative on each card.
- **FR-010**: Spot cards MUST distinguish at least: best estimated opportunity; surfable with limitations; few waves; uncertain; incomplete forecast—without treating “surfable” as “excellent.”
- **FR-011**: Incomplete profiles or missing essential data MUST be shown as not evaluable; they MUST NOT receive a recommendation-style presentation.
- **FR-012**: Users MUST be able to select among the five forecast days from a compact day list that highlights the selection and may show a short rating/status chip when data exist.
- **FR-013**: View B MUST show peak header, conditions, hourly evolution, and best-window section behavior defined in US3.
- **FR-014**: Best window MUST appear only when the existing engine supports it; otherwise the UI MUST explicitly say none exists.
- **FR-015**: Technical provenance MUST be available as a collapsible `DETALLES TÉCNICOS` section inside View B (toggle via keyboard); the product MUST NOT add a third independent diagnostic screen for that content.
- **FR-016**: All primary user-facing prose and condition labels in this redesign MUST be Spanish; machine identifiers remain internal.
- **FR-017**: User-facing Spanish condition/state labels MUST follow this compact vocabulary map (engine identifiers and thresholds unchanged): `very_good` and `good` → `Buena oportunidad`; `fair` → `Surfeable`; `small_but_surfable` → `Variable`; `no_surfable_waves` → `Pocas olas`; `uncertain` → `Incierto`; `incomplete_forecast` → `Pronóstico incompleto`; `analysis_window_completed` → `Ventana de análisis finalizada`.
- **FR-018**: Status color MUST be supplementary only; every status also has text and/or a non-color symbol.
- **FR-019**: Layout MUST adapt to different terminal widths without overlap or silent truncation of important content; scrolling is allowed.
- **FR-020**: Keyboard navigation MUST support day change, spot change where applicable, open detail, toggle technical details, refresh per existing rules, stored-only query as a secondary action, help, back to summary, and quit; bindings may be adapted for terminal capability but MUST remain documented in the footer/help.
- **FR-021**: Spot names MUST display with correct Spanish capitalization for the five configured peaks (La Aguada, Zanja Honda, Los Botes, La Serena, La Balconada).
- **FR-022**: Redesign MUST preserve existing snapshot immutability/traceability behavior for emitted queries.
- **FR-023**: Day-rating calculation and day-analysis generation MUST remain separable from pure view rendering so each can be validated with example data.
- **FR-024**: Day narrative and global day rating MUST be part of the shared forecast presentation consumed by the TUI and by machine-readable CLI/JSON outputs (including snapshots), not TUI-only ephemeral views.
- **FR-025**: Existing forecast engine thresholds, profile fields, and classification formulas MUST remain unchanged by this feature; any future change requires independent justification outside this redesign’s visual needs.
- **FR-026**: The TUI MUST NOT include an interactive read-only profiles screen; peak profiles remain human-editable versioned JSON outside the UI. Stored-only query MUST remain reachable as a secondary keyboard action documented in help/footer.
- **FR-027**: Presentation verification MUST cover at least: normal good day, variable/mixed day, incomplete data, provisional profile, and analysis-window-completed today—via the project’s established verification approach (deterministic fixtures/checklists and any presentation checks added for this feature).
- **FR-028**: Visual style MUST be dark, sober, high-contrast, with consistent monospace alignment; titles/separators in blue/cyan; favorable/variable/alert/neutral encoded with green/yellow/red/gray respectively without large saturated backgrounds or excessive frames.
- **FR-029**: Primary screens MUST avoid showing internal ids, raw logs, or English machine enums as the main content.

### Key Entities

- **Daily Summary View**: Selected day presentation combining header, narrative analysis, global rating, and ordered spot cards.
- **Day Analysis**: Deterministic Spanish narrative derived from structured day/peak facts and profiles; includes limitation text when thin.
- **Global Day Rating**: Optional 1.0–5.0 (0.5 steps) indicator for overall day surf prospects, with reason when absent; not a probability.
- **Spot Card**: Compact comparable peak summary for one day (condition label, size range, period, wind, optional peak-specific score only if engine already provides a documented per-peak evaluation).
- **Peak Detail View**: Peak/day conditions, hourly slots, optional best window, collapsible technical details.
- **Technical Details**: Provenance and conversion/traceability fields secondary to surfer-oriented content.
- **Condition Vocabulary Map**: Explicit correspondence between internal engine grades/states and user-facing Spanish labels used in this redesign.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a manual walkthrough with sample data, a new user can answer the three primary questions for a selected day in under 60 seconds from the main summary without opening technical details.
- **SC-002**: For every fixture day used in verification, the day analysis either cites only available facts/profile-derived interpretations or explicitly states limitations—zero fabricated claims in the reviewed cases.
- **SC-003**: Global day ratings, when present, are always in {1.0, 1.5, …, 5.0}; numeric and glyph forms never disagree; insufficient cases show `Sin valoración` with reason in 100% of reviewed insufficient fixtures.
- **SC-004**: Spot cards for a mixed-quality day never upgrade an incomplete or poor peak into a recommended appearance solely because the global rating is favorable.
- **SC-005**: Best-window section appears only when the engine provides a supported window; otherwise the UI states absence in 100% of no-window fixtures.
- **SC-006**: Technical details remain reachable inside peak detail and are not required to understand the primary summary; no third diagnostic screen exists.
- **SC-007**: At least two terminal width classes (narrow and wide) show all required View A/B information without overlap or silent clipping of the day analysis.
- **SC-008**: Documented keyboard paths for day change, open/back, technical toggle, help, refresh, and quit succeed in the verification checklist.
- **SC-009**: Existing engine verification scenarios continue to pass after the redesign; presentation verification covers normal, uncertain, missing-data, provisional-profile, and analysis-window-completed cases.

## Assumptions

- The existing on-demand forecast query, five-day horizon, five peaks, 06:00–20:00 UYT analysis window, confidence/degradation rules, and snapshot behavior from `001` remain the data backbone.
- Per-spot numeric ratings appear on cards only if the engine already exposes a documented per-peak evaluation; this redesign does not invent a second undocumented per-spot score merely for UI symmetry with the global day rating.
- “Surfeable” (`fair`) means acceptable surfable conditions under existing engine rules and is not a synonym of excellent; “Variable” (`small_but_surfable`) means small but surfable / limited quality, not “no waves.”
- Merging `good` and `very_good` into one display label is an intentional presentation simplification; internal grades remain distinct for evaluation/traceability.
- Half-step star glyphs may fall back to a terminal-safe alternative; numeric rating is the source of truth for accessibility.
- Visual theme tokens (cyan titles, green/yellow/red/gray status) are presentation guidance, not additional business rules.
- Implementation planning will document the exact day-rating weights/factors; the specification requires determinism, documentation, and honesty constraints rather than prescribing the formula here.
- Verification remains primarily manual/fixture-driven as in the project baseline; “presentation tests” means reproducible presentation scenarios and checklists (and optional automated checks if the project later adopts them), not a mandate to introduce a full CI stack in this feature alone.
- Branding string `SURF · LA PALOMA` is the user-facing product title for this redesign.
- Default secondary key for stored-only remains `o` unless planning finds a conflict; help/footer MUST document the final binding.
- Profile JSON path may still be mentioned in Help/About as documentation, without an interactive profiles browser screen.

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: MUST NOT introduce paid services or mandatory costs.
- **On-demand**: MUST NOT add always-on daemons, alerts infrastructure, or background notification services.
- **Honesty**: Uncertainty, incomplete forecast, stale data, and single-source limits MUST remain visible; day rating is an indicator, not a guarantee or probability.
- **Inform, do not decide**: Copy MUST NOT tell the user to surf or travel.
- **Data integrity**: Narrative and ratings MUST NOT invent meteorological facts; raw Hs MUST NOT be presented as beach breaking height; derived estimates remain labeled as such in technical details.
- **Traceability**: Snapshot id, criteria/profile versions, sources/models, and conversion factors remain available in technical details.
- **Simplicity**: No favorites/preferences/alerts; no third diagnostic screen; no engine rewrite for cosmetics.
- **Tension note**: Elaborated narrative analysis was deferred beyond first delivery in `001`; this feature intentionally introduces a constrained, rule-based narrative as a presentation/interpretation layer. It MUST stay evidence-bound (Principles V/VIII) and MUST NOT become free-form storytelling.
