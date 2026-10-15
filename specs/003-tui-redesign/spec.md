# Feature Specification: Surfer-friendly TUI redesign

**Feature Branch**: `003-tui-redesign`

**Created**: 2026-10-14

**Status**: Draft

**Input**: User description: "Complete redesign of the Surf Forecast La Paloma terminal interface into two surfer-oriented views (daily summary + peak detail), with a grounded Spanish day narrative, a documented global day rating (1–5), comparable spot cards, hourly evolution, and secondary technical details—without rewriting the forecast engine or inventing conditions." Plus product framing as a daily surf report (not merely a forecast comparator), narrative/timestamp guidance, and conceptual mockups `mock1.jpg` / `mock2.png`.

## Scope Summary

**Product framing**: With this redesign the interface stops being only a forecast comparator and becomes a **daily surf report**: natural-language analysis, condition valuation, and selection of the best peaks—while remaining honest that a clearer UI is not a more reliable forecast.

**Primary goal**: Redesign the interactive terminal experience so a surfer without technical meteorology background can quickly answer:

1. How will surf conditions look each day?
2. Which beaches/peaks offer the best opportunities that day, and why?
3. When within the day are the best conditions expected?

**In scope**:

- Two primary views: **Daily summary (View A)** and **Peak detail (View B)**, following the binding conceptual composition in `mock2.png`.
- Interpreted Spanish presentation of existing forecast results (day narrative, peak narrative when facts suffice, global and per-peak ratings on the documented 1–5 map, comparable spot cards, hourly evolution, optional technical details)—shared with CLI/JSON/snapshots, not TUI-only.
- Explicit condition vocabulary mapping and an on-screen condition legend (labels always accompany color).
- Keyboard navigation, help footer, responsive layout for different terminal widths.
- Traceability and honesty about uncertainty retained (technical details secondary, not removed).
- Strict separation of **meteorological data age/update time** from **application query execution time**.

**Out of scope**:

- Rewriting the forecast engine, spot profiles, surfability thresholds, or size/quality formulas (except display mapping and any *new* documented day/peak-rating rule that consumes existing outputs).
- Favorites, alerts/notifications, user preference persistence.
- A third independent diagnostic screen.
- Interactive read-only profiles screen inside the TUI (profiles remain file-based configuration outside this UI).
- Paid data sources or new external services.
- Expanding forecast horizon, peaks, or zones beyond the existing product.
- Presenting the day/peak rating as a statistical probability or empirically validated skill score.
- Treating a more attractive UI as evidence of higher forecast skill.
- Binding adoption of `mock1.jpg` as the primary layout (imperial units, air temperature, primary/secondary swell split, and multi-day filled swell chart are **not** required for this delivery; see Visual References).

**Relationship to `001`**: This feature redesigns presentation and adds derived, documented interpretation layers on top of the existing forecast outputs. Engine grade thresholds and classification rules remain those defined in `001` unless a separate, justified change is approved.

## Visual References

Conceptual mockups live beside this spec. **Values shown in the images are illustrative only** and MUST NOT be treated as a real forecast or as acceptance oracles for numeric outputs.

### `mock2.png` — binding conceptual layout (Views A and B)

Reference composition for this feature:

**View A (daily report)**:

- Header: `SURF · LA PALOMA`, horizon (`Pronóstico de hoy + 4 días` / equivalent), meteorological update timestamp in UYT, discrete data-state chip (e.g. `Datos disponibles`).
- Left rail: compact `DÍAS` list (weekday + date), optional per-day rating chip, selected-day highlight, and a compact **Estado de condiciones** legend aligned with FR-017.
- Main column: selected-day title; `ANÁLISIS DEL DÍA`; `VALORACIÓN DEL DÍA` (stars + mandatory numeric score + short qualitative caption); `PICOS DEL DÍA` (neutral; not “recomendados”) as comparable cards (name, FR-017 tag, size m, period s, wind, per-peak 1–5 when resolved).
- Optional right rail on wide terminals: legend / how-to-read metrics; on narrow terminals this content moves to Help or a compact footer/legend strip—MUST NOT be required for answering the three primary questions.
- Footer: contextual key hints (`↑↓` day, `←→` spot, `Enter` detail, `R` refresh, `?` help, `Q` quit; plus documented stored-only and other secondary keys).

**View B (peak detail)**:

