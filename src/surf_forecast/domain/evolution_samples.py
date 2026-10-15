"""Sample analysis-window slots into morning/midday/afternoon rows."""

from __future__ import annotations

from typing import Any

from surf_forecast.domain.models import PeakDayForecast, SlotEvaluation
from surf_forecast.domain.windows import URUGUAY_TZ

# Inclusive of 15:00–20:00 end band via hour <= 20 and minute handling below.
_BANDS: list[tuple[str, int, int]] = [
    ("morning", 6, 11),   # [06:00, 11:00)
    ("midday", 11, 15),   # [11:00, 15:00)
    ("afternoon", 15, 21),  # [15:00, 21:00) covers through 20:xx
]


def direction_label(degrees: float | None) -> str | None:
    if degrees is None:
        return None
    sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degrees % 360) / 45.0 + 0.5) % 8
    return sectors[idx]


def sample_evolution(peak: PeakDayForecast) -> list[dict[str, Any]]:
    by_band: dict[str, SlotEvaluation] = {}
    for slot in peak.reference_slots:
        local = slot.valid_at.astimezone(URUGUAY_TZ)
        hour = local.hour
        for name, start, end in _BANDS:
            if start <= hour < end and name not in by_band:
                by_band[name] = slot
                break
    from surf_forecast.domain.presentation import CONDITION_LABELS, STATE_LABELS

    samples: list[dict[str, Any]] = []
    for name, _, _ in _BANDS:
        slot = by_band.get(name)
        if slot is None:
            continue
        condition = slot.condition_grade.value if slot.condition_grade else None
        label = CONDITION_LABELS.get(condition) if condition else STATE_LABELS.get(slot.state.value)
        wind = slot.wind
        samples.append(
            {
                "band": name,
                "local_hour": slot.valid_at.astimezone(URUGUAY_TZ).strftime("%H:%M"),
                "size_point_m": slot.size.point_m if slot.size else None,
                "period_s": slot.period_s,
                "wind_dir_label": direction_label(wind.direction_deg) if wind else None,
                "wind_speed_kmh": wind.speed_kmh if wind else None,
                "wind_intensity": wind.intensity.value if wind else None,
                "condition_label": label,
                "incomplete_or_uncertain": slot.state.value in {"uncertain", "incomplete_forecast"},
            }
        )
    return samples


def representative_wind(peak: PeakDayForecast) -> tuple[str | None, float | None, str | None]:
    """Best-effort card wind from first sample or first slot with wind."""
    samples = sample_evolution(peak)
    for sample in samples:
        if sample.get("wind_speed_kmh") is not None or sample.get("wind_dir_label"):
            return sample.get("wind_dir_label"), sample.get("wind_speed_kmh"), sample.get("wind_intensity")
    for slot in peak.reference_slots:
        if slot.wind:
            return (
                direction_label(slot.wind.direction_deg),
                slot.wind.speed_kmh,
                slot.wind.intensity.value,
            )
    return None, None, None
