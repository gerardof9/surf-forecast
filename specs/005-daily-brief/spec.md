# Feature Specification: Daily brief (Hoy / Mañana)

**Feature Branch**: `005-daily-brief`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "Brief diario tipo Pronóstico Experto: home con exactamente 2 tarjetas (Hoy y Mañana). Cada tarjeta muestra condición, altura surfeable, headline corto, análisis en prosa natural (sin jerga técnica ni ≈◇!), mejor ventana horaria en HH:MM, y solo spots que valen la pena (filtrar por umbral de grade/score; máximo 2–3). Quitar de la home: rail DÍAS de 5 días, sección PICOS DEL DÍA, grid de PeakCards, y LEYENDA. No mostrar Tiempo ni Energía. Uso personal: el brief puede recomendar cuándo y a qué playas ir (deroga 'informar no decidir' estricto y la regla 003 de mostrar todos los picos malos en la home). Conservar motor de grades/best_window; reescribir narrative. View B opcional/secundario."

**Supersedes on home UX** (for this feature only): `003-tui-redesign` home layout (5-day rail + PICOS DEL DÍA + LEYENDA) and the “show every poor peak on the board” home rule. Forecast engine grades / `best_window` remain the source of truth; presentation and narrative change.

**Reference intent**: Match the *product shape* of Pronóstico Experto–style day cards (two day briefs, plain-language analysis, when/where)—not weather “Tiempo/Energía” metrics and not commercial branding.

## Clarifications

### Session 2026-10-15

- Q: Where does the daily brief apply (TUI only vs shared presentation)? → A: Option B — Full shared presentation contract: DayBrief (headline, prose, go-window, worth spots) is part of the common presentation payload; TUI, CLI, and JSON all consume the same brief.
- Q: What happens to peak detail (View B)? → A: Option A — Remove View B in this feature: home is only the two day cards; no peak detail screen.
- Q: What about days 3–5 beyond Mañana? → A: Option B — Engine may still evaluate a longer horizon; shared presentation exposes only Hoy and Mañana (no days 3–5 in TUI/CLI/JSON).
- Q: When multiple worth spots have different windows, which day timing is shown? → A: Option A — Use only the best worth-spot’s window (first in the ranked list).
- Q: Where does the card’s large surfeable height come from? → A: Option A — Height range of the best worth-spot; if none qualify, show n/d / no clear height (do not use below-threshold peaks).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open and know when/where today and tomorrow (Priority: P1)

As a personal La Paloma surfer, I open the app and immediately see **two day cards** (Hoy and Mañana). Each card tells me, in plain Spanish, whether the day is worth considering, **what time window is best**, and **which beaches** are worth going to—without scanning five peak cards or a legend.

**Why this priority**: This is the entire product pivot; without it the old home still fails the user’s goal.

**Independent Test**: Load a normal report fixture; home shows exactly two day cards; each has condition, surf height, short headline, natural-language analysis, a go-window phrase, and zero-to-three worth-going spots; no DÍAS rail, no PICOS DEL DÍA, no LEYENDA.

**Acceptance Scenarios**:

1. **Given** a successful report load, **When** the home view paints, **Then** exactly two day brief cards are shown (Hoy and Mañana) and no 5-day day list is present.
2. **Given** Hoy and Mañana cards, **When** I read either card, **Then** I see: condition label, surfeable height from the best worth-spot (or honest n/d when none), one-line headline, multi-sentence plain analysis, a best-time phrase from that same best spot in local `HH:MM–HH:MM` (or honest “sin pico claro / ventana amplia” / no-beach wording), and a short list of worth-going beaches (or an explicit “ningún pico claro” message).
3. **Given** the home view, **When** I scan for secondary chrome, **Then** there is no “PICOS DEL DÍA” section, no peak-card grid of all five peaks, and no LEYENDA / FR-017 legend rail.
4. **Given** analysis text on a card, **When** I read it, **Then** it uses natural Spanish without technical prefixes (`≈` / `◇` / `!`) and without jargon as the main voice (no “Hs cruda”, “ventana de análisis”, “perfil provisional” as the lead story).

---

### User Story 2 - Only beaches that are worth the trip (Priority: P1)

As a surfer, I do not want five equal peak cards when only one beach is worth going to. The card lists **only spots that pass a “vale la pena” threshold**, capped so the list stays short.

**Why this priority**: Directly addresses the user’s complaint that showing all five peaks implies equal relevance.

**Independent Test**: Fixture where only one peak is fair-or-better → only that peak appears; fixture where all are poor → explicit empty-state message, no invented beaches.

**Acceptance Scenarios**:

1. **Given** five evaluated peaks and only one meets the worth threshold, **When** the day card renders spots, **Then** only that one beach is listed (not five).
2. **Given** three or more peaks meet the threshold, **When** spots render, **Then** at most three are shown, ordered best-first.
3. **Given** no peak meets the threshold, **When** spots render, **Then** the card states clearly that no beach is clearly worth going, and does not invent names or inflate grades.
4. **Given** a listed beach, **When** shown, **Then** the name is readable and optionally a one-short-phrase reason; it is not a full technical peak card.

