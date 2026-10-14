# Feature Specification: Personalized surf forecast for La Paloma

**Feature Branch**: `001-la-paloma-surf-forecast`

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: "Personal, on-demand tool that gathers free swell and wind data to estimate, peak by peak, whether there will be surfable waves today and over the next 4 days in La Paloma, with confidence, local profiles, and staged evolution."

## Scope Summary

**Primary question**: Will there be waves at each La Paloma peak today and over the next 4 days?

**Secondary**: With what quality, at what hours, and with how much confidence?

**Medium-term (later stage)**: What swell do the models already show en route for the following days?

**Surfable definition**: estimated size ≥ 0.5 m (real wave face, not raw model height). Wind, period, and direction grade quality; they do not by themselves rule out the existence of waves.

**First delivery (MVP)**: US1, US2, and US3 — basic operational forecast for today + 4 days (5 days total), five peaks, basic confidence, graceful source-failure handling, terminal interface, and immutable local snapshots of every emitted query. Observation entry, discrepancy analysis, criteria adjustments, elaborated narrative analysis, medium-term outlook, and performance evaluation belong to later stages and **do not expand** first-delivery scope.

**Delivery stages (order)**:
1. First: US1–US3 (operational + profiles + basic confidence) and immutable query snapshots
2. Second: US6 validation foundation (record observations, compare them with snapshots, expose discrepancies, and support manual versioned reversible criteria adjustments)
3. Third: US4 (analysis / model comparison) + US5 (days 5–10 outlook)
4. Fourth: US6 advanced correction (evidence-based adjustment proposals and bounded automatic application with historical impact checks)
5. Last: US7–US9 (reference comparison, changes between queries, other zones)

**Out of scope (first delivery and until expressly added)**: other zones (e.g. La Pedrera), commercial/multi-user/accounts/payments, alerts or autonomous processes, GUI or web interfaces, tide, automatic extraction from forecast websites, proprietary wave-propagation or coastal-hydrodynamics models, presenting hit probability without contrasting against observations.

## Clarifications

### Session 2026-10-13

- Q: How should estimated size and quality factors map into the ordinal condition scale above “No surfable waves”? → A: Size bands set the ceiling; unfavorable wind/period/direction may lower the grade by at most one step (Option B)
- Q: How long may previously downloaded forecast data be reused before a new fetch is required (unless the user forces refresh)? → A: 3 hours (Option B)
- Q: How should the fixed daily analysis window be defined (FR-020)? → A: 06:00–20:00 Uruguay local; call it the “analysis time window”, not actual daylight hours.
- Q: What non-overlapping wind-speed bands (sustained, km/h) should map to light / moderate / strong / very strong? → A: 0 ≤ v < 10 / 10 ≤ v < 20 / 20 ≤ v < 35 / v ≥ 35 km/h.
- Q: What initial provisional rule should convert model significant wave height into estimated surfable size? → A: surfable ≈ 0.5 × Hs; configurable and visible in results, documented as provisional and replaceable/calibratable, not a validated physical conversion.
- Q: Is offshore/terral wind required for surfability or good conditions? → A: No. Wind direction and intensity are relevant quality indicators, but neither offshore wind nor any single wind direction is a prerequisite for surfability or by itself decisive for overall quality.
- Q: How should size bands be expressed? → A: With non-overlapping intervals and explicit inclusive/exclusive boundaries.
- Q: Can quality factors lower a size-qualified surfable result to “No surfable waves”? → A: No. When estimated size is at least 0.5 m, quality downgrades MUST stop at “Small but surfable.”
- Q: What happens when a query is made after the 06:00–20:00 analysis window? → A: Today is shown as “Analysis window completed,” receives no condition or best window, and the fixed horizon remains today through day +4.
- Q: What must be retained from the MVP onward? → A: Every emitted query is saved as an immutable local snapshot with the inputs, provenance, effective criteria/profile versions, outputs, confidence, and incidents needed for traceability and later comparison.
- Q: How is uncertainty handled near the 0.5 m threshold? → A: A point estimate alone MUST NOT force a hard classification when the plausible range crosses 0.5 m; show the range and “Uncertain.” Phase 0 research defines the initial documented configurable uncertainty method.

### Session 2026-10-14

- Q: When is a quality factor “unfavorable,” and when does the one-step downgrade apply? → A: Classify swell direction, period, and wind each as favorable, neutral, unfavorable, or unknown using the versioned criteria below. Apply at most one downgrade only when **two or more** of those three factors are unfavorable. One unfavorable factor is shown as a reason and does not lower the grade. Unknown never counts as unfavorable. Size ≥ 0.5 m still cannot fall below Small but surfable.
- Q: Does first delivery honor a user-marked calibrated profile? → A: Yes, when essential fields are complete. The system never promotes a profile to calibrated by itself. Incomplete essential fields keep the profile incomplete even if the file says calibrated. A calibrated profile does not lift the medium-confidence cap while only one model family is in use.
- Q: Is swell building/peaking/dropping in the first delivery? → A: Yes, as a labeled derived trend from consecutive hourly swell or total-wave height when at least three analysis-window samples exist. Otherwise the trend is unsupported, never invented.
- Q: Are alternative prediction methods (FR-045) in the first delivery? → A: No. First delivery has one versioned criteria set. Comparing another method is a later stage; until then, change criteria JSON and replay a snapshot.