- Header/breadcrumb: peak name, selected day, profile orientation/status when available (e.g. provisional), back affordance.
- Summary: FR-017 condition, estimated size range, period, wind/swell summary, peak 1–5 rating when resolved, confidence.
- Temporal block: compact **sampled** analysis-window evolution (documented morning/midday/afternoon-style rows); `MEJOR VENTANA ESTIMADA` only when engine-supported.
- Short **peak analysis** narrative when peak facts suffice (same rule family as day analysis; spot-scoped; no invented meteorology); otherwise omitted/limitation.
- Collapsible `DETALLES TÉCNICOS` starting collapsed (toggle `D`): source/model, Hs vs derived size, ages, shared-cell warning, snapshot id. Technical content MUST NOT dominate the default reading path.

Pixel-perfect reproduction is not required; information hierarchy, Spanish copy patterns, dual-time honesty, and keyboard paths are.

### `mock1.jpg` — non-binding density inspiration

Inspirational only for dense monospaced charting and directional glyphs. Explicitly **not** binding for this delivery because it assumes a different product surface (e.g. feet/mph/°F, primary+secondary swell columns, air temperature, multi-day filled swell graph outside the agreed View A/B daily-report structure). Compatible ideas that may be reused if they fit existing metric units and engine fields: compact direction arrows; sober dashed frames; high information density without cluttering the daily-report narrative.

## Clarifications

### Session 2026-10-14

- Q: Exact Spanish display vocabulary mapping from engine grades/states? → A: Compact map (Option A): `very_good`/`good` → Buena oportunidad; `fair` → Surfeable; `small_but_surfable` → Variable; `no_surfable_waves` → Pocas olas; `uncertain` → Incierto; `incomplete_forecast` → Pronóstico incompleto; `analysis_window_completed` → Ventana de análisis finalizada. Engine identifiers and thresholds unchanged; only user-facing labels merge `very_good` and `good`.
- Q: Are day narrative and global day rating shared with CLI/JSON or TUI-only? → A: Shared across TUI and machine-readable presentation/CLI/JSON (Option A), so adapters stay thin and snapshots retain the same interpretation layer.
- Q: Keep profiles screen and stored-only action? → A: Keep stored-only query as a secondary action; remove the interactive read-only profiles screen from the TUI (Option B). Profiles remain editable as versioned JSON on disk outside this UI.
- Q: How should the global day rating (1–5) be derived from the day’s peak evaluations? → A: Best-peak only (Option A): the day rating mirrors the single best evaluable peak that day; other peaks still appear honestly on cards and must not be hidden by a favorable rating.
- Q: Which peaks count as “evaluable” for that best-peak day rating? → A: Only peaks with a resolved condition grade (Option A); exclude `uncertain`, `incomplete_forecast`, and `analysis_window_completed`. If none qualify, show `Sin valoración` with reason.
- Q: How should spot cards express FR-010 distinctions vs FR-017 vocabulary? → A: FR-017 labels on all cards, plus a distinct “best of day” marker on the top resolved peak only (Option B); no parallel role-badge vocabulary on every card.
- Q: How should View A order spot cards? → A: Engine day ranking (Option A): condition grade rank plus the engine’s existing tie-breaks, best resolved first—aligned with the best-of-day marker and day rating source when present.
- Q: On View A after a forecast loads, where should keyboard focus start? → A: Day list on the current selected day (Option A); spots reached afterward via horizontal navigation or focus cycling.
- Q: How should conceptual mockups and the “daily surf report” framing affect the spec? → A: Adopt product framing as a daily surf report (not only a comparator). Treat `mock2.png` as the binding conceptual layout for Views A/B; treat `mock1.jpg` as non-binding density inspiration. Mock numeric/content values are illustrative only. Keep narrative generation on structured facts + explicit rules (no invented meteorology). Keep meteorological data age distinct from app query time—even when an older update timestamp appears on a later local calendar day. Allow the same documented 1–5 mapping used for the day rating to label each resolved peak on cards/detail. Allow an optional short peak-scoped analysis in View B under the same honesty rules as the day analysis.
- Q: How should View A label the spot-card section titled roughly “SPOTS RECOMENDADOS” in the mock? → A: Neutral title `PICOS DEL DÍA` (Option B refined); no “recomendado” / `SPOTS EVALUADOS` copy. Keep the “best of day” marker without advice-to-surf wording.
- Q: When should View B show the optional peak analysis narrative in the first delivery? → A: Show when sufficient peak-scoped facts exist for at least one evidence-bound sentence; otherwise omit or show a brief limitation (Option A).
- Q: Should peak 1–5 scores and peak analysis text also be part of the shared machine-readable presentation? → A: Yes for both (Option A): peak scores and peak analysis (when present) are included in the shared presentation consumed by TUI, CLI/JSON, and snapshots.
- Q: On first open of View B, should `DETALLES TÉCNICOS` start collapsed or visible? → A: Collapsed by default; expand/collapse with `D` (Option A).
- Q: How dense should View B’s hourly evolution be relative to analysis-window hours? → A: Sampled times only (Option A), e.g. morning/midday/afternoon style as in the mock; sampling rule MUST be documented and MUST NOT invent a best window. Full hourly detail remains available via engine/presentation data for verification even if the TUI samples for display.
- Q: Confirm plan pending decisions (score map, captions, sample bands, section title)? → A: Confirmed as suggested (2026-10-14): ordinal `SurfGrade`→1.0…5.0 whole points; day = best resolved peak; captions per `data-model.md`; bands 06:00–10:59 / 11:00–14:59 / 15:00–20:00 UYT; section title `PICOS DEL DÍA`. Rating is display encoding of engine grades, not a new meteorology formula; narrative remains templates only (no LLM); TUI does not reimplement classification rules.
- Q: Post-`/speckit-analyze` remediations (I1–I3, U1–U3)? → A: FR-007 aligned to ordinal `SurfGrade` map only (no multi-factor UI formula); v1 whole-point scores; section title only `PICOS DEL DÍA`; TUI must render `sentences` fact vs interpretation; checks cover provisional + analysis-window-completed; wind km/h via presentation pass-through of engine slot inputs (no evaluation threshold changes).

