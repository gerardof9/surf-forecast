# Non-interactive Command Contract

**Executable form**: `py -m surf_forecast`  
**Human output**: Spanish  
**JSON identifiers**: stable English `snake_case`  
**JSON schema version**: required on every JSON document

## General rules

- `--json` writes one JSON document to stdout; diagnostics go to stderr.
- Without `--json`, human-readable output is Spanish.
- `--now ISO-8601` supplies a deterministic aware reference instant. A value
  without an offset is invalid.
- `--fixture PATH` replaces all network acquisition with deterministic source
  payloads under `PATH`.
- `--refresh` and `--stored-only` are mutually exclusive.
- Forecast-producing commands always commit the immutable snapshot before
  reporting success.
- Rendering an existing snapshot does not create another snapshot.
- Human and JSON adapters consume the same `ForecastPresentation`.

## Commands

### `tui`

```powershell
py -m surf_forecast tui
```

Launches the TUI contract. This is also the default with no subcommand.

### `forecast`

```powershell
py -m surf_forecast forecast [--refresh | --stored-only] [--json]
    [--now ISO-8601] [--fixture PATH]
```

Produces today through day +4 for all complete profiles, profile validation
summary, source states, incidents, confidence, versions, and snapshot ID.

Mode rules:

- default: use cache if younger than 3 hours; otherwise try live.
- `--refresh`: bypass freshness reuse and try live; may fall back explicitly.
- `--stored-only`: no network; use cached normalized inputs or latest stored
  snapshot according to availability and label the exact origin.
- `--fixture`: no network; fixture metadata determines source outcomes.

### `detail`

```powershell
py -m surf_forecast detail --date YYYY-MM-DD --peak PEAK_ID
    [--snapshot SNAPSHOT_ID] [--json]
```

Reads the latest snapshot by default or the specified immutable snapshot.
Returns reference slots, best window, inputs, estimated point/range, wind
assessment, reason codes, confidence, provenance, and versions. It does not
run a new query or create a snapshot.

### `profiles list`

```powershell
py -m surf_forecast profiles list [--json]
```

Lists peak ID, name/aliases, status, version, and estimated/unknown fields.

### `profiles validate`

```powershell
py -m surf_forecast profiles validate [--json]
```

Validates schema, essential fields, numeric ranges, direction-sector
coherence, uniqueness, and profile status. It never edits files.

### `sources status`

```powershell
py -m surf_forecast sources status [--snapshot SNAPSHOT_ID] [--json]
```

Displays provider/service/dataset/model, requested/resolved coordinates,
valid/download/model-run timestamps and availability, cache state, age,
incidents, terms, attribution, and license.

### `snapshots show`

```powershell
py -m surf_forecast snapshots show SNAPSHOT_ID [--json]
```

Inspects immutable snapshot metadata and optionally the human-readable saved
forecast. It does not modify or duplicate the snapshot.

### `snapshots replay`

```powershell
py -m surf_forecast snapshots replay SNAPSHOT_ID
    [--now ISO-8601] [--json]
```

Re-evaluates the snapshot's normalized inputs using the configuration copies
embedded in that snapshot and compares canonical result hashes. It does not
write a new snapshot. Success means the replayed canonical result matches the
saved result.

### `fixtures replay`

```powershell
py -m surf_forecast fixtures replay PATH --now ISO-8601 [--json]
```

Runs the normal application evaluation path against deterministic fixtures.
It writes a snapshot under a fixture/replay marker so snapshot persistence and
immutability can be verified without network access.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Complete requested operation; forecast may contain explicit per-peak Uncertain states |
| `1` | Degraded forecast emitted (partial source failure, stale fallback, or Incomplete forecast) and snapshot committed |
| `2` | Invalid command, option combination, configuration, profile, or fixture |
| `3` | No forecast could be emitted (no usable data/snapshot) |
| `4` | Snapshot/cache persistence or integrity failure |
| `5` | Replay mismatch |
| `130` | User cancellation |

JSON remains valid on exit `1` and contains `overall_status: "degraded"`.
On codes `2`–`5`, `--json` returns the error envelope below when possible.

## JSON envelope

Successful forecast/detail documents conform to
`schemas/forecast-output.schema.json`.

Abbreviated shape (the schema, not this shortened illustration, defines all
required fields):

```json
{
  "schema_version": "1.0.0",
  "overall_status": "complete",
  "snapshot_id": "q_20261013T221500Z_a1b2c3d4",
  "query": {
    "mode": "normal",
    "reference_time": "2026-10-13T22:15:00Z",
    "timezone": "America/Montevideo",
    "horizon_start": "2026-10-13",
    "horizon_end": "2026-10-17"
  },
  "days": [
    {
      "local_date": "2026-10-14",
      "state": "resolved",
      "peaks": [
        {
          "peak_id": "la_aguada",
          "state": "resolved",
          "condition": "small_but_surfable",
          "condition_label": "Olas pequeñas pero surfeables"
        }
      ]
    }
  ]
}
```

Machine logic MUST use `condition`, never `condition_label`.

## Error envelope

```json
{
  "schema_version": "1.0.0",
  "error": {
    "code": "configuration_invalid",
    "message": "Spanish human-readable message",
    "details": {}
  }
}
```

`error.code` is stable English; `message` is Spanish.

## Snapshot behavior

Creates a new snapshot:

- startup/default TUI query;
- TUI forced refresh or stored-only query;
- `forecast` in any mode;
- `fixtures replay`.

Does not create a snapshot:

- navigating or filtering TUI data;
- `detail`;
- `profiles *`;
- `sources status`;
- `snapshots show`;
- `snapshots replay`.

There is no `--no-snapshot` option for forecast-producing commands.

## Degraded cases

| Case | Output | Exit |
|------|--------|------|
| One source fails, no adequate replacement | Valid available data + `incomplete_forecast` + incidents | `1` |
| Live fails, fresh cache succeeds | Forecast labeled fresh cache | `0` |
| Live fails, only stale cache succeeds | Forecast labeled stale, confidence low | `1` |
| All fail, latest snapshot requested in stored-only mode | Saved forecast, exact age/origin | `1` |
| All fail, no cache/snapshot | Error `forecast_unavailable` | `3` |
| Range crosses 0.5 m | `uncertain`, range and reason | `0` unless another degradation applies |
| Query at/after 20:00 local | Today `analysis_window_completed`; tomorrow–day+4 present | `0` |
| Snapshot commit fails | No success result; persistence error | `4` |