## User Scenarios & Testing *(mandatory)*

Surf condition uses a single scale (also used in observations): **No surfable waves** (< 0.5 m estimated), **Small but surfable**, **Fair**, **Good**, **Very good**, plus **Uncertain** (low confidence) and **Incomplete forecast** (missing data). The system informs; it does not recommend or discourage surfing or traveling.

**Provisional size → ceiling-grade mapping** (estimated real wave; documented, replaceable bands):

| Estimated size | Ceiling grade |
|----------------|---------------|
| 0 ≤ h < 0.5 m | No surfable waves (wind/period/direction do not turn this into surfable) |
| 0.5 ≤ h < 0.8 m | Small but surfable |
| 0.8 ≤ h < 1.2 m | Fair |
| 1.2 ≤ h < 1.8 m | Good |
| h ≥ 1.8 m | Very good |

**Quality rule**: size sets the ceiling; wind (direction and intensity), period, and swell direction are quality indicators, not requirements for a wave to be surfable. Offshore (terral) wind is not required. Factors never raise the grade above the size ceiling. A size-qualified result of at least 0.5 m MUST NEVER be downgraded below **Small but surfable**.

**Initial provisional factor classification** (versioned in criteria; replaceable):

| Factor | Favorable | Unfavorable | Neutral / unknown |
|--------|-----------|-------------|-------------------|
| Swell direction | Inside an ideal sector | Inside a blocked sector | Acceptable sector, or unclassified; missing direction is unknown |
| Period | Inside the ideal period range | Below `minimum_period_s` when that field is set; otherwise below the ideal-range minimum | At or above the ideal minimum but outside the ideal range; missing period is unknown |
| Wind | Offshore or offshore-side, and light or moderate | Onshore or onshore-side, and strong or very strong | All other classified combinations, including light onshore; missing speed or direction is unknown |

**Downgrade trigger**: lower the size-ceiling grade by **at most one step** only when **two or more** classified factors are unfavorable. A single unfavorable factor is recorded and shown; it is not by itself decisive. Unknown factors are omitted from the count and MUST NOT be treated as favorable or unfavorable.

### User Story 1 - Conditions today and coming days (Priority: P1) — First delivery

As a La Paloma surfer, I want to see for today and the next 4 days what conditions each peak will have, so I know when and where there will be surfable waves.

**Why this priority**: reason the system exists.

**Independent Test**: with sample data, one query produces each day's summary.

**Acceptance Scenarios**:

1. **Given** data from at least one source, **When** the user requests the forecast, **Then** they receive for today and each of the next 4 days a summary with headline, size range, dominant swell (period and direction), wind (speed range, direction, and rotation through the day), surf condition, and confidence.
2. **Given** a day when conditions differ across peaks, **Then** the summary shows each peak's condition and highlights the best ones.
3. **Given** a day without sufficient swell or wind data, **Then** it is marked Incomplete forecast and never No surfable waves.
4. **Given** a day with low confidence, **Then** the condition is presented as Uncertain with a brief cause (incomplete/stale data, a single useful source/model, or provisional profile). Detailed model comparison belongs to US4.
5. **Given** the current day, **Then** only remaining hours are considered and the query time is shown.
6. **Given** a query at or after 20:00 Uruguay local time, **Then** today is shown as Analysis window completed, no condition or best window is emitted for today, and forecasts still cover tomorrow through day +4 without extending to day +5.

---

### User Story 2 - Detail by peak and time slot (Priority: P1) — First delivery

As a surfer, I want to know how each peak's conditions evolve through the day and when they will be best.

**Why this priority**: time of day and wind define quality as much as size.

**Independent Test**: for a sample peak and day, the time-slot breakdown is obtained.

**Acceptance Scenarios**:

1. **Given** a peak and a day, **When** the user views detail, **Then** they see conditions at 06:00, 12:00, and 18:00 (size, period, swell direction and whether favorable for that peak, wind and whether favorable) and the best window of at least 2 hours.
2. **Given** wind worsens in the afternoon without size changing, **Then** the best slot is morning and the reason is explained.
3. **Given** size increases but wind worsens, **Then** it is not interpreted as a quality improvement.
4. **Given** a day from the day after tomorrow onward, **Then** the most favorable analysis time window (morning, midday, or afternoon) is indicated without promising an exact hour.