## User Scenarios & Testing *(mandatory)*

The product informs; it does not recommend or discourage surfing or traveling. Incomplete data MUST NOT be shown as “no waves.” Color may reinforce status but MUST never be the only signal.

### User Story 1 - Daily surf report at a glance (Priority: P1)

As a La Paloma surfer, I want a daily surf report with a short Spanish analysis, a global day rating, and comparable spot cards so I can grasp the day’s picture without reading raw model fields.

**Why this priority**: Directly answers questions 1 and 2; is the default landing experience and the core “informe diario” framing.

**Independent Test**: With a complete sample forecast for five days, open the app and verify View A shows header, analysis, rating (or explicit “Sin valoración”), legend-capable condition labels, and ordered spot cards for the selected day; changing the day updates those sections.

**Acceptance Scenarios**:

1. **Given** a successful forecast query with enough data for a selected day, **When** the user opens the main interface, **Then** View A shows: application title `SURF · LA PALOMA`, selected local date with weekday (e.g. `Miércoles 14/10`), horizon `Hoy + 4 días` (or equivalent Spanish), meteorological data-update time in Uruguay local time when available, and a discrete data-state indicator when needed—without presenting that update time as the moment the app was run unless they coincide and are labeled accordingly.
2. **Given** meteorological data last updated on an earlier calendar day than the selected forecast day (e.g. updated `12/10 18:00 UYT` while viewing `14/10`), **When** View A renders, **Then** the UI may show that older update timestamp as the real data age/update time and MUST NOT imply the models were refreshed on the selected day unless that is true.
3. **Given** View A for a day with sufficient inputs, **When** the user reads `ANÁLISIS DEL DÍA`, **Then** they see a multi-sentence Spanish summary built from structured facts and explicit rules (e.g. SE swell + S-SE wind + E-oriented exposures from profiles), covering available swell evolution, direction/period, wind evolution, profile-backed exposure interpretation, and estimated surfable size variation—without inventing unsupported phenomena (cyclones, concrete probabilities, model disagreement with a single source, “series mayores,” meter-class sets, etc.).
4. **Given** an analysis that includes both forecast facts and profile-derived interpretations, **When** View A renders `ANÁLISIS DEL DÍA`, **Then** those kinds are visually distinguishable (via `day_analysis.sentences[].kind` styling or explicit prefixes)—not a single undifferentiated paragraph that hides the distinction.
5. **Given** insufficient inputs for a grounded analysis, **When** View A renders, **Then** the analysis section explains the limitation briefly instead of fabricating a narrative.
6. **Given** at least one peak with a resolved condition grade for the day, **When** View A renders, **Then** a day rating uses the confirmed whole-point ordinal map of that peak’s engine `SurfGrade` (1.0…5.0), with both a visual indicator and a mandatory numeric form that always match, optionally plus a short qualitative caption; if every peak is uncertain, incomplete, or analysis-window-completed (or otherwise lacks a resolved grade), show `Sin valoración` with the reason.
7. **Given** multiple evaluated peaks, **When** View A lists spots, **Then** cards follow the engine’s day ranking (condition grade rank and existing tie-breaks, best resolved first), show comparable fields (name, Spanish FR-017 condition label, size range m, period s, wind direction/speed km/h when available from presentation pass-through), show the documented 1–5 peak score for resolved peaks, mark only the best resolved peak with a distinct “best of day” indicator, do not repeat the full day narrative, and never present incomplete profiles as recommended.
8. **Given** a day whose peaks include both favorable and unfavorable conditions, **When** a favorable global rating is shown, **Then** unfavorable spots remain visibly unfavorable on their cards via FR-017 labels (global rating and the single best-of-day marker MUST NOT hide poor spots).

