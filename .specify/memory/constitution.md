<!--
Sync Impact Report
- Version change: 1.0.0 → 1.0.1
- Modified principles: none renamed; full document translated Spanish → English (PATCH)
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ already English
  - .specify/templates/spec-template.md ✅ already English
  - .specify/templates/tasks-template.md ✅ already English
  - specs/001-la-paloma-surf-forecast/spec.md ✅ translated in same change set
- Follow-up TODOs: none
-->

# Surf Forecast La Paloma Constitution

## Core Principles

### I. Zero cost and personal use

The project is exclusively personal and non-commercial. No decision
may introduce mandatory costs or depend on paid services, subscriptions,
or commercial licenses. Free data sources, tools, and services compatible
with this use are prioritized. Free-tier quota limits MUST be documented.

**Rationale**: A personal project must not accumulate fixed costs or get
blocked by licenses; quota transparency avoids surprise failures.

### II. On-demand execution without permanent infrastructure

The system runs only when the user requests it. It MUST NOT require
always-on servers, background processes, autonomous services, or continuous
execution infrastructure. It may consume free external services and reuse
locally stored data. Each run MUST be controllable and explain which data
it used.

**Rationale**: No always-on means no hosting cost or daemon maintenance;
per-run traceability is the operational minimum.

### III. Flexibility and correctability

Evaluation criteria, weights, thresholds, and formulas MUST be configurable,
versioned, and replaceable without unnecessarily changing the rest of the
system. Real observations may justify changes to criteria. No model,
formula, or threshold MUST be treated as final without sufficient
validation.

**Rationale**: Surf is empirical; criteria must evolve with evidence
without full rewrites.

### IV. Modularity and architectural simplicity

Data acquisition, storage, condition evaluation, and result presentation
MUST keep separate responsibilities. Data sources and evaluation criteria
MUST be independently replaceable. Infrastructure, abstractions, or
dependencies that do not provide a concrete, justified benefit MUST NOT
be added.

**Rationale**: Separating concerns allows changing sources or rules without
dragging the rest; YAGNI avoids premature complexity.

### V. Honesty about uncertainty

Scores and confidence levels are evaluation indicators, not success
probabilities, unless they have been statistically calibrated and
validated. Discrepancies between sources and models MUST be made visible.
Missing data, uncertainty, and forecast limitations MUST be communicated
explicitly; they MUST NOT be hidden behind seemingly precise scores.

**Rationale**: False precision is more dangerous than declared uncertainty.

### VI. Inform, do not decide for the user

The system presents data, estimated conditions, evaluations, limitations,
and confidence levels to support the user's personal decision to travel or
surf. It MUST NOT present its classifications as guarantees that surfable
waves will exist, nor replace the user's assessment of real conditions and
safety.

**Rationale**: In-water safety is the user's responsibility; the system is
informational support.

### VII. Validation against reality

Forecast quality MUST be evaluated through real observations of surf
conditions and, when possible, comparison with existing forecasts or
references. Improvements MUST be demonstrated with documented comparisons
and consistent criteria. A source, formula, or model MUST NOT be claimed
superior without sufficient evidence.

**Rationale**: Without empirical grounding, “improvements” are opinion.

### VIII. Do not invent or confuse data

Variable names and units, source capabilities, coordinates, peak
orientations, and any other technical data MUST be verified before use.
Observed data, model forecasts, and derived estimates MUST be clearly
distinguished. In particular, forecast open-ocean wave height MUST NOT be
presented as actual beach breaking height. Unknown data MUST be identified
as such, not filled by silent assumptions.

**Rationale**: Confusing offshore height with breaking height, or silently
filling gaps, produces bad decisions.

### IX. Traceability and reproducibility

Each evaluation MUST be linkable to input data, sources consulted,
reference date and time, rules applied, and the criteria version used.
When technically feasible, the data and results needed to reproduce and
analyze prior evaluations MUST be retained.

**Rationale**: Without traceability there is no debugging or learning from
errors.

### X. Simplicity first and evidence-based evolution

The first version MUST implement the simplest path that yields useful,
transparent, and verifiable evaluations. New sources, models, features, or
components are added only when there is a concrete need and an expected
benefit that justifies their cost, complexity, and maintenance.

**Rationale**: Starting simple accelerates real learning; scaling only with
evidence avoids over-engineering.

### XI. Pragmatic verification proportional to risk

Validation MUST include real swell and wind situations, historical cases
when available, and manual review of results. Complex test infrastructure
or continuous integration is NOT required. Small, focused automated tests
are allowed when they significantly reduce error or regression risk,
especially for calculations, thresholds, and data transforms.

**Rationale**: Risk lives in numbers and transforms, not in enterprise CI
for personal use.

### XII. Graceful degradation and failure transparency

Source failure, unavailability, or missing data MUST NOT produce misleading
results or unnecessary failure of the whole system. Whenever possible,
available valid data MUST be used, and the system MUST indicate which
sources failed, what information is missing, and how that limitation
affects the result. Confidence MUST NEVER artificially increase because
information is absent.

**Rationale**: Silent failure or invented confidence when data is missing
is worse than an explicit partial result.

### XIII. Privacy and minimal scope

The project is for personal use and MUST NOT require user accounts,
multi-user authentication, payments, telemetry, or personal-data
collection. These capabilities MUST NOT be added unless scope is expressly
changed and justified.

**Rationale**: Minimal scope means less attack surface, fewer dependencies,
and alignment with personal use.

### XIV. Implementation discipline

Technical decisions MUST be consistent with these principles and the
current specification. When ambiguous, the simplest free, verifiable, and
reversible option MUST be preferred. Decisions that introduce costs,
significant complexity, new dependencies, or material architectural
changes MUST be justified explicitly before implementation.

**Rationale**: The constitution only works if implementations respect it
deliberately.

## Precedence Criterion

These principles guide all project decisions. If a proposal contradicts
any of them, the contradiction MUST be identified and resolved explicitly
before continuing. Changes to these principles MUST be deliberate and
documented, not introduced implicitly as a side effect of an
implementation decision.

## Compliance Expectations

- Every plan (`plan.md`) MUST pass the Constitution Check before research
  (Phase 0) and re-check after design (Phase 1).
- Every specification MUST respect zero cost, honesty about uncertainty,
  no invented data, and the informational (non-decisional) role.
- Tasks MUST favor modularity, traceability, and pragmatic verification;
  they MUST NOT assume accounts, complex CI, or permanent infrastructure
  by default.
- Justified violations are documented in the plan's Complexity Tracking
  with the simpler alternative rejected and the reason.

## Governance

This constitution supersedes informal habits, generic templates, and ad
hoc preferences. Amendments MUST:

1. Document the change (affected principle, reason, impact).
2. Bump the version per semver:
   - MAJOR: removal or incompatible redefinition of principles.
   - MINOR: new principle/section or material expansion of guidance.
   - PATCH: clarifications, wording, typos, non-semantic refinements.
3. Update `Last Amended` to the ISO date of the change.
4. Propagate impact to dependent templates and guides when constraints or
   work categories change.
5. Resolve conflicts with the current specification explicitly before
   implementing.

Compliance review occurs in each plan's Constitution Check and in manual
reviews of results against real observations (Principles VII and XI).
Complexity, costs, and new dependencies require prior written
justification (Principle XIV).

**Version**: 1.0.1 | **Ratified**: 2026-10-12 | **Last Amended**: 2026-10-13