---

### User Story 3 - Profile for each peak (Priority: P1) — First delivery

As someone who knows the area, I want to describe how each peak works (swell directions, clean winds, shelter, periods, bottom) so the system can distinguish nearby peaks.

**Why this priority**: regional models do not distinguish peaks; the profile is what differentiates them.

**Independent Test**: with complete, incomplete, incoherent, and user-marked calibrated sample profiles, each peak gets the correct status.

**Acceptance Scenarios**:

1. **Given** a peak with all essential fields and no observation contrast, **Then** it is evaluated as provisional, shown as such, and its confidence does not exceed medium.
2. **Given** a peak missing essential fields, **Then** it is incomplete: it receives no condition, is listed separately with what is missing and available regional data. Estimated optional fields do not enable it.
3. **Given** a peak the user marked calibrated after comparing with observations, **Then** it is evaluated as calibrated.
4. **Given** a profile with incoherent values, **Then** the system detects and reports it before evaluating.
5. **Given** swell, period, or wind differing from the profile ideals, **Then** the system estimates with a documented provisional initial rule whether ≥ 0.5 m waves could still arrive; it labels the estimate, expresses uncertainty; it does not discard solely for non-ideal, nor present the estimate as a measurement or validated physical conversion.

---

### User Story 4 - Understand why (Priority: P2) — Third stage

As a user who does not want to trust blindly, I want to see which data and rules led to each condition and read a brief analysis.

**Why this priority**: builds trust and helps spot errors; the condition already works without this.

**Independent Test**: for any condition, the reasoning can be reconstructed.

**Acceptance Scenarios**:

1. **Given** any condition, **When** the user opens reasoning detail (US4 stage), **Then** they see swell and wind values used, source and model, favorable/unfavorable factors, and a brief natural-language analysis marked as automatically generated. First delivery only needs basic data, condition, confidence, and a short rule-based reason.
2. **Given** two or more models differ, **Then** (US4) they are shown separately with disagreement, not only an average.
3. **Given** the result depends on a provisional peak, **Then** that is indicated with the condition.
4. **Given** stored data from a prior query were used, **Then** their age is reported.

---

### User Story 5 - Medium-term outlook (Priority: P2) — Third stage

As a user, I want an estimate of what is coming later, based on swell the models already show en route.

**Why this priority**: extends the horizon with less reliability than the short range.

**Independent Test**: a query shows the outlook separately from the operational forecast.

**Acceptance Scenarios**:

1. **Given** sources cover that range, **When** queried, **Then** a regional daily swell/wind outlook is shown, clearly distinct from the operational forecast.
2. **Given** swell already shown en route by models, **Then** estimated arrival and uncertainty are reported, without asserting surfable waves at a peak.
3. **Given** a day in that range, **Then** no per-peak or per-hour condition is emitted.
4. **Given** the signal changes between queries or models, **Then** confidence is marked low.

---

### User Story 6 - Observations and criteria correction (Priority: P2) — Second and fourth stages

As a user, I want to record what I found in the water (or what other forecasts say) and have the system review its criteria when it is wrong.

**Why this priority**: moves from provisional rules to validated rules.

**Independent Test**: in the second stage, a sample observation is compared with an immutable query snapshot and produces a discrepancy available for review. In the fourth stage, a supported sample error produces an adjustment proposal and, only when evidence is sufficient, a bounded automatic adjustment.

**Acceptance Scenarios**:

1. **Given** the user records an observation (date, time, peak, condition on the common scale, size, wind, subjective/instrumental type), **Then** it is stored and not mixed with another type.
2. **Given** the user reports inconsistency with what they see at the peak, **Then** the system records the discrepancy, keeps the original forecast intact, and identifies involved criteria; only with a justifiable rule and sufficient evidence does it apply an automatic bounded reversible adjustment without further confirmation.
3. **Given** an adjustment was applied, **Then** it recalculates the current forecast, shows the new result and what changed; the observation does not replace the historical forecast; if the new result disagrees with the observation, it reports that.
4. **Given** the error is from sources or the cause cannot be identified with support, **Then** it records the discrepancy, does not change criteria for source error, and if the cause is uncertain proposes an adjustment for review.
5. **Given** an adjustment would appreciably worsen past recorded cases, **Then** it applies only if it improves the new case and records the conflict.
6. **Given** an adjustment was applied, **Then** it is logged with date and reason, is reversible, and later queries use the new criteria.
7. **Given** a manually loaded reference forecast that disagrees, **Then** it is recorded as evidence but does not by itself change criteria.
8. **Given** a sufficient set of observations, **When** the user requests evaluation, **Then** they receive a hit/miss report by lead time (same day, 1–4 days, days 5–10 outlook) with false positives and missed opportunities.
9. **Given** days without stored forecasts, **Then** the report states that and only uses source history if available.