---

### User Story 2 - Navigate days and open peak detail (Priority: P1)

As a surfer, I want to move across the five forecast days and open a peak’s detail so I can compare days and inspect when conditions look best.

**Why this priority**: Completes the core browse loop for questions 1–3.

**Independent Test**: From View A, change days with keyboard, select a peak, open View B, and return to View A without losing the selected day context unexpectedly.

**Acceptance Scenarios**:

1. **Given** five local forecast days, **When** the user moves day selection (↑/↓ or documented equivalents), **Then** the selected day is visually highlighted and View A content switches to that day; the day list stays compact (rating/summary chip allowed; no long headlines duplicated in the list).
2. **Given** a forecast has just loaded into View A, **When** the shell is ready for keyboard input, **Then** focus starts on the day list at the current selected day (not on spot cards or the analysis panel).
3. **Given** a selected day and focus on a spot card, **When** the user presses Enter (or documented open action), **Then** View B opens for that peak and day.
4. **Given** View B, **When** the user presses Esc (or documented back action), **Then** they return to View A for the same day.
5. **Given** View A or B, **When** the user requests help (`?`), **Then** key bindings and meaning of conditions/uncertainty are available; a footer always shows contextual key hints.
6. **Given** an active forecast session, **When** the user requests refresh (`R`), **Then** data refresh follows existing cache/force-refresh rules and the UI remains usable (no frozen shell).

---

### User Story 3 - Peak detail, hourly evolution, and best window (Priority: P1)

As a surfer, I want peak detail with hourly evolution and a best window only when evidence exists so I can judge timing within the day.

**Why this priority**: Answers question 3 without inventing an optimal entry time.

**Independent Test**: Open View B for a peak with hourly slots and, separately, for a peak/day without a supported best window; verify both presentations.

**Acceptance Scenarios**:

1. **Given** View B, **When** it opens, **Then** the header shows peak name, selected day/date, analysis window `06:00–20:00` UYT (or equivalent), overall condition, and estimated size; profile orientation/status may appear when available.
2. **Given** available peak inputs, **When** conditions section renders, **Then** it shows surfable size range, swell direction/period, wind direction/intensity, wind evolution when available, confidence, peak 1–5 rating when resolved, and a brief limitation explanation.
3. **Given** hourly slots in the analysis window, **When** View B’s evolution section renders, **Then** it shows a **documented sample** of times (e.g. morning / midday / afternoon within 06:00–20:00 UYT), each with local time, estimated surfable size, wind (direction, intensity, relative evaluation), estimated condition, and uncertainty/incomplete markers when applicable, in compact metric form (m, s, km/h). Sampling MUST NOT invent missing hours or a best window.
4. **Given** the engine identified a best window meeting the project’s minimum duration with sufficient hourly support, **When** View B renders, **Then** `MEJOR VENTANA ESTIMADA` appears with that engine-backed window even if sample rows omit some in-between hours; otherwise the UI explicitly states that no clear window exists and does not invent one.
5. **Given** sufficient peak-scoped facts for at least one evidence-bound sentence, **When** View B renders, **Then** a short peak analysis narrative is shown from the same rule family as the day analysis, scoped to that peak, and MUST NOT invent unsupported meteorology; **Given** insufficient peak facts, **Then** the peak-analysis block is omitted or replaced by a brief limitation (not fabricated prose).
6. **Given** today after the analysis window ended, **When** View B (or View A for today) renders, **Then** the existing rule applies: analysis window completed; no new surf best window for today.

---

### User Story 4 - Secondary technical details without a third screen (Priority: P2)

