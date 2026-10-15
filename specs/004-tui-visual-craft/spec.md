# Feature Specification: TUI visual craft (graphic layer)

**Feature Branch**: `004-tui-visual-craft`  
**Created**: 2026-10-15  
**Status**: Draft  
**Input**: User request for a binding graphic-layer specification so the Textual TUI matches `modelo.png` hierarchy and the professional quality bar of LazyGit / btop / K9s / Wireshark—without changing the forecast engine. Evidence: `references/detalle.pdf` captures vs `references/modelo.png`; diagnosis in `references/diagnostico2.pdf`.

**Binding graphic contract**: [`graphic-layer.md`](./graphic-layer.md) (v1.0.0).  
**Frozen product rules** (do not reopen): presentation schema 1.1.0, FR-017 vocabulary, honesty/narrative rules, View A/B semantics already shipped.

## Clarifications

### Session 2026-10-15

- Q: How is `Frame` chrome implemented? → A: Option A — Custom `Frame` widget with Unicode box-drawing and title embedded in the top border (LazyGit / db-log-explorer style); focus changes border color/weight.
- Q: How does peak focus/selection work on View A? → A: Option B — Primary keyboard focus stays on the day list; `←→` moves the active peak with strong card chrome; `Enter` opens View B for the active peak.
- Q: How much decorative iconography from `modelo.png`? → A: Option B — Minimal stable Unicode set: rating stars, condition `●`, best-of-day `★`; optional reliable wind arrows; no app-like wave/pin/compass iconography or Nerd Font dependency.
- Q: How to present a best window that spans nearly the whole analysis day? → A: Option A — Still show the callout with an honest “ventana amplia / día completo” label plus local `HH:MM–HH:MM`; do not emphasize huge minute counts as if it were a tight peak window.
- Q: How is visual “done” validated? → A: Option B — Mandatory manual screenshots vs `modelo.png` hierarchy (VS-A1…VS-N1) plus Textual `run_test` smoke for format hygiene, Enter/Esc navigation, and detectable anti-pattern strings; no pixel-diff CI gate.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View A reads as a surf report board (Priority: P1)

As a La Paloma surfer, I want the daily view to show framed analysis, a hero day rating, and a row of comparable peak cards so I can scan the day like a real report—not a log dump.

**Why this priority**: Largest gap vs `references/modelo.png` and vs `references/detalle_capture_0.png`.

**Independent Test**: Open View A on a wide terminal with a normal fixture; verify header dual timestamps + status pill, analysis/rating frames, and up to five structured peak cards with FR-017 badges and formatted metrics.

**Acceptance Scenarios**:

1. **Given** a wide terminal (≥ 130 columns) and five peaks, **When** View A renders, **Then** peak cards appear in a multi-column row (up to 5), each with badge, size, period, wind, and score glyphs per `graphic-layer.md`.
2. **Given** day analysis sentences with mixed kinds, **When** View A renders, **Then** fact / interpretation / limitation are visually distinct and limitations are not the only visible content when facts exist.
3. **Given** a day rating, **When** View A renders `VALORACIÓN DEL DÍA`, **Then** Unicode stars match the numeric score and ASCII `*`/`-` stars are absent.
4. **Given** View A after load, **When** the shell is ready, **Then** keyboard focus remains on the day list; `←→` changes the active peak card highlight without moving day-list focus; `Enter` opens View B for that active peak.

---

### User Story 2 - View B is a three-zone detail board (Priority: P1)

As a surfer, I want peak detail to show summary, evolution, and window first—with technical data secondary—so timing decisions are obvious.

**Why this priority**: `references/detalle_capture_1.png` is a vertical diagnostic stack; `references/modelo.png` is a board.

**Independent Test**: Open View B for a peak with evolution samples; confirm summary | evolution/window/analysis hierarchy, local `HH:MM` times, rounded meters, collapsed tech by default.

**Acceptance Scenarios**:

1. **Given** View B opens, **When** first paint completes, **Then** technical details start collapsed and do not dominate the viewport.
2. **Given** size/period/wind in the payload, **When** summary renders, **Then** meters use one decimal (comma), period is not a spurious `0 s` for missing data, and no raw multi-decimal floats appear.
3. **Given** a best window from the engine, **When** the callout renders, **Then** primary times are local `HH:MM–HH:MM` (not ISO-first).
4. **Given** a best window whose duration spans the full (or nearly full) analysis day, **When** the callout renders, **Then** it uses an honest wide-window label (e.g. “Ventana amplia (día completo)”) with `HH:MM–HH:MM` and MUST NOT present a large minute count as the primary emphasis.

---

### User Story 3 - Professional chrome and hygiene (Priority: P2)

As a user of terminal tools like LazyGit/btop, I want framed panels, a distinct StatusBar, and semantic condition color so the app feels operational and trustworthy.

**Why this priority**: Establishes the design system that makes US1/US2 sustainable.

**Independent Test**: Screenshot VS-A1 / VS-B1 against `graphic-layer.md` gates; verify Frame title-in-border, StatusBar not framed, FR-017 colors reinforce labels.

**Acceptance Scenarios**:

1. **Given** any primary content region, **When** rendered, **Then** it uses Frame chrome (title in top border) rather than floating titles over bare canvas.
2. **Given** the footer, **When** rendered, **Then** StatusBar is a dedicated bar (not a content Frame) with grouped shortcuts.
3. **Given** condition badges, **When** color is unavailable, **Then** full Spanish FR-017 text remains readable.

