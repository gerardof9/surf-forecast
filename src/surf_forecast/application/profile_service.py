"""Read-only peak profile validation."""

from __future__ import annotations

import math
from pathlib import Path

from surf_forecast.domain.models import PeakProfile, ProfileStatus
from surf_forecast.storage.config import load_peaks


def list_profiles(path: Path | None = None) -> list[PeakProfile]:
    return [validate_profile(profile) for profile in load_peaks(path)]


def validate_profile(profile: PeakProfile) -> PeakProfile:
    errors: list[str] = []
    if not profile.peak_id:
        errors.append("missing_peak_id")
    if not profile.name:
        errors.append("missing_name")
    if math.isnan(profile.latitude) or not -90 <= profile.latitude <= 90:
        errors.append("invalid_latitude")
    if math.isnan(profile.longitude) or not -180 <= profile.longitude <= 180:
        errors.append("invalid_longitude")
    if math.isnan(profile.orientation_deg) or not 0 <= profile.orientation_deg < 360:
        errors.append("invalid_orientation")
    if not profile.ideal_swell_sectors:
        errors.append("missing_ideal_swell")
    if profile.ideal_period_s.minimum <= 0 or profile.ideal_period_s.maximum < profile.ideal_period_s.minimum:
        errors.append("invalid_ideal_period")
    for sector in profile.ideal_swell_sectors:
        for blocked in profile.blocked_swell_sectors:
            if sector.start_deg == blocked.start_deg and sector.end_deg == blocked.end_deg:
                errors.append("ideal_blocked_overlap")
    requested = profile.status
    if errors:
        profile.status = ProfileStatus.INCOMPLETE
    elif requested is ProfileStatus.CALIBRATED:
        profile.status = ProfileStatus.CALIBRATED
    else:
        profile.status = ProfileStatus.PROVISIONAL
    profile.validation_errors = errors
    return profile