As a careful user, I want technical provenance available inside peak detail so I can verify sources, conversion factors, and snapshot identity without leaving the surfer-oriented flow.

**Why this priority**: Preserves honesty/traceability without dominating the default view.

**Independent Test**: In View B, toggle technical details on and off; confirm required provenance fields appear only when expanded.

**Acceptance Scenarios**:

1. **Given** View B just opened, **When** the user views the screen before toggling details, **Then** `DETALLES TÉCNICOS` starts collapsed and technical identifiers/logs do not dominate the primary content.
2. **Given** View B, **When** the user toggles details (`D` or documented equivalent), **Then** `DETALLES TÉCNICOS` expands or collapses accordingly; when expanded it shows source/model identity, update time and data age, raw Hs and derived estimated size, conversion factor and uncertainty range, peak-profile and criteria versions, confidence/limitation reasons, snapshot id, and shared regional-cell warnings when relevant.
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
- Day where every peak is uncertain, incomplete, or analysis-window-completed: global rating is `Sin valoración` with reason; cards still show each peak’s honest state.
- Day with some resolved and some incomplete peaks: rating uses only the best resolved peak; incomplete peaks remain non-recommended on cards.
- Single data source only: analysis MUST NOT claim model disagreement.
- Missing model run / update time: do not display a fake model update time; distinguish query execution time from meteorological data age; if sources differ in age, do not pretend they share one age.
- Older meteorological update shown on a later local day (e.g. data updated 12/10 18:00 UYT while reading 14/10): allowed when labeled as data update/age; MUST NOT be presented as “forecast generated on 14/10” solely because that is the selected day.
- Mockup-like decorative content that the engine cannot support (secondary swell split, air temperature, imperial units, multi-day filled swell chart as primary View A): MUST NOT be fabricated to resemble `mock1.jpg`.
- Narrow terminal width: stack/compact layout without silent truncation of important analysis text (scroll instead).
- Wide terminal width: multi-panel layout allowed if all required information and keyboard access remain.
- Half-star glyph unsupported by terminal: numeric rating remains fully understandable; alternate half-step glyph allowed.
- Refresh while previous refresh is in flight: follow existing cancel/replace behavior so older results cannot overwrite newer ones.
- Snapshot persistence failure: do not claim durable reproducibility until persistence succeeds (existing honesty rule).
- Provisional profiles: never presented as calibrated; evaluation limits remain visible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide exactly two primary interactive views for this redesign: Daily summary (View A) and Peak detail (View B).
- **FR-002**: View A MUST show header content: `SURF · LA PALOMA`, selected local weekday/date, `Hoy + 4 días` (or equivalent), Uruguay-local meteorological data update time when known, and a discrete data-state indicator when relevant, consistent with the `mock2.png` header hierarchy.
- **FR-003**: System MUST distinguish query execution time from meteorological data age/update time and MUST NOT present unavailable model-run times as if known. An older meteorological update timestamp MAY appear while viewing a later local day when it reflects real data age and is labeled accordingly.
- **FR-004**: View A MUST include `ANÁLISIS DEL DÍA`: a Spanish natural-language summary generated only from available forecast facts, peak profiles, and documented template/rules (first version: structured sentence construction, not free-form generative prose).
- **FR-005**: Day analysis MUST NOT invent unsupported weather evolution, cyclones, concrete probabilities, multi-model disagreement without evidence, unsupported “series mayores,” or other unsupported claims; when evidence is insufficient, it MUST state the limitation and reduce content. A more attractive narrative MUST NOT be treated as higher forecast reliability.
- **FR-006**: Day analysis MUST visually/typographically distinguish forecast facts from profile-derived interpretations when both appear (via structured `sentences[].kind` of `fact` | `interpretation` | `limitation` rendered distinctly in View A).
- **FR-007**: System MUST compute a global day rating by **ordinal display encoding** of the engine’s existing resolved `SurfGrade` for the single best resolved peak that day (method `best_resolved_grade_map_v1`): `no_surfable_waves`→1.0, `small_but_surfable`→2.0, `fair`→3.0, `good`→4.0, `very_good`→5.0. Size, wind, period, direction, and uncertainty MUST NOT be re-scored in the presentation/TUI layer—the engine already applied those rules when producing the grade. Peaks in `uncertain`, `incomplete_forecast`, or `analysis_window_completed` MUST NOT be selected as the rating source. If no resolved-grade peak exists, output `Sin valoración` with reason. The rating MUST NOT average or blend multiple peaks; weaker or non-resolved peaks MUST still appear honestly on cards. The scale allows 0.5 increments for a future documented refinement; **v1 MUST emit whole-point scores only**.
- **FR-008**: Day rating presentation MUST include a mandatory numeric form that exactly matches any star/glyph visualization; an optional short qualitative caption MAY accompany the score when it is consistent with the documented mapping. Rating MUST NOT be described as a probability or validated skill metric. v1 glyphs represent whole points from FR-007 (half-step glyphs unused unless a later confirmed refinement emits half scores).
- **FR-009**: View A MUST list spot cards under the neutral section title `PICOS DEL DÍA` (MUST NOT use “recomendados”, `SPOTS EVALUADOS`, or advice-to-surf wording), in the engine’s day-ranking order (condition grade rank plus existing engine tie-breaks; best resolved peaks first), with comparable fields when available, without duplicating the full day narrative on each card.
- **FR-010**: Spot cards MUST use FR-017 Spanish condition/state labels as the primary condition text. Resolved peaks MUST show the same documented 1–5 mapping applied to that peak (so card scores are comparable to the day rating). The single best resolved peak for the day MUST receive one additional distinct “best of day” marker. Cards MUST NOT introduce a second parallel role-badge vocabulary on every card. “Surfeable” MUST NOT be treated as “excellent.”
- **FR-011**: Incomplete profiles or missing essential data MUST be shown as not evaluable; they MUST NOT receive a recommendation-style presentation.
- **FR-012**: Users MUST be able to select among the five forecast days from a compact day list that highlights the selection and may show a short rating/status chip when data exist. View A MUST expose a compact FR-017 condition legend (sidebar, strip, or Help)—color alone is never sufficient.
- **FR-013**: View B MUST show peak header, conditions, **sampled** analysis-window evolution (documented sample rule; not necessarily every hourly slot), best-window behavior, peak analysis when facts suffice, and rating/confidence as defined in US3, following the `mock2.png` information hierarchy.
- **FR-014**: Best window MUST appear only when the existing engine supports it; otherwise the UI MUST explicitly say none exists.
- **FR-015**: Technical provenance MUST be available as a collapsible `DETALLES TÉCNICOS` section inside View B that starts **collapsed** on first open and toggles via keyboard (`D` or documented equivalent); the product MUST NOT add a third independent diagnostic screen for that content. Shared regional-cell warnings remain in this secondary area when relevant (visible when expanded).
- **FR-016**: All primary user-facing prose and condition labels in this redesign MUST be Spanish; machine identifiers remain internal.
- **FR-017**: User-facing Spanish condition/state labels MUST follow this compact vocabulary map (engine identifiers and thresholds unchanged): `very_good` and `good` → `Buena oportunidad`; `fair` → `Surfeable`; `small_but_surfable` → `Variable`; `no_surfable_waves` → `Pocas olas`; `uncertain` → `Incierto`; `incomplete_forecast` → `Pronóstico incompleto`; `analysis_window_completed` → `Ventana de análisis finalizada`.
- **FR-018**: Status color MUST be supplementary only; every status also has text and/or a non-color symbol.
- **FR-019**: Layout MUST adapt to different terminal widths without overlap or silent truncation of important content; scrolling is allowed.
- **FR-020**: Keyboard navigation MUST support day change, spot change where applicable, open detail, toggle technical details, refresh per existing rules, stored-only query as a secondary action, help, back to summary, and quit; bindings may be adapted for terminal capability but MUST remain documented in the footer/help. After a forecast loads into View A, initial keyboard focus MUST be on the day list at the selected day.
- **FR-021**: Spot names MUST display with correct Spanish capitalization for the five configured peaks (La Aguada, Zanja Honda, Los Botes, La Serena, La Balconada).
- **FR-022**: Redesign MUST preserve existing snapshot immutability/traceability behavior for emitted queries.
- **FR-023**: Day-rating calculation, peak-rating mapping, and day/peak-analysis generation MUST remain separable from pure view rendering so each can be validated with example data.
- **FR-024**: Day narrative, global day rating, per-peak 1–5 scores (when resolved), and peak analysis text (when present) MUST be part of the shared forecast presentation consumed by the TUI and by machine-readable CLI/JSON outputs (including snapshots), not TUI-only ephemeral views.
- **FR-025**: Existing forecast engine thresholds, profile fields, and classification formulas MUST remain unchanged by this feature; any future change requires independent justification outside this redesign’s visual needs.
- **FR-026**: The TUI MUST NOT include an interactive read-only profiles screen; peak profiles remain human-editable versioned JSON outside the UI. Stored-only query MUST remain reachable as a secondary keyboard action documented in help/footer.
- **FR-027**: Presentation verification MUST cover at least: normal good day, variable/mixed day, incomplete data, provisional profile, and analysis-window-completed today—via the project’s established verification approach (deterministic fixtures/checklists and any presentation checks added for this feature).
- **FR-028**: Visual style MUST be dark, sober, high-contrast, with consistent monospace alignment; titles/separators in blue/cyan; favorable/variable/alert/neutral encoded with green/yellow/red/gray (and additional legend colors only when paired with FR-017 text) without large saturated backgrounds or excessive frames. Layout SHOULD follow `mock2.png` hierarchy; it MUST NOT require `mock1.jpg` chrome or imperial presentation.
- **FR-029**: Primary screens MUST avoid showing internal ids, raw logs, or English machine enums as the main content.
- **FR-030**: Peak analysis in View B MUST appear when sufficient peak-scoped facts exist for at least one evidence-bound sentence; otherwise it MUST be omitted or replaced by a brief limitation. When shown, it MUST use the same evidence-bound template/rules approach as the day analysis and MUST remain separable from view rendering for verification.
- **FR-031**: Conceptual mockup files `mock1.jpg` and `mock2.png` are design references only; illustrative numbers and copy in those images MUST NOT be copied into fixtures as if they were engine truth.