**Stage boundary**: the second stage implements observation capture, comparison with saved query snapshots, discrepancy visibility, and manual versioned reversible adjustments. Evidence-based proposals, automatic application, recalculation, and historical impact checks belong to the fourth stage.

---

### User Story 7 - Compare with existing reference (Priority: P3) — Later stage

As a user, I want to compare the system's forecast with another Uruguayan site and with what was observed, to know if the tool is more accurate.

**Why this priority**: accuracy is only proven by comparison; needs accumulated observations.

**Independent Test**: with sample references and observations, the comparison is obtained.

**Acceptance Scenarios**:

1. **Given** a manually entered reference forecast, **Then** it is stored separately from the system's own.
2. **Given** a sufficient set of observations with own and reference forecasts, **Then** the report compares both against what was observed.
3. **Given** any use, **Then** the system does not scrape or reproduce reference-site content: it only stores what the user enters.

---

### User Story 8 - Changes since last query (Priority: P3) — Later stage

As a user who checks occasionally, I want to quickly see what changed.

**Why this priority**: convenience; does not affect forecast content.

**Independent Test**: two successive queries with different data show the difference.

**Acceptance Scenarios**:

1. **Given** a prior query less than 72 hours old, **Then** relevant changes are highlighted (condition, best peak, estimated size).
2. **Given** none exists or it is older, **Then** "no recent comparison" is indicated.

---

### User Story 9 - Add other zones (Priority: P3) — Later stage

As a user, I want to later add peaks from other zones (e.g. La Pedrera).

**Why this priority**: not needed in v1, but shapes the design.

**Independent Test**: a test peak is added and appears in the query.

**Acceptance Scenarios**:

1. **Given** a new peak with its profile, **When** it is added, **Then** it appears in queries without changing how the system works.

---

### Edge Cases

- One source fails or takes too long: the query continues with the others; each source's status is shown. With a single available source, confidence does not exceed medium.
- All sources fail: if recent stored data exist, they are used with age reported; if not, this is stated clearly and no forecast is generated.
- No connectivity: only the last stored query may be shown, identified as such.
- Repeated queries in a short time: data downloaded less than 3 hours ago are reused unless the user forces refresh; data ≥ 3 h are not reusable as fresh (new download or stored-only mode with age reported).
- Models disagree: shown separately and confidence drops; not hidden by an average.
- Non-independent models (same origin/service): do not count as mutual confirmation.
- Wind sea vs groundswell: not confused.
- Swell building or dropping: arrival / peak / drop reported when supported.
- Wind rotating: evaluated per slot; no all-day average.
- Size grows but wind worsens: not a quality improvement.
- Swell reaches the zone but a peak does not receive it: the coast is not assumed uniform.
- Model height ≠ perceived height: the 0.5 m minimum is on the real wave; initial estimate uses **surfable size ≈ k × Hs**, with k = 0.5 configurable, visible in results, not validated as a physical breaking-height conversion.
- A plausible estimated-size range crosses 0.5 m: show the range and Uncertain; do not force either No surfable waves or Small but surfable from the point estimate alone.
- Fewer than 2 valid hours in a day: that day has no window and is not classified as No surfable waves.
- A query is made at or after 20:00 Uruguay local time: today is shown as Analysis window completed with no condition or best window; the horizon remains today through day +4.
- The selected source exposes samples less frequently than hourly: the system MUST NOT silently claim a precise contiguous 2-hour window. Phase 0 research must select an hourly source or define and label a derived interpolation rule; without sufficient support, the window is Uncertain or unavailable.
- Data that do not distinguish peaks or land on land: detected and reported; unsupported differences are not presented as precise.
- A source stops being free or changes terms: continue with others; never activate a cost.
- Reference vs system disagree: do not declare who is right; compare against observation.
- Few or no observations: scores and confidence are not presented as probabilities.
- Isolated report: adjustments bounded, reversible, checked against past cases; no drastic criteria change from a single case.

## Requirements *(mandatory)*

### Functional Requirements

#### On-demand query

- **FR-001**: The system MUST run on demand: on user command, obtain data, process it, and deliver the forecast without depending on prior or permanent processes.
- **FR-002**: The system MUST deliver results in a simple terminal (text) interface: immediate summary and peak/slot detail on request, without requiring a browser or GUI. *(First delivery)*
- **FR-003**: The system MUST reuse data downloaded less than 3 hours ago to avoid unnecessary downloads; MUST allow forced refresh or stored-only mode (reporting age). After 3 hours, a normal query MUST try to obtain new data.

#### Sources and data

