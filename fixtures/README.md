# Manual verification fixtures

These files are deterministic source payloads, not an automated test suite.
Replay with an aware `--now`. Example:

```powershell
python -m surf_forecast fixtures replay fixtures\normal --now 2026-10-13T15:00:00-03:00 --json
```

## Expected outcomes

| Fixture | `--now` | Expect |
|---------|---------|--------|
| `normal/` | 2026-10-13T15:00:00-03:00 | Five local dates 2026-10-13..17, snapshot ID, no network. South-facing peaks typically `fair`. Shared-grid notice present. |
| `normal/` | 2026-10-13T20:00:00-03:00 | Today `analysis_window_completed`, no condition/window for today, horizon still through 2026-10-17. |
| `normal/` | 2026-10-13T19:59:00-03:00 | Today still has remaining hours; not completed. |
| `boundaries/three-hour/` | 2026-10-13T15:00:00-03:00 | No silent interpolation; window unsupported / `unsupported_temporal_resolution`. |
| `boundaries/one-unfavorable/` | 2026-10-13T15:00:00-03:00 | One unfavorable factor recorded; grade not lowered. |
| `boundaries/two-unfavorable/` | 2026-10-13T15:00:00-03:00 | One-step downgrade; never below `small_but_surfable` when size ≥ 0.5 m. |
| `failures/marine-down/` | 2026-10-13T15:00:00-03:00 | `incomplete_forecast`, exit 1, snapshot committed. |
| `failures/all-down/` | 2026-10-13T15:00:00-03:00 | No forecast, exit 3, no forecast snapshot. |
| `boundaries/profiles/incomplete.json` | n/a | Sample incomplete profile (missing essentials) even if status says calibrated. Compare with `config/peaks.json` via `profiles validate`. |

Live smoke (after fixtures): one normal query and one `--refresh`. Record whether the connected query finished in under 30 seconds. Do not change criteria to make a slow run pass.

## Observed 2026-10-14 (implementation pass)

- `fixtures replay fixtures/normal --now 2026-10-13T15:00:00-03:00 --json`: five dates, `fair` on all complete peaks, `shared_regional_grid`, snapshot written, exit 0.
- Same fixture at `20:00-03:00`: today `analysis_window_completed`, horizon 2026-10-13..17.
- `failures/all-down`: exit 3, JSON error `forecast_unavailable`.
- `profiles validate`: five peaks `provisional`.
- `snapshots replay` of a saved snapshot: `match: true`.
- Live `forecast --json`: Open-Meteo success in about 6 s (under the 30 s SC-001 note). TUI not driven interactively in this pass; launch with `python -m surf_forecast`.