### Key Entities

- **Daily Surf Report (View A)**: Selected-day presentation combining header, day analysis, global rating (+ optional caption), condition legend, and ordered spot cards—framed as an informe diario, not a raw comparator table.
- **Day Analysis**: Deterministic Spanish narrative from structured day/peak facts and profiles via explicit templates/rules; includes limitation text when thin; never free-invented meteorology.
- **Peak Analysis**: Shorter spot-scoped narrative shown when peak facts suffice for ≥1 evidence-bound sentence; otherwise omitted/limitation; same honesty rules as day analysis.
- **Global Day Rating**: Optional 1.0–5.0 (0.5 steps) indicator that mirrors the day’s single best peak with a resolved condition grade; reason when absent; not a probability and not a multi-peak average; never sourced from uncertain/incomplete/analysis-window-completed peaks.
- **Peak Rating**: Same documented 1–5 mapping applied to an individual resolved peak for cards and View B.
- **Spot Card**: Compact comparable peak summary for one day (FR-017 condition label, size range, period, wind, 1–5 when resolved, “best of day” marker for the top resolved peak).
- **Peak Detail View**: Peak/day conditions, hourly slots, optional best window, optional peak analysis, collapsible technical details.
- **Technical Details**: Provenance and conversion/traceability fields secondary to surfer-oriented content.
- **Condition Vocabulary Map**: Explicit correspondence between internal engine grades/states and user-facing Spanish labels used in this redesign.
- **Time Provenance**: Distinct meteorological data update/age versus application query execution time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a manual walkthrough with sample data, a new user can answer the three primary questions for a selected day in under 60 seconds from the main daily report without opening technical details.
- **SC-002**: For every fixture day used in verification, day (and peak, if shown) analysis either cites only available facts/profile-derived interpretations or explicitly states limitations—zero fabricated claims in the reviewed cases; no cyclone/probability/unsupported-set language appears unless backed by system data.
- **SC-003**: Global day ratings, when present, are always in the allowed scale; **v1 fixtures emit whole points in {1.0, 2.0, 3.0, 4.0, 5.0}**; numeric and glyph forms never disagree; insufficient cases show `Sin valoración` with reason in 100% of reviewed insufficient fixtures.
- **SC-004**: Spot cards for a mixed-quality day never upgrade an incomplete or poor peak into a recommended appearance solely because the global rating is favorable.
- **SC-005**: Best-window section appears only when the engine provides a supported window; otherwise the UI states absence in 100% of no-window fixtures.
- **SC-006**: Technical details remain reachable inside peak detail and are not required to understand the primary summary; no third diagnostic screen exists.
- **SC-007**: At least two terminal width classes (narrow and wide) show all required View A/B information without overlap or silent clipping of the day analysis.
- **SC-008**: Documented keyboard paths for day change, open/back, technical toggle, help, refresh, and quit succeed in the verification checklist.
- **SC-009**: Existing engine verification scenarios continue to pass after the redesign; presentation verification covers normal, uncertain, missing-data, provisional-profile, and analysis-window-completed cases.
- **SC-010**: In verification, meteorological update/age and query execution time are distinguishable in at least one reviewed complete-result presentation; a stale-or-older update on a later selected day remains correctly labeled when tested.
- **SC-011**: A reviewer comparing the running TUI to `mock2.png` can recognize the same information hierarchy (days rail, analysis, valuation, spot cards, detail with secondary technicals) without requiring pixel parity or copying illustrative mock numbers.

