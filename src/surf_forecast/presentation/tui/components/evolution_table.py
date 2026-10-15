"""Sampled evolution table for View B."""

from __future__ import annotations

from typing import Any

from surf_forecast.presentation.tui.components.frame import Frame
from surf_forecast.presentation.tui.formatters import (
    format_hhmm_local,
    format_meters_point,
    format_wind,
)


class EvolutionTable(Frame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__("EVOLUCIÓN (muestras)", "", **kwargs)

    def set_samples(self, samples: list[dict[str, Any]] | None) -> None:
        samples = samples or []
        if not samples:
            self.set_body("Sin muestras en la ventana de análisis.")
            return
        lines = ["Hora   Tamaño     Viento              Condición"]
        for sample in samples:
            hour = format_hhmm_local(sample.get("local_hour") or sample.get("local_time"))
            if hour == "—" and sample.get("local_hour"):
                hour = str(sample.get("local_hour"))[:5]
            size_s = format_meters_point(sample.get("size_point_m"))
            wind = format_wind(
                dir_label=sample.get("wind_dir_label"),
                intensity=sample.get("wind_intensity"),
                speed_kmh=sample.get("wind_speed_kmh"),
            )
            cond = sample.get("condition_label") or "—"
            lines.append(f"{hour:<6} {size_s:<10} {wind:<19} ● {cond}")
        self.set_body("\n".join(lines))