- **FR-004**: The system MUST use exclusively zero-cost sources and tools, without subscriptions, free trials that become paid, or depleting credits.
- **FR-005**: The system MUST respect each source's terms of use (personal use, query limits, attribution).
- **FR-006**: The system MUST inform, for each displayed datum, which source and model it comes from and when it is from.
- **FR-007**: The system MUST NOT treat sources that share an origin as independent.
- **FR-008**: The system MUST distinguish measured data, forecast data, physical inference, and empirical rule.
- **FR-009**: The system MUST NOT automatically extract third-party web content when their terms disallow it.
- **FR-010**: The system MUST keep working with remaining sources when one fails or changes terms.

#### Peak profiles

- **FR-011**: The system MUST maintain a per-peak profile, editable by the user without changing the system: location, orientation, ideal swell directions (and acceptable/blocked if known), offshore winds, wind shelter by direction, ideal period, and bottom type.
- **FR-012**: The system MUST derive profile status from content and user decision, and behave accordingly (US3). Missing any essential field yields `incomplete`, even if the file says `calibrated`. Complete essential fields with no user calibration yield `provisional`. A user-marked `calibrated` value is honored only when essential fields are complete. The system MUST NEVER promote a profile to `calibrated` by itself.
- **FR-013**: The system MUST NOT invent essential profile fields (valid location, orientation, ideal swell, and ideal period). Known offshore winds are useful for quality assessment but are not a requirement to decide whether surfable waves may exist and MUST NOT be decisive alone. Missing optional fields MAY be estimated with a documented rule, marked as estimated, and correctable; if there is no basis, they remain unknown. An estimate does not enable an incomplete profile.
- **FR-014**: The system MUST report when several peaks receive the same origin data (differences only from profiles).
- **FR-015**: The system MUST allow adding new peaks or zones by supplying only their profiles.

#### Evaluation and surf condition

- **FR-016**: The system MUST evaluate compatibility of swell, wind, and profile for each peak and slot. First delivery MUST use a provisional configurable initial rule **estimated surfable size ≈ k × Hs**, with initial **k = 0.5** (Hs = model significant wave height). The current k and calculated size MUST be shown in results. The rule MUST be documented and replaceable/calibratable per peak/criteria; MUST NOT be presented as a validated physical conversion or breaking-height prediction. Deviations from ideal conditions MUST NOT automatically discard surfable waves.
- **FR-017**: The system MUST classify wind relative to each peak as offshore, offshore-side, cross-shore, onshore-side, or onshore, per orientation and shelter, with intensity by sustained speed in km/h: **light** 0 ≤ v < 10, **moderate** 10 ≤ v < 20, **strong** 20 ≤ v < 35, **very strong** v ≥ 35. Intervals do not overlap; bands are documented and replaceable; daily rotation MUST be described. Wind classification is a quality indicator, not a requirement for surfable waves nor a sole determinant of overall quality; offshore wind MUST NOT be required.
- **FR-018**: The system MUST distinguish local wind sea from distant groundswell when data allow; report whether swell is building, peaking, or dropping when supported; estimate surfable size distinct from raw model height (FR-016); and MUST NOT treat significant wave height as breaking-wave height. Size-range uncertainty follows FR-016 and the versioned `k`/`k_range` policy. If that range crosses the 0.5 m threshold, the system MUST show the range and Uncertain rather than classify from the point estimate alone. First delivery MUST compute swell trend from consecutive hourly swell height, falling back to total wave height, when at least three samples exist inside the analysis window: last-third mean vs first-third mean, with a 10% or 0.1 m change (whichever is larger) marking building or dropping, and a middle-third maximum with both ends lower marking peaking; otherwise `steady`. Fewer than three hourly samples, or coarser input, yields `unsupported`. The trend is a labeled derived series, not a physical arrival forecast.
- **FR-019**: The system MUST classify each slot and each peak-day on the common scale or as Uncertain / Incomplete forecast. No surfable waves = an estimated range supported entirely below 0.5 m. Above the threshold, MUST apply documented non-overlapping size bands as grade ceiling: 0.5 ≤ h < 0.8 m; 0.8 ≤ h < 1.2 m; 1.2 ≤ h < 1.8 m; h ≥ 1.8 m. Quality factors follow the Quality rule: apply at most one downgrade only when two or more of swell direction, period, and wind are unfavorable; MUST NEVER lower a result with size ≥ 0.5 m below Small but surfable, and MUST NEVER raise it above the size ceiling. Each day summary MUST include a short rule-based headline, dominant swell, wind rotation through the analysis window (start vs end slot, not a daily average), per-peak condition, and which complete peaks share the highest resolved grade (“best peaks”). Fewer than two valid hours yields no best window and MUST NOT be classified as No surfable waves solely for that reason.
- **FR-020**: The system MUST base a peak's day condition on its best contiguous window of at least 2 hours within the **analysis time window 06:00–20:00 Uruguay local time** (fixed band; does not use sunrise/sunset tables and does not necessarily represent actual daylight), not on the day average. For the current day, the window may only use remaining hours in that band (see FR-024).
- **FR-021**: The system MUST report whether estimated surfable size could reach 0.5 m (real wave). Wind (including offshore or onshore), period, and swell direction grade quality but are not surfability requirements and do not alone discard wave existence. Wind direction MUST NOT have disproportionate weight or be decisive alone. Without sufficient support: Uncertain or a range. MUST NOT recommend or discourage surfing or traveling.
- **FR-022**: The system MUST show only what is needed: no wave energy, water temperature, or suggested wetsuit.
- **FR-023**: The system MUST adjust precision by horizon: today and tomorrow — 06:00/12:00/18:00 and ≥ 2 h window; day after tomorrow through day 4 — day condition and favorable slot without exact hour; days 5–10 — outlook only (US5).
- **FR-024**: For the current day, MUST consider only remaining hours and show query time. At or after 20:00 Uruguay local time, the system MUST show today as Analysis window completed, MUST NOT emit a condition or best window for today, and MUST preserve the fixed today-through-day-+4 horizon rather than extending it to day +5.
- **FR-025**: In the third stage, MUST accompany each day/peak with a brief natural-language analysis marked as automatic. First delivery MUST emit stable English `reason_codes` and Spanish labels for the rules that produced the state (size band, range crossing, two-factor downgrade, missing input, stale data, single model family, provisional profile, shared grid, unsupported window). No elaborate narrative.
- **FR-026**: The system MUST offer a medium-term outlook (days 5–10) with expected size, period, and direction and estimated arrival, distinct from operational, without per-peak/per-hour condition. Limited to swell already shown en route; phenomena not yet generating swell are evaluated in the plan. *(Third stage — US5)*

