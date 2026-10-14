"""Generate deterministic Open-Meteo-shaped fixtures. Run from repo root."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START = datetime(2026, 10, 13, 0, 0, tzinfo=timezone.utc)
HOURS = 120


def series(kind: str) -> dict:
    times = [(START + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(HOURS)]
    if kind == "marine":
        wave = []
        swell = []
        period = []
        direction = []
        for i in range(HOURS):
            local_hour = (START + timedelta(hours=i)).hour
            base = 2.0 if 10 <= (local_hour - 3) % 24 <= 20 else 1.6
            wave.append(round(base, 2))
            swell.append(round(base * 0.85, 2))
            period.append(11.0)
            direction.append(180.0)
        return {
            "latitude": -34.75,
            "longitude": -54.0,
            "generationtime_ms": 0.1,
            "utc_offset_seconds": 0,
            "timezone": "GMT",
            "elevation": 0.0,
            "hourly_units": {"time": "iso8601", "wave_height": "m"},
            "hourly": {
                "time": times,
                "wave_height": wave,
                "wave_direction": direction,
                "wave_period": period,
                "swell_wave_height": swell,
                "swell_wave_direction": direction,
                "swell_wave_period": period,
                "wind_wave_height": [0.3] * HOURS,
                "wind_wave_direction": [180.0] * HOURS,
                "wind_wave_period": [4.0] * HOURS,
            },
        }
    wind_dir = [0.0] * HOURS
    speed = [8.0] * HOURS
    return {
        "latitude": -34.61763,
        "longitude": -54.140625,
        "generationtime_ms": 0.1,
        "utc_offset_seconds": 0,
        "timezone": "GMT",
        "elevation": 8.0,
        "hourly_units": {"time": "iso8601", "wind_speed_10m": "km/h"},
        "hourly": {
            "time": times,
            "wind_speed_10m": speed,
            "wind_direction_10m": wind_dir,
            "wind_gusts_10m": [12.0] * HOURS,
        },
    }


def dump(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    marine = series("marine")
    wind = series("wind")
    dump(ROOT / "normal" / "marine.json", marine)
    dump(ROOT / "normal" / "wind.json", wind)

    coarse_times = marine["hourly"]["time"][::3]
    coarse = json.loads(json.dumps(marine))
    for key, values in coarse["hourly"].items():
        if key == "time":
            coarse["hourly"][key] = coarse_times
        else:
            coarse["hourly"][key] = values[::3]
    dump(ROOT / "boundaries" / "three-hour" / "marine.json", coarse)
    dump(ROOT / "boundaries" / "three-hour" / "wind.json", wind)

    onshore = json.loads(json.dumps(wind))
    onshore["hourly"]["wind_direction_10m"] = [180.0] * HOURS
    onshore["hourly"]["wind_speed_10m"] = [25.0] * HOURS
    dump(ROOT / "boundaries" / "two-unfavorable" / "marine.json", marine)
    dump(ROOT / "boundaries" / "two-unfavorable" / "wind.json", onshore)

    light_onshore = json.loads(json.dumps(wind))
    light_onshore["hourly"]["wind_direction_10m"] = [180.0] * HOURS
    light_onshore["hourly"]["wind_speed_10m"] = [8.0] * HOURS
    dump(ROOT / "boundaries" / "one-unfavorable" / "marine.json", marine)
    dump(ROOT / "boundaries" / "one-unfavorable" / "wind.json", light_onshore)

    dump(ROOT / "failures" / "marine-down" / "sources.json", {"marine": None, "wind": wind})
    dump(ROOT / "failures" / "all-down" / "sources.json", {"marine": None, "wind": None})

    dump(
        ROOT / "boundaries" / "profiles" / "incomplete.json",
        {
            "schema_version": "1.0.0",
            "peaks": [
                {
                    "peak_id": "incomplete_peak",
                    "name": "Incompleto",
                    "zone_id": "la_paloma",
                    "status": "calibrated",
                    "profile_version": "1.0.0",
                    "schema_version": "1.0.0",
                    "updated_at": "2026-10-13T00:00:00Z",
                    "estimated_fields": [],
                }
            ],
        },
    )


if __name__ == "__main__":
    main()