## Assumptions

- The existing on-demand forecast query, five-day horizon, five peaks, 06:00–20:00 UYT analysis window, confidence/degradation rules, and snapshot behavior from `001` remain the data backbone.
- The documented 1–5 mapping applies both to the global day rating (best resolved peak) and to each resolved peak’s card/detail score; non-resolved peaks show no numeric score (or explicit absence), never a fake rating.
- “Surfeable” (`fair`) means acceptable surfable conditions under existing engine rules and is not a synonym of excellent; “Variable” (`small_but_surfable`) means small but surfable / limited quality, not “no waves.”
- Merging `good` and `very_good` into one display label is an intentional presentation simplification; internal grades remain distinct for evaluation/traceability.
- The “best of day” card marker identifies the same resolved peak that sources the global day rating when a rating exists.
- Spot-card order matches engine day ranking so the first resolved card is typically the best-of-day / rating source when one exists.
- Half-step star glyphs may fall back to a terminal-safe alternative; numeric rating is the source of truth for accessibility.
- Visual theme tokens (cyan titles, green/yellow/red/gray status) are presentation guidance, not additional business rules; mock legend colors may vary if text labels remain correct.
- Implementation planning documents: (1) ordinal `SurfGrade`→1.0…5.0 whole-point map (`best_resolved_grade_map_v1`, no multi-factor UI formula); (2) sentence templates for day/peak analysis with `fact`/`interpretation`/`limitation` kinds; (3) View B sample bands `06:00–10:59` / `11:00–14:59` / `15:00–20:00` UYT; (4) wind km/h via presentation pass-through of engine slot inputs. Exact Spanish prose strings remain template-implementation detail in `narrative.py`.
- Full hourly slots remain in the underlying forecast/presentation model for best-window logic and verification even when View B displays only samples.
- Verification remains primarily manual/fixture-driven as in the project baseline; “presentation tests” means reproducible presentation scenarios and checklists (and optional automated checks if the project later adopts them), not a mandate to introduce a full CI stack in this feature alone.
- Branding string `SURF · LA PALOMA` is the user-facing product title for this redesign.
- Default secondary key for stored-only remains `o` unless planning finds a conflict; help/footer MUST document the final binding.
- Profile JSON path may still be mentioned in Help/About as documentation, without an interactive profiles browser screen.
- After load, View A focus starts on the day list; moving to spots uses ←/→ or Tab/focus cycle as documented in help.
- Wide-terminal right-rail legend from `mock2.png` may collapse into Help on narrow terminals without losing FR-017 textual labels on cards/states.
- Metric units (m, s, km/h, UYT) remain canonical; mock1 imperial units are ignored.

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: MUST NOT introduce paid services or mandatory costs.
- **On-demand**: MUST NOT add always-on daemons, alerts infrastructure, or background notification services.
- **Honesty**: Uncertainty, incomplete forecast, stale data, and single-source limits MUST remain visible; day/peak ratings are indicators, not guarantees or probabilities. A polished daily-report UI MUST NOT be presented as improved forecast skill.
- **Inform, do not decide**: Copy MUST NOT tell the user to surf or travel; section titles MUST avoid “recomendados” advice framing (use neutral peak/spot evaluation wording).
- **Data integrity**: Narrative and ratings MUST NOT invent meteorological facts; raw Hs MUST NOT be presented as beach breaking height; derived estimates remain labeled as such in technical details.
- **Traceability**: Snapshot id, criteria/profile versions, sources/models, conversion factors, and distinct data-age vs query-time remain available.
- **Simplicity**: No favorites/preferences/alerts; no third diagnostic screen; no engine rewrite for cosmetics; no fabricating mock1-only fields.
- **Tension note**: Elaborated narrative analysis was deferred beyond first delivery in `001`; this feature intentionally introduces constrained, rule/template-based day (and optional peak) narratives as a presentation/interpretation layer. They MUST stay evidence-bound (Principles V/VIII) and MUST NOT become free-form storytelling.