#### Uncertainty and confidence

- **FR-027**: First delivery: confidence high/medium/low via documented rules (availability, age, completeness, profile status). Reused data aged ≥ 3 h (stored-only or after download failure) MUST be treated as stale for confidence. Absence of a needed datum is NOT a favorable signal.
- **FR-028**: Confidence capped at medium with a single useful source/model or provisional peak; low if data are incomplete, stale, or clearly insufficient.
- **FR-029**: MUST NOT present scores or confidence as probabilities until contrasted with observations.
- **FR-030**: Third stage: show per-model values, disagreement, and range. First delivery: if clear disagreement is available, do not hide it and reduce confidence.
- **FR-031**: Missing confidence component = reported missing datum, not a good signal.

#### Transparency and traceability

- **FR-032**: Each current or historical condition MUST be traceable to the normalized inputs, source/provider/model identity and timestamps, effective rules and parameters, criteria version, and peak-profile version that produced it.
- **FR-033**: MUST always warn that regional models do not distinguish nearby peaks. First delivery MUST show this on the main forecast result and in JSON (`shared_regional_input`), not only in Help/About.
- **FR-035**: From the first delivery onward, the system MUST save every emitted query as an immutable local snapshot. Each snapshot MUST include query time and timezone, source/model status and provenance, issue/valid/download times, normalized inputs used, effective criteria and profile versions, effective configurable parameters including `k`, emitted conditions and confidence, data age, and incidents. Later features MAY link observations and adjustments to snapshots, but MUST NOT overwrite an original snapshot.

#### Observations and validation *(from second and later stages / US6–US7)*

- **FR-034**: Allow recording observations with the common condition scale, size, wind, and type (subjective/instrumental), without mixing types.
- **FR-036**: Allow manually entering reference forecasts, store them separately, compare with observation, without automatic extraction.
- **FR-037**: Evaluate performance by lead time (same day, 1–4 days, days 5–10 outlook): size/period/direction error, condition hits/misses, false positives, missed opportunities, slot quality; compare with references.
- **FR-038**: In US6 second stage, record discrepancies and support manual versioned reversible adjustments. In the fourth stage, evaluate adjustment proposals and automatic application per FR-047–FR-051.

#### Changes between queries *(US8)*

- **FR-039**: Compare with prior query only if < 72 h old; otherwise "no recent comparison".

#### Operation and cost

- **FR-040**: Complete a typical query in short time (SC-001).
- **FR-041**: MUST NOT require servers, scheduled jobs, or permanent processes.
- **FR-042**: Record incidents (down sources, missing data, term changes) and show them in the result.
- **FR-043**: Present UI text in Spanish and show times in Uruguay local time.

#### Flexibility and criteria adjustment

