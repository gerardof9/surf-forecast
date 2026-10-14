# Suggested `/speckit-plan` Prompt

Copy the text below as the arguments to `/speckit-plan`.

```text
Create the implementation plan for the first delivery only (US1–US3) of the
La Paloma personalized surf forecast, including the immutable query snapshots
required by FR-035. Do not implement observation entry, discrepancy workflows,
criteria correction, US4–US9, or other later-stage user capabilities.

Produce all planning artifacts in English. Runtime terminal output must remain
in Spanish, as required by FR-043.

Plan a simple single-user CLI application that runs locally on Windows and on
demand, with no server, scheduler, account system, telemetry, web UI, or
permanent background process.

Use these technical preferences unless Phase 0 research establishes a concrete
reason to reject them:

- Python 3.12+.
- A single-project CLI architecture.
- Standard library first; add only small, well-justified dependencies.
- Clear separation between source acquisition, normalization, immutable local
  query persistence/cache, domain evaluation, and terminal presentation.
- Versioned, human-editable peak profiles and evaluation criteria.
- Small focused automated tests for calculations and high-risk boundaries.
  Do not introduce complex CI infrastructure.

Phase 0 research must:

1. Identify and compare currently available zero-cost data sources for personal
   use that provide marine and wind variables for La Paloma and cover at least
   today through day +4.
2. Verify current terms of use, attribution, quotas, API-key requirements,
   forecast horizon, update frequency, spatial/temporal resolution, and
   variables. Do not rely on source names or outdated documentation.
3. Distinguish provider, service, dataset, and underlying model. Models delivered
   through the same service must not automatically count as independent.
4. Verify whether candidates provide significant wave height, swell
   height/components, swell direction and period, wind speed/direction, gusts,
   model run time, and valid time. Mark unavailable fields explicitly.
5. Determine suitable offshore coordinates for marine data and appropriate wind
   coordinates. Verify that sampling points do not fall on land and document
   limitations from coarse regional model resolution.
6. Select the smallest viable source set. Prefer one reliable source over
   unjustified multi-source complexity; with only one useful source/model,
   enforce the medium-confidence ceiling.
7. Verify temporal resolution. Prefer hourly inputs because the specification
   requires a contiguous 2-hour best window. If candidates expose only coarser
   samples, do not silently interpolate: compare selecting another source,
   using an explicitly documented derived interpolation rule, or marking the
   window Uncertain/unavailable.
8. Define timeout, retry, cache, stale-data, offline, and partial-failure
   behavior consistent with the 3-hour reuse rule and graceful degradation.
9. Evaluate local JSON snapshots versus SQLite using simplicity, atomic writes,
   immutability, traceability, reproducibility, schema evolution, and later-stage
   linking of observations as criteria. Choose one and document alternatives.
   The MVP must save each emitted query; this is not deferred to US6.
10. Define and justify a provisional configurable method for producing the
    plausible estimated-size range around k × Hs. If the range crosses 0.5 m,
    the output must be Uncertain; do not invent a calibrated probability.
11. Verify Uruguay timezone handling and the fixed 06:00–20:00 analysis window,
    including the rule that at or after 20:00 today is marked Analysis window
    completed, receives no condition/best window, and the horizon remains today
    through day +4.

The design must explicitly model:

- Raw source responses separately from normalized forecast data.
- Provider/service/dataset/model identity and model-independence metadata.
- Peak profiles with incomplete, provisional, and calibrated states.
- Versioned evaluation criteria, including configurable k × Hs (initial k =
  0.5), a configurable plausible-range uncertainty method, non-overlapping size
  and wind bands, and the maximum one-step quality downgrade.
- The quality floor: a supported size >= 0.5 m can never be downgraded below
  Small but surfable; a plausible range crossing 0.5 m yields Uncertain.
- Query metadata: query time/timezone, source/model status and provenance,
  issue/valid/download times, normalized inputs, data age, incidents, criteria
  version, profile version, and effective parameters.
- Immutable query snapshots containing emitted conditions and confidence,
  sufficient to reproduce historical evaluations and link later observations
  without overwriting the original.
- Uncertain and Incomplete forecast as states distinct from surf-condition
  grades.
- A contiguous best-window calculation of at least 2 hours within 06:00–20:00
  Uruguay local time, without claiming unsupported temporal precision.

Define CLI contracts for at least:

- Requesting the normal forecast.
- Forcing refresh.
- Using stored data only.
- Viewing day/peak detail.
- Validating or listing peak profiles.
- Displaying source incidents, data age, criteria/profile versions, effective k,
  estimated-size range, and snapshot identifier.

Testing in the plan must remain small and risk-focused. Include boundary cases
for:

- 0.5 m surfability and every size-band boundary.
- The Small but surfable downgrade floor.
- A plausible range crossing 0.5 m.
- Every wind-speed boundary.
- The 3-hour cache boundary.
- Queries immediately before and at/after 20:00 Uruguay local time.
- A 2-hour window with hourly data and unsupported coarser data.
- Source failure, all-source failure, stale stored data, and confidence caps.
- Immutable snapshot creation and historical reproducibility.

Do not plan implementation of observation entry, manual or automatic criteria
adjustments, narrative model comparison, days 5–10 outlook, reference forecasts,
change summaries, or additional zones. Preserve simple extension seams for
later stages, but do not add speculative frameworks, services, repositories,
plugin systems, or abstractions solely for future use.

Generate:

- plan.md with completed pre- and post-design Constitution Checks.
- research.md with decision, verified evidence, rationale, and alternatives for
  every technical choice.
- data-model.md with entities, validation rules, relationships, states,
  immutability, and versioning/traceability fields.
- CLI contracts with commands, options, output fields, exit behavior, snapshot
  behavior, and degraded cases.
- quickstart.md covering installation, configuration, profile validation,
  normal query, forced refresh, stored-only mode, snapshot inspection, and
  focused tests.

Call out every assumption that cannot be verified. Do not invent source
capabilities, coordinates, temporal precision, model independence, physical
conversions, or uncertainty calibration. Any constitution violation must stop
planning unless explicitly justified in Complexity Tracking.
```
