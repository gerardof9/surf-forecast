"""Confidence caps for the first delivery."""

from __future__ import annotations

from surf_forecast.domain.models import (
    ConfidenceAssessment,
    ConfidenceLevel,
    ForecastState,
    PeakProfile,
    ProfileStatus,
    SourceFetch,
    FetchStatus,
)

SINGLE_FAMILY_CAP = "single_model_family"
PROVISIONAL_CAP = "provisional_profile"
STALE_DEGRADATION = "stale_data"
MISSING_DEGRADATION = "missing_required_input"


def assess(
    *,
    profile: PeakProfile,
    state: ForecastState,
    fetches: list[SourceFetch],
    independence_groups: set[str],
) -> ConfidenceAssessment:
    caps: list[str] = []
    degradations: list[str] = []
    if len(independence_groups) <= 1:
        caps.append(SINGLE_FAMILY_CAP)
    if profile.status == ProfileStatus.PROVISIONAL:
        caps.append(PROVISIONAL_CAP)
    if profile.status == ProfileStatus.CALIBRATED and len(independence_groups) <= 1:
        caps.append(SINGLE_FAMILY_CAP)
    if any(fetch.status == FetchStatus.STALE_CACHE for fetch in fetches):
        degradations.append(STALE_DEGRADATION)
    if state == ForecastState.INCOMPLETE_FORECAST:
        degradations.append(MISSING_DEGRADATION)
    if degradations:
        level = ConfidenceLevel.LOW
    else:
        level = ConfidenceLevel.MEDIUM
    return ConfidenceAssessment(
        level=level,
        caps=sorted(set(caps)),
        degradations=degradations,
        explanation_code=degradations[0] if degradations else (caps[0] if caps else "ok"),
    )