---

### User Story 3 - Plain “when to go” without fake precision (Priority: P2)

As a surfer, I want the best time stated simply (e.g. “mejor entre 06:00–09:00”) derived from existing best-window evaluation—not buried in a detail screen and not as raw ISO or huge minute counts.

**Why this priority**: “A qué hora conviene ir” is half of the user’s stated goal; depends on US1 prose shell.

**Independent Test**: Day with a tight best window vs a near-full-day window; verify wording differs (tight `HH:MM–HH:MM` vs honest wide-window language).

**Acceptance Scenarios**:

1. **Given** a tight best window from the engine, **When** the card shows timing, **Then** primary text uses local `HH:MM–HH:MM` (not ISO-first, not “840 min”-led).
2. **Given** a best window that spans nearly the whole analysis day, **When** timing renders, **Then** wording is honest (“ventana amplia” / “sin pico claro de hora”) plus `HH:MM–HH:MM`, not sold as a sharp peak hour.
3. **Given** multiple worth spots with different windows, **When** the day timing line renders, **Then** it shows the best (first-ranked) worth-spot’s window only—not a merge or multi-spot combined phrase.

---

### User Story 4 - Home is the only interactive surface (Priority: P3)

As a personal user, I only need the two day briefs. There is **no** peak detail screen in this product shape—when/where lives entirely on Hoy/Mañana cards.

**Why this priority**: Confirms scope cut; avoids rebuilding View B while the home is rewritten.

**Independent Test**: After load, no Enter/navigation path opens a peak-detail view; quitting/help are the only non-home exits.

**Acceptance Scenarios**:

1. **Given** the app after a successful load, **When** I use normal navigation (arrows, Enter, Esc, listed shortcuts), **Then** I never enter a peak-detail / View B screen.
2. **Given** help or status shortcuts, **When** shown, **Then** they do not advertise opening peak detail or comparing a five-peak board.

---

### Edge Cases

- **Both days poor**: Both cards still render; each says no clear beach / weak day; no invented swell story.
- **Only Hoy available / Mañana incomplete**: Mañana card shows explicit missing/limited data; does not copy Hoy silently.
- **Missing height or window**: Show `n/d` or honest omission; never fake zeros that look like measurements.
- **No worth-spots**: Height and go-window both absent/clear empty; do not backfill from discarded peaks.
- **Tied peaks**: Stable deterministic order (score then name); still respect the max-three cap.
- **Narrow terminal**: Two cards stack vertically; text remains readable; no crash.
- **Provisional / limited confidence**: May appear once as a short caution in the analysis, not as the headline voice.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Home MUST present exactly two day brief cards: **Hoy** and **Mañana** (local calendar days relative to the report).
- **FR-001a**: The shared presentation output (TUI, CLI, and JSON) MUST expose DayBrief only for **Hoy** and **Mañana**. Days beyond Mañana MUST NOT appear in presentation channels even if the engine evaluated a longer horizon.
- **FR-002**: Home MUST NOT show: a 5-day day rail, a “PICOS DEL DÍA” section, a grid of one card per peak for all peaks, or a LEYENDA / grade-legend rail.
- **FR-003**: Each day card MUST include: condition (day-level), surfeable height summary, short headline, plain-language analysis body, best-time guidance, and worth-going spots (or empty-state).
- **FR-003a**: Surfeable height on the card MUST be the derived height range of the **best (first-ranked) worth-spot**. If no worth-spot qualifies, height MUST be `n/d` / “sin altura clara”—MUST NOT pull height from below-threshold peaks.
- **FR-004**: Home MUST NOT show Tiempo (weather) or Energía metrics; those concepts are out of scope.
- **FR-005**: Analysis body MUST be natural Spanish suitable for a non-technical reader; MUST NOT lead with technical markers (`≈` / `◇` / `!`) or engine jargon as the primary voice.
- **FR-006**: Best-time guidance MUST use local `HH:MM–HH:MM` when a window exists, with honest wording for wide/full-day windows.
- **FR-006a**: When at least one worth-spot is listed, day-level go-window MUST be taken from the **best (first-ranked) worth-spot** only. When no worth-spot is listed, go-window MAY be omitted or stated as no clear beach/time—MUST NOT invent a window from below-threshold peaks.
- **FR-007**: Worth-going spots MUST be filtered: include only peaks at or above the worth threshold; show at most three; exclude the rest from the home card.
- **FR-008**: Worth threshold (default): peak condition/grade at least **fair** (or equivalent score band used by the existing day/peak rating vocabulary). Peaks below threshold MUST NOT appear on the home card.
- **FR-009**: When no peak meets the threshold, the card MUST say no beach is clearly worth going; MUST NOT invent spots or upgrade grades to fill the list.
- **FR-010**: The brief MAY explicitly recommend when and which beaches to prefer for personal decision support; it MUST still state that conditions are estimates, not guarantees of surfable waves or safety.
- **FR-011**: Surfeable height on the card MUST remain a derived/estimated range (not presented as raw offshore Hs as breaking height).
- **FR-012**: Existing evaluation outputs (grades, scores, `best_window`) MUST remain the factual basis; this feature rewrites presentation and narrative, not the core scoring formulas (unless a tiny threshold mapping is needed for FR-007/FR-008).
- **FR-013**: The interactive TUI for this feature MUST NOT include a peak-detail (View B) screen; when/where MUST be fully answered on the two day cards alone.
- **FR-014**: Dual honesty of timestamps (data validity vs consultation time) MUST remain visible somewhere on home or card chrome.
- **FR-015**: Keyboard/help copy on home MUST describe Hoy/Mañana navigation (if any) and MUST NOT instruct users to compare five peak cards or open a legend that no longer exists.
- **FR-016**: DayBrief fields (headline, plain analysis, go-window text, worth spots, condition, height summary) MUST be produced once in the shared presentation contract so TUI, CLI, and JSON expose the same brief content (channel-specific layout only; no divergent technical narrative on other channels).