- **FR-044**: Allow changing interpretation (profiles, tolerances, height relation, wind classification, scale) without rebuilding the system or losing records.
- **FR-045**: Later stage: allow alternative prediction/interpretation methods and compare them on the same data. First delivery uses one versioned criteria set; a different method is compared only by editing that configuration and replaying a snapshot (FR-044), not by a plugin or parallel-engine framework.
- **FR-046**: Indicate in each result which criteria were used.
- **FR-047**: In the fourth stage of US6, on inconsistency report: record discrepancy, identify criteria; only with a justifiable rule and sufficient evidence apply an automatic bounded reversible adjustment. An isolated report alone is not enough to prove the general rule wrong. The second-stage workflow limits changes to explicit manual versioned reversible adjustments.
- **FR-048**: After adjustment: recalculate current, show changes, keep original and observation separate; if it disagrees with observation, report it.
- **FR-049**: Store each adjustment with date and reason and allow revert.
- **FR-050**: Bound each adjustment, check against past cases, and record when it improves the new case but worsens prior ones.
- **FR-051**: If the cause is source data: record and MUST NOT change criteria. If cause is uncertain: keep original, record observation, propose adjustment for review.

#### Growth

- **FR-052**: Be able to add new data sources without changing what the user sees or how conditions are interpreted.
- **FR-053**: Be able to offer another form of use later (e.g. web or desktop) without rebuilding functions or losing data. Today: terminal.
- **FR-054**: Be as simple as possible to use and maintain; extra complexity justified by user benefit.
- **FR-055**: Be able to grow in peaks, sources, days, and evaluation methods without changing what already works.

### Key Entities

- **Peak**: surf spot evaluated individually (name, zone, location, associated profile).
- **Peak profile**: how the peak works (orientation; ideal/acceptable/blocked swell; offshore winds; shelter by direction; useful periods; bottom; status incomplete/provisional/calibrated).
- **Interpretation criteria**: versioned configurable rules/formulas (tolerances, non-overlapping size→ceiling-grade bands, max one-step quality downgrade with Small but surfable as the floor for h ≥ 0.5 m, initial configurable model↔surfable relation **k × Hs** with k = 0.5, plausible-range uncertainty method, wind classification, condition scale, version and date).
- **Surfable criteria**: minimum estimated size 0.5 m on real wave (initially via k × Hs, k = 0.5 configurable and visible; see FR-016). Wind/period/swell direction are quality indicators, not surfability requirements. Two or more unfavorable factors may lower the ceiling grade by at most one step; one factor is not decisive; never below Small but surfable when h ≥ 0.5 m, and never raise it. A plausible range crossing 0.5 m yields Uncertain.
- **Data source**: external origin (provider, model, terms, cost, status available/degraded/down).
- **Regional forecast**: what a source/model says hour by hour (total and component swell, wind/gusts; issue, download, validity times).
- **Query**: one on-demand run (query time/timezone, sources/models and status, issue/valid/download times, criteria and profile versions, effective parameters, horizon, incidents, data age, normalized inputs, and emitted results).
- **Query snapshot**: immutable local record of an emitted query, retained from the MVP onward and linkable by later observations, discrepancies, and adjustments without overwriting the original.
- **Peak condition in a slot**: estimated size, period, direction and favorability, wind (class/intensity/favorability), condition on scale, per-model values.
- **Window**: best contiguous ≥ 2 h stretch within analysis time window 06:00–20:00 Uruguay local (start, end, condition); not necessarily actual daylight.
- **Day summary**: headline, size range, dominant swell, wind and rotation, condition per peak, best peak/slot, confidence, reason/analysis.
- **Medium-term outlook**: days 5–10 (expected size/period/direction, arrival, confidence).
- **Confidence**: level high/medium/low, components, reason for any cap.
- **Observation**: what the user actually found (date/time/peak/condition/size/wind/type/notes).
- **Reference forecast**: third-party forecast entered manually (issue date, day, peak/zone, size, rating, origin).
- **Discrepancy**: observation/reference contradicts the system (status pending/adjusted/dismissed).
- **Criteria adjustment**: applied change (what, reason, discrepancies, date, prior version for revert).
- **Performance report**: hits/misses by lead time, false positives, missed opportunities, reference comparison, suggested adjustments.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full query (command → summary on screen) takes under 30 seconds on a normal connection in at least 90% of queries.
- **SC-002**: Cost of use = zero: no function requires payment, card, or subscription.
- **SC-003**: 100% of emitted conditions, including those from prior queries, are reproducible from an immutable snapshot that identifies normalized inputs, source/model provenance and times, effective rules and parameters, criteria/profile versions, confidence, and incidents.
- **SC-004**: No peak with an incomplete profile receives a condition in any query.
- **SC-005**: A day without sufficient data is never shown as No surfable waves.
- **SC-006**: With one or more sources down (but not all), the query returns a result in 100% of test cases and shows each source's status.
- **SC-007**: The user understands today and coming days by reading the summary in under 2 minutes.
- **SC-008**: Adding a new peak requires only completing its profile, with no change to how the system works.
- **SC-009**: With ≥ 20 observations, the performance report covers each lead time that has data and explicitly states those that do not.
- **SC-010**: With ≥ 20 observations and entered references, the report compares system vs reference accuracy.
- **SC-011**: Accuracy targets are set after that first report; until then no result is presented as validated.
- **SC-012**: Changing a criterion (e.g. direction tolerance) does not require changing how the system works.
- **SC-013**: In US6, adjust only with a justifiable rule and sufficient evidence; otherwise record discrepancy and propose when appropriate; always keep original and show observation, current result, and changes separately.
- **SC-014**: Adding a peak, source, or new form of use does not force rebuilding what already works.
- **SC-015**: What already worked keeps producing the same results after adding a peak, source, or form of use.
- **SC-016**: In 100% of boundary tests, a supported size ≥ 0.5 m is never downgraded to No surfable waves, and a plausible range that crosses 0.5 m is reported as Uncertain.
- **SC-017**: In 100% of queries at or after 20:00 Uruguay local time, today is marked Analysis window completed without a condition or best window, and the horizon does not extend beyond day +4.