---

### Edge Cases

- Narrow terminal (&lt; 90): stack layout; legend moves to Help; no crash; analysis scrolls.
- Window-completed day: one banner; cards keep comparable fields from payload.
- Missing period/size: `n/d` labels, never fake zeros that look like measurements.
- Provisional profile: visible once in summary/meta; not spammed on every line.
- Full-day / near-full-day `best_window`: honest “ventana amplia” callout, not hidden and not ISO/`840 min`-led.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-G01**: TUI MUST implement the component catalog and layout wireframes in [`graphic-layer.md`](./graphic-layer.md).
- **FR-G11**: Primary content regions MUST use a custom `Frame` widget with Unicode box-drawing (`╭╮╰╯`) and the section title embedded in the top border; Textual CSS `border` alone with a floating/inner-only title is non-compliant for framed content. Focus MUST restyle the frame border (and matching title color).
- **FR-G12**: View A MUST keep primary keyboard focus on the day list; peak cards are selection-highlighted via `←→` (not independently focus-trapping); `Enter` opens View B for the active peak.
- **FR-G13**: Iconography MUST stay minimal: Unicode rating stars, FR-017 condition `●`, best-of-day `★`, and optional wind arrows only when glyphs are reliable across common Windows terminals. Decorative wave/map-pin/compass icons and Nerd Font requirements are out of scope.
- **FR-G14**: When `best_window` spans the full or nearly full analysis day, View B MUST still show the callout with an honest wide-window label and local `HH:MM–HH:MM`; it MUST NOT lead with a large raw minute duration as if the window were tight. Threshold for “nearly full”: duration ≥ 6 hours **or** window covers the entire documented analysis band (06:00–20:00 UYT).
- **FR-G15**: Sign-off MUST include (1) manual screenshot review for VS-A1, VS-A2, VS-B1, VS-B2, VS-N1 against `modelo.png` hierarchy, and (2) automated Textual `run_test` smoke covering format hygiene (no raw multi-decimal floats in primary fields), Enter→View B / Esc back, and absence of documented anti-pattern strings where detectable. Pixel-diff / screenshot CI is out of scope.
- **FR-G02**: Display formatters MUST enforce the hygiene table in `graphic-layer.md` §5 for all primary View A/B fields.
- **FR-G03**: View A peak grid MUST allow up to five columns on wide terminals; a hard max of two columns on wide terminals is non-compliant.
- **FR-G04**: View B MUST use a multi-zone board (summary + evolution/window/analysis + secondary tech), not a homogeneous vertical dump of equal panels.
- **FR-G05**: Rating glyphs MUST be Unicode stars consistent with the numeric score; ASCII star substitutes are forbidden in primary UI.
- **FR-G06**: Semantic condition colors MUST follow FR-017 roles in `graphic-layer.md` §4.2 and MUST NOT be the sole signal.
- **FR-G07**: StatusBar MUST follow the LazyGit-style footer contract (not a framed content panel).
- **FR-G08**: Implementation MUST NOT change engine evaluation thresholds, invent meteorology, or diverge from frozen presentation 1.1.0 field semantics.
- **FR-G09**: Feature sign-off MUST pass visual gates VS-A1, VS-A2, VS-B1, VS-B2, VS-N1 in `graphic-layer.md` §12.
- **FR-G10**: Widget code MUST NOT override Textual `Widget._render` for content population (use `_populate` / `_apply`).

### Key Entities

- **Graphic theme**: Token roles for chrome, text, and FR-017 conditions.
- **Frame / PeakCard / RatingHero / EvolutionTable / Badge / StatusBar**: Catalog components in `graphic-layer.md` §6.
- **Display formatter**: Pure formatting over presentation 1.1.0 fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: SC-G01…SC-G06 in `graphic-layer.md` §15 pass.
- **SC-002**: Side-by-side review vs `modelo.png` passes hierarchy recognition (SC-V01 ≤ 5 seconds).
- **SC-003**: `scripts/check_report_presentation.py` and normal fixture replay still exit successfully after graphic changes.
- **SC-004**: No primary-UI occurrence of raw multi-decimal floats on `fixtures/normal` View A/B screenshots.
- **SC-005**: A Textual `run_test` smoke (or equivalent script) fails the check when primary View A/B text contains raw multi-decimal float patterns or when Enter/Esc peak-detail navigation raises.

## Assumptions

- Textual remains the TUI toolkit; no GUI rewrite.
- Presentation schema 1.1.0 remains the data source (frozen; not redesigned in this feature).
- `references/modelo.png` / `references/mock2.png` bind composition; mock numbers are not oracles.
- Exact hex colors may be tuned if roles stay distinguishable.
- Decorative mock icons (wave, pin, compass) are intentionally not replicated; scan path relies on badges, metrics columns, and stars.
- Visual acceptance is dual: human screenshot gates + lightweight Textual smoke; not pixel regression CI.
- Active Spec Kit feature directory is `specs/004-tui-visual-craft` only (`.specify/feature.json`).

## Constitution Constraints *(mandatory alignment)*

- **Personal / zero cost**: No paid UI services or fonts that impose cost.
- **On-demand**: Graphic layer is local Textual only.
- **Honesty**: Visual polish MUST NOT hide uncertainty, incomplete data, or provisional profiles.
- **Modularity**: Graphic layer stays in `presentation/tui`; domain evaluation untouched.
- **Inform, do not decide**: Badges and ratings remain indicators; no “go surf” imperative chrome.
