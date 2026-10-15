# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (Surf Forecast La Paloma).
Any FAIL that must proceed requires an entry in Complexity Tracking.

- [ ] **I. Zero cost / personal use**: No paid APIs, subscriptions, or commercial
      licenses; free-tier limits documented if used
- [ ] **II. On-demand execution**: No always-on servers, daemons, or permanent
      infra; run explains which data it used
- [ ] **III. Configurable criteria**: Thresholds/weights/formulas are versioned
      and replaceable without rewriting the whole system
- [ ] **IV. Modular simplicity**: Data fetch, storage, evaluation, and
      presentation stay separable; no unjustified abstractions/deps
- [ ] **V. Honest uncertainty**: Scores are not sold as success probabilities
      unless calibrated; gaps/discrepancies are visible
- [ ] **VI. Inform, don't decide**: Personal advisory when/where briefs are
      allowed; MUST NOT claim surfable-wave guarantees or replace safety
      judgment; advice remains estimative
- [ ] **VII. Reality validation**: Improvements tied to observations / documented
      comparisons when claiming superiority
- [ ] **VIII. No invented/confused data**: Units, coords, peak orientation
      verified; observed vs model vs derived distinguished; offshore ≠ beach
      breaking height; unknowns labeled
- [ ] **IX. Traceability**: Evaluation links inputs, sources, reference time,
      rules, and criteria version
- [ ] **X. Simplicity first**: Smallest path to useful, transparent, verifiable
      evaluations; new pieces need concrete benefit
- [ ] **XI. Pragmatic verification**: Real swell/wind cases + manual review;
      small focused tests only where they cut regression risk (calcs/thresholds)
- [ ] **XII. Graceful degradation**: Source failure → partial valid results +
      explicit gaps; confidence MUST NOT rise when data is missing
- [ ] **XIII. Privacy / minimal scope**: No multi-user auth, payments,
      telemetry, or personal-data collection unless scope is explicitly changed
- [ ] **XIV. Implementation discipline**: Ambiguity → simplest free verifiable
      reversible option; cost/complexity/deps justified before build

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
