"""Swappable source acquisition boundary. No Open-Meteo or Textual imports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from surf_forecast.domain.models import (
    GeoPoint,
    Incident,
    NormalizedMarineHour,
    NormalizedWindHour,
    SourceDescriptor,
    SourceFetch,
)


@dataclass
class AcquisitionResult:
    fetches: list[SourceFetch]
    descriptors: list[SourceDescriptor]
    marine_hours: list[NormalizedMarineHour]
    wind_hours: list[NormalizedWindHour]
    incidents: list[Incident] = field(default_factory=list)
    raw_payloads: dict[str, Any] = field(default_factory=dict)


class SourceAdapter(Protocol):
    def acquire(self, now: datetime, *, force_refresh: bool, stored_only: bool) -> AcquisitionResult:
        ...


MARINE_COORDINATE = GeoPoint(-34.70, -54.10)
WIND_COORDINATE = GeoPoint(-34.66, -54.18)

MARINE_DESCRIPTOR = SourceDescriptor(
    source_id="open_meteo_gfs_wave_025",
    provider="Open-Meteo",
    service="Marine API",
    dataset="NCEP GFS Wave 0.25°",
    model="ncep_gfswave025",
    model_family="noaa_ncep_gfs",
    independence_group="noaa_ncep_gfs",
    terms_url="https://open-meteo.com/en/terms",
    license="CC-BY-4.0",
    attribution="Datos: Open-Meteo (CC BY 4.0)",
    native_temporal_resolution_minutes=60,
    spatial_resolution_km=25,
    model_run_time_available=False,
    requested_coordinate=MARINE_COORDINATE,
)

WIND_DESCRIPTOR = SourceDescriptor(
    source_id="open_meteo_gfs_wind",
    provider="Open-Meteo",
    service="GFS API",
    dataset="NCEP GFS atmosphere",
    model="gfs_seamless",
    model_family="noaa_ncep_gfs",
    independence_group="noaa_ncep_gfs",
    terms_url="https://open-meteo.com/en/terms",
    license="CC-BY-4.0",
    attribution="Datos: Open-Meteo (CC BY 4.0)",
    native_temporal_resolution_minutes=60,
    spatial_resolution_km=25,
    model_run_time_available=False,
    requested_coordinate=WIND_COORDINATE,
)