### Key Entities

- **DayBrief**: One calendar day summary in the shared presentation contract (rendered as home cards in TUI and as equivalent day sections in CLI/JSON)—condition, height from best worth-spot (or n/d), headline, analysis prose, go-window from that same spot (or absent), ordered worth spots, timestamps/meta needed for honesty.
- **WorthSpot**: A beach/peak that passed the worth filter—display name, optional short reason, optional rank order.
- **GoWindow**: Human-facing timing guidance derived from the best worth-spot’s engine best-window (tight vs wide semantics); absent when no worth-spot qualifies.
- **DayCondition**: Existing day-level rating vocabulary reused as the card’s condition pill/label.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On first paint of a normal report, a first-time user can state (a) whether Hoy is worth considering, (b) a preferred time window, and (c) up to three beach names—without opening detail—within one short read of the Hoy card.
- **SC-002**: In fixtures where only one peak is worth going, 100% of home spot lists for that day show that single beach and zero of the below-threshold peaks.
- **SC-003**: Home chrome checklist: zero occurrences of sections titled PICOS DEL DÍA or LEYENDA; zero 5-peak comparable card grids on home.
- **SC-006**: Presented day count is exactly two (Hoy, Mañana) in TUI, CLI, and JSON for a normal successful report.
- **SC-004**: In a side-by-side review of 5 sample days, reviewers rate the analysis as “plain language / actionable” rather than “technical log” for at least 4 of 5 days.
- **SC-005**: Wide-window days never present a large minute count as the primary timing message; tight windows always show local clock times.

## Assumptions

- Target user is the project owner (personal, non-commercial); Spanish UI copy.
- “Mañana” means the next local calendar day after Hoy in the report, not a second speculative model.
- Longer engine horizons (days 3–5) may still be computed for internal reuse; they are omitted from all presentation channels in this feature.
- Worth threshold defaults to fair-or-better in the existing grade vocabulary; max three spots is enough.
- Tiempo/Energía and expert photo/branding from third-party sites are explicitly out of scope.
- Peak-detail View B is **removed** from the interactive product for this feature (not merely de-emphasized). Technical evolution tables are out of the interactive path; raw evaluation data may still exist internally for building DayBrief.
- Constitution Principle VI is **narrowly relaxed for home copy**: the app may say “conviene ir a X a la hora Y” as personal advisory language, while Principle V/VIII honesty (no guarantees, no invented data, no Hs-as-breaking) still binds.
- Specs `003` / `004` remain historical for engine/visual craft; **home information architecture follows this `005` spec**.
- Presentation channels share one DayBrief; only chrome/layout differs by channel.

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: No paid services; personal-only product.
- **On-demand**: Local/on-demand run; no always-on infrastructure.
- **Honesty**: Uncertainty and limitations remain representable; recommendations are indicators, not guarantees of waves or safety (**FR-010**).
- **Data integrity**: Observed vs forecast vs derived stay distinct; unknown values not invented; height remains derived (**FR-011**).
- **Principle VI tension (explicit)**: This feature **intentionally** allows when/where advisory wording on the home brief for personal use. It does **not** claim guaranteed surf or replace in-water judgment. A future constitution MINOR amendment may formalize “advisory brief allowed for personal use”; until then, this spec documents the justified exception for home narrative only.
- **Out of scope by default**: Accounts, payments, telemetry, multi-user—unchanged.
- **Supersession note**: Showing only worth-going spots on home **contradicts** older 003 “poor peaks must remain visible on the board.” That older home rule is **superseded by FR-007–FR-009** for this feature’s home view.