## Assumptions

- Single user, personal use; text terminal and internet when querying (except stored-only mode).
- User supplies profiles. Essential to interpret a peak: valid location, orientation, ideal swell, and ideal period. Known offshore winds are a useful profile attribute for quality, but not mandatory to declare surfable waves or good conditions. Optional (estimable if there is a basis): acceptable/blocked directions, minimum period, shelter, and bottom.
- Current profiles describe general ideals; reasonable variations may also produce ≥ 0.5 m and must be estimated and labeled as such.
- Swell/wind data from coarse global models; no reliable nearby directional buoys or automatic ground truth.
- Model height ≠ perceived height; initial provisional configurable relation **estimated surfable size ≈ k × Hs**, with k = 0.5 at start. Current k and result are shown to the user; not a validated physical conversion; may be revised with observations.
- The initial plausible-range uncertainty method around the 0.5 m threshold is selected and justified during Phase 0 research, remains configurable and versioned, and is not presented as a probability.
- The MVP persists immutable local query snapshots for future validation; observation capture and criteria correction remain later-stage user capabilities.
- A precise contiguous 2-hour window requires hourly data or an explicitly documented derived method. The plan must prefer hourly data and must not silently interpolate coarser samples.
- A Uruguayan reference site is a *format* model and future comparison target; **not** a system data source.
- Concrete sources are chosen in the plan; free and personal-use. Multiple models from one service ≠ independence.
- Days 5–10 outlook limited to swell already en route; not-yet-formed cyclones out of that stage's first version.
- References only by manual entry; no automatic querying of third-party sites.
- Tide, water temperature, and suggested wetsuit out of scope.
- Validation relies on queries the user makes (sparse history) and, if available, source archives.
- Anaconda, La Pedrera, and other zones out of first version.

### Known peak profiles (user-supplied; locations approximate; all provisional)

| Peak | Also called | Orientation | Bottom | Ideal swell | Ideal period | Offshore wind | Approx. location | Status |
|------|-------------|-------------|--------|-------------|--------------|---------------|------------------|--------|
| La Aguada | Arachania | E | Sand | E and ESE (SE and SSE more crossed) | 8–12 s or more | SW, W, WNW | -34.6435, -54.1546 | Provisional |
| Zanja Honda | Corumbá | S | Sand and rock | S and SE (E and ESE also) | 9–13 s or more | N, NW, W | -34.6606, -54.1859 | Provisional |
| Los Botes | — | S | Sand and rock | S and SSW | 10–14 s or more | N, NE, ENE | -34.6618, -54.1791 | Provisional |
| La Serena | — | S | Sand and rock | S and SE (SSW also) | 9–13 s or more | N, NE, ENE | -34.6612, -54.1986 | Provisional |
| La Balconada | — | S | Sand and rock | S and SE (SSW also) | 9–13 s or more | N, NE, ENE | -34.6653, -54.1630 | Provisional |

The five peaks lie within a few kilometers, less than model resolution; what distinguishes them is exposure, shelter, and bottom. The system must estimate other directions/periods/winds that also produce ≥ 0.5 m and report them as estimates.

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: Free sources and tools only; free-tier quotas documented; never activate a cost.
- **On-demand**: No permanent servers, autonomous alerts, or background processes.
- **Honesty**: Confidence and Uncertain/Incomplete visible; no probabilities without calibration; disagreements not hidden by averages.
- **Inform, don't decide**: Informs conditions and confidence; surfing/travel decision is the user's.
- **Data integrity**: Distinguish measured / forecast / inferred / empirical; model height ≠ breaking height; do not invent essential profile fields; initial size conversion is configurable, visible, and provisional.
- **Traceability**: Every current and historical condition traceable to an immutable query snapshot containing data, provenance, effective rules/parameters, profile, and criteria version.
- **Simplicity first**: First delivery = simplest path (US1–US3 + terminal); later stages only with concrete need.
- **Out of scope by default**: No accounts, payments, telemetry, or multi-user.
