"""Size, quality, trend, and day-summary evaluation."""

from __future__ import annotations

from datetime import datetime

from surf_forecast.domain.confidence import assess
from surf_forecast.domain.models import (
    GRADE_ORDER,
    BestWindow,
    CriteriaSet,
    DaySummary,
    ForecastState,
    NormalizedMarineHour,
    NormalizedWindHour,
    PeakDayForecast,
    PeakProfile,
    QualityClass,
    QueryRequest,
    SlotEvaluation,
    SourceFetch,
    SurfGrade,
    SurfableSizeEstimate,
    SwellTrend,
    SwellTrendState,
    WindAssessment,
    WindIntensity,
    WindRelative,
)
from surf_forecast.domain.windows import (
    URUGUAY_TZ,
    analysis_window_completed,
    day_offset,
    horizon_dates,
    is_today,
    native_step_minutes,
    part_of_day_label,
    select_best_window,
    slot_in_analysis_window,
    slot_in_calendar_analysis_window,
)


def circular_delta(left: float, right: float) -> float:
    return abs((left - right + 180) % 360 - 180)


def size_estimate(hs: float, criteria: CriteriaSet) -> SurfableSizeEstimate:
    return SurfableSizeEstimate(
        raw_hs_m=hs,
        point_m=criteria.point_k * hs,
        minimum_m=criteria.range_k_low * hs,
        maximum_m=criteria.range_k_high * hs,
        point_k=criteria.point_k,
        range_k_low=criteria.range_k_low,
        range_k_high=criteria.range_k_high,
    )


def ceiling_from_size(size: SurfableSizeEstimate, criteria: CriteriaSet) -> tuple[ForecastState, SurfGrade | None]:
    if size.minimum_m < criteria.surfable_threshold_m <= size.maximum_m:
        return ForecastState.UNCERTAIN, None
    if size.maximum_m < criteria.surfable_threshold_m:
        return ForecastState.RESOLVED, SurfGrade.NO_SURFABLE_WAVES
    for band in criteria.size_bands:
        if band.contains(size.point_m):
            return ForecastState.RESOLVED, band.grade
    return ForecastState.RESOLVED, SurfGrade.VERY_GOOD


def wind_intensity(speed: float, criteria: CriteriaSet) -> WindIntensity:
    for band in criteria.wind_speed_bands:
        if band.contains(speed):
            return band.intensity
    return WindIntensity.UNKNOWN


def wind_relative(direction: float, profile: PeakProfile) -> WindRelative:
    if any(sector.contains(direction) for sector in profile.offshore_wind_sectors):
        return WindRelative.OFFSHORE
    delta = circular_delta(direction, profile.orientation_deg)
    if delta < 22.5:
        return WindRelative.ONSHORE
    if delta < 67.5:
        return WindRelative.ONSHORE_SIDE
    if delta < 112.5:
        return WindRelative.CROSS_SHORE
    if delta < 157.5:
        return WindRelative.OFFSHORE_SIDE
    return WindRelative.OFFSHORE


def wind_quality(relative: WindRelative, intensity: WindIntensity, criteria: CriteriaSet) -> QualityClass:
    if relative is WindRelative.UNKNOWN or intensity is WindIntensity.UNKNOWN:
        return QualityClass.UNKNOWN
    if relative in criteria.wind_unfavorable_classes and intensity in criteria.wind_unfavorable_intensities:
        return QualityClass.UNFAVORABLE
    if relative in {WindRelative.OFFSHORE, WindRelative.OFFSHORE_SIDE} and intensity in {
        WindIntensity.LIGHT,
        WindIntensity.MODERATE,
    }:
        return QualityClass.FAVORABLE
    return QualityClass.NEUTRAL


def swell_quality(direction: float | None, profile: PeakProfile) -> tuple[str, QualityClass]:
    if direction is None:
        return "unknown", QualityClass.UNKNOWN
    if any(sector.contains(direction) for sector in profile.ideal_swell_sectors):
        return "ideal", QualityClass.FAVORABLE
    if any(sector.contains(direction) for sector in profile.blocked_swell_sectors):
        return "blocked", QualityClass.UNFAVORABLE
    if any(sector.contains(direction) for sector in profile.acceptable_swell_sectors):
        return "acceptable", QualityClass.NEUTRAL
    return "unknown", QualityClass.NEUTRAL


def period_quality(period: float | None, profile: PeakProfile) -> tuple[str, QualityClass]:
    if period is None:
        return "unknown", QualityClass.UNKNOWN
    if profile.ideal_period_s.contains(period):
        return "ideal", QualityClass.FAVORABLE
    minimum = profile.minimum_period_s if profile.minimum_period_s is not None else profile.ideal_period_s.minimum
    if period < minimum:
        return "below_minimum", QualityClass.UNFAVORABLE
    return "usable", QualityClass.NEUTRAL


def apply_downgrade(ceiling: SurfGrade, steps: int, criteria: CriteriaSet) -> SurfGrade:
    if ceiling is SurfGrade.NO_SURFABLE_WAVES or steps <= 0:
        return ceiling
    index = GRADE_ORDER.index(ceiling)
    lowered = GRADE_ORDER[max(0, index - min(steps, criteria.max_quality_downgrade_steps))]
    floor_index = GRADE_ORDER.index(criteria.minimum_surfable_grade)
    if GRADE_ORDER.index(ceiling) >= floor_index:
        return GRADE_ORDER[max(floor_index, GRADE_ORDER.index(lowered))]
    return lowered


def evaluate_slot(
    *,
    profile: PeakProfile,
    marine: NormalizedMarineHour | None,
    wind: NormalizedWindHour | None,
    criteria: CriteriaSet,
) -> SlotEvaluation:
    reasons: list[str] = []
    if marine is None or marine.wave_height_m is None or wind is None or wind.speed_kmh is None:
        fallback = marine.valid_at if marine is not None else wind.valid_at if wind is not None else datetime.fromtimestamp(0, tz=URUGUAY_TZ)
        return SlotEvaluation(
            peak_id=profile.peak_id,
            valid_at=fallback,
            size=None,
            wind=None,
            swell_favorability="unknown",
            period_favorability="unknown",
            swell_quality_class=QualityClass.UNKNOWN,
            period_quality_class=QualityClass.UNKNOWN,
            ceiling_grade=None,
            unfavorable_factor_count=0,
            quality_downgrade_steps=0,
            condition_grade=None,
            state=ForecastState.INCOMPLETE_FORECAST,
            reason_codes=["missing_required_input"],
            period_s=None,
            swell_direction_deg=None,
        )
    size = size_estimate(marine.wave_height_m, criteria)
    state, ceiling = ceiling_from_size(size, criteria)
    swell_label, swell_class = swell_quality(marine.swell_direction_deg or marine.wave_direction_deg, profile)
    period_s = marine.swell_period_s if marine.swell_period_s is not None else marine.wave_period_s
    period_label, period_class = period_quality(period_s, profile)
    relative = (
        wind_relative(wind.direction_deg, profile) if wind.direction_deg is not None else WindRelative.UNKNOWN
    )
    intensity = wind_intensity(wind.speed_kmh, criteria) if wind.speed_kmh is not None else WindIntensity.UNKNOWN
    wind_class = wind_quality(relative, intensity, criteria)
    wind_assessment = WindAssessment(
        relative_class=relative,
        intensity=intensity,
        quality_class=wind_class,
        favorable=True if wind_class is QualityClass.FAVORABLE else False if wind_class is QualityClass.UNFAVORABLE else None,
        reasons=[],
        speed_kmh=wind.speed_kmh,
        direction_deg=wind.direction_deg,
    )
    count = sum(
        1
        for item in (swell_class, period_class, wind_class)
        if item is QualityClass.UNFAVORABLE
    )
    steps = 1 if count >= criteria.quality_downgrade_min_unfavorable_factors else 0
    if state is ForecastState.UNCERTAIN:
        reasons.append("range_crosses_threshold")
        grade = None
    elif ceiling is None:
        grade = None
    else:
        grade = apply_downgrade(ceiling, steps, criteria)
        if steps:
            reasons.append("two_factor_quality_downgrade")
        elif count == 1:
            reasons.append("single_unfavorable_factor")
        if grade is SurfGrade.NO_SURFABLE_WAVES:
            reasons.append("size_below_threshold")
    return SlotEvaluation(
        peak_id=profile.peak_id,
        valid_at=marine.valid_at,
        size=size,
        wind=wind_assessment,
        swell_favorability=swell_label,
        period_favorability=period_label,
        swell_quality_class=swell_class,
        period_quality_class=period_class,
        ceiling_grade=ceiling,
        unfavorable_factor_count=count,
        quality_downgrade_steps=steps if state is ForecastState.RESOLVED else 0,
        condition_grade=grade,
        state=state,
        reason_codes=reasons,
        period_s=period_s,
        swell_direction_deg=marine.swell_direction_deg
        if marine.swell_direction_deg is not None
        else marine.wave_direction_deg,
    )


def swell_trend(hours: list[NormalizedMarineHour], criteria: CriteriaSet) -> SwellTrend:
    samples = [(hour.valid_at, hour.swell_height_m if hour.swell_height_m is not None else hour.wave_height_m, "swell_height_m" if hour.swell_height_m is not None else "wave_height_m") for hour in hours]
    usable = [(when, height, variable) for when, height, variable in samples if height is not None]
    if len(usable) < criteria.swell_trend_min_samples:
        return SwellTrend(SwellTrendState.UNSUPPORTED, len(usable), "swell_height_m")
    usable.sort(key=lambda item: item[0])
    variable = usable[0][2]
    values = [item[1] for item in usable]
    n = len(values)
    third = max(1, n // 3)
    first = sum(values[:third]) / third
    last = sum(values[-third:]) / third
    middle = values[third:-third] or values
    threshold = max(criteria.swell_trend_absolute_change_m, abs(first) * criteria.swell_trend_relative_change)
    peak = max(middle)
    if peak > first + threshold and peak > last + threshold:
        state = SwellTrendState.PEAKING
    elif last - first >= threshold:
        state = SwellTrendState.BUILDING
    elif first - last >= threshold:
        state = SwellTrendState.DROPPING
    else:
        state = SwellTrendState.STEADY
    return SwellTrend(state, n, variable)


def _hour_lookup(hours: list, attr: str = "valid_at") -> dict[datetime, object]:
    table: dict[datetime, object] = {}
    for hour in hours:
        table[getattr(hour, attr).astimezone(URUGUAY_TZ).replace(minute=0, second=0, microsecond=0)] = hour
    return table


def evaluate_forecast(
    *,
    request: QueryRequest,
    criteria: CriteriaSet,
    profiles: list[PeakProfile],
    marine_hours: list[NormalizedMarineHour],
    wind_hours: list[NormalizedWindHour],
    fetches: list[SourceFetch],
    independence_groups: set[str],
) -> list[DaySummary]:
    dates = horizon_dates(request.reference_time)
    marine_by_hour = _hour_lookup(marine_hours)
    wind_by_hour = _hour_lookup(wind_hours)
    step = native_step_minutes([hour.valid_at for hour in marine_hours])
    days: list[DaySummary] = []
    complete_profiles = [profile for profile in profiles if not profile.validation_errors and profile.status.value != "incomplete"]
    for local_date in dates:
        # After 20:00 UYT today: still evaluate the full day's slots for display/rating,
        # but never invent a new best window (FR window-completed).
        window_done = is_today(local_date, request.reference_time) and analysis_window_completed(
            request.reference_time
        )
        day_marine = [
            hour
            for hour in marine_hours
            if (
                slot_in_calendar_analysis_window(hour.valid_at, local_date)
                if window_done
                else slot_in_analysis_window(hour.valid_at, local_date, request.reference_time)
            )
        ]
        trend = swell_trend(day_marine, criteria)
        peaks: list[PeakDayForecast] = []
        for profile in profiles:
            if profile.validation_errors or profile.status.value == "incomplete":
                continue
            slots = _slots_for_day(
                profile,
                local_date,
                request,
                criteria,
                marine_by_hour,
                wind_by_hour,
                full_day=window_done,
            )
            window = None if window_done or (step and step != 60) else select_best_window(slots, step)
            day_state, condition, size, reasons = _day_condition(slots, window, step)
            if step and step != 60:
                reasons.append("unsupported_temporal_resolution")
            if len([slot for slot in slots if slot.state == ForecastState.RESOLVED]) < 2:
                reasons.append("fewer_than_two_valid_hours")
            confidence = assess(
                profile=profile,
                state=day_state,
                fetches=fetches,
                independence_groups=independence_groups,
            )
            if window_done:
                reasons.append("analysis_window_completed")
            peaks.append(
                PeakDayForecast(
                    peak_id=profile.peak_id,
                    local_date=local_date,
                    state=day_state,
                    condition=condition,
                    size=size,
                    best_window=None if window_done else window,
                    confidence=confidence,
                    reason_codes=sorted(set(reasons)),
                    reference_slots=_reference_slots(slots, local_date, request.reference_time),
                )
            )
        resolved = [peak for peak in peaks if peak.state == ForecastState.RESOLVED and peak.condition]
        best_ids: list[str] = []
        if resolved:
            best_grade = max(resolved, key=lambda peak: GRADE_ORDER.index(peak.condition or SurfGrade.NO_SURFABLE_WAVES)).condition
            best_ids = [peak.peak_id for peak in resolved if peak.condition == best_grade]
        for peak in peaks:
            peak.highlighted = peak.peak_id in best_ids
        rotation = _wind_rotation(
            slots=None,
            wind_hours=wind_hours,
            local_date=local_date,
            request=request,
            criteria=criteria,
            profiles=complete_profiles,
            full_day=window_done,
        )
        if window_done:
            headline, code = "Ventana de análisis finalizada", "analysis_window_completed"
            day_state = ForecastState.ANALYSIS_WINDOW_COMPLETED
        else:
            headline, code = _headline(peaks, best_ids)
            day_state = _rollup_state(peaks)
        days.append(
            DaySummary(
                local_date=local_date,
                state=day_state,
                headline=headline,
                headline_code=code,
                best_peak_ids=best_ids,
                swell_trend=trend,
                wind_rotation=rotation,
                peaks=peaks,
            )
        )
    return days


def _slots_for_day(
    profile,
    local_date,
    request,
    criteria,
    marine_by_hour,
    wind_by_hour,
    *,
    full_day: bool = False,
) -> list[SlotEvaluation]:
    keys = sorted(set(marine_by_hour) | set(wind_by_hour))
    slots: list[SlotEvaluation] = []
    for when in keys:
        in_window = (
            slot_in_calendar_analysis_window(when, local_date)
            if full_day
            else slot_in_analysis_window(when, local_date, request.reference_time)
        )
        if not in_window:
            continue
        slots.append(
            evaluate_slot(
                profile=profile,
                marine=marine_by_hour.get(when),  # type: ignore[arg-type]
                wind=wind_by_hour.get(when),  # type: ignore[arg-type]
                criteria=criteria,
            )
        )
    return slots


def _reference_slots(slots: list[SlotEvaluation], local_date: str, reference: datetime) -> list[SlotEvaluation]:
    offset = day_offset(local_date, reference)
    wanted_hours = {6, 12, 18}
    selected = [
        slot
        for slot in slots
        if slot.valid_at.astimezone(URUGUAY_TZ).hour in wanted_hours
    ]
    if offset >= 2:
        return selected
    return selected


def _day_condition(slots, window: BestWindow | None, step: int | None):
    if any(slot.state == ForecastState.INCOMPLETE_FORECAST for slot in slots) and not any(
        slot.state == ForecastState.RESOLVED for slot in slots
    ):
        return ForecastState.INCOMPLETE_FORECAST, None, None, ["missing_required_input"]
    if window is not None:
        matching = [slot for slot in slots if slot.valid_at == window.start_at]
        size = matching[0].size if matching else None
        reasons = list(matching[0].reason_codes) if matching else []
        return ForecastState.RESOLVED, window.condition, size, reasons
    uncertain = [slot for slot in slots if slot.state == ForecastState.UNCERTAIN]
    if uncertain:
        return ForecastState.UNCERTAIN, None, uncertain[0].size, ["range_crosses_threshold"]
    resolved = [slot for slot in slots if slot.state == ForecastState.RESOLVED and slot.condition_grade]
    if not resolved:
        return ForecastState.INCOMPLETE_FORECAST, None, None, ["missing_required_input"]
    best = max(resolved, key=lambda slot: GRADE_ORDER.index(slot.condition_grade or SurfGrade.NO_SURFABLE_WAVES))
    return best.state, best.condition_grade, best.size, list(best.reason_codes)


def _headline(peaks: list[PeakDayForecast], best_ids: list[str]) -> tuple[str, str]:
    if not peaks:
        return "Sin picos completos", "no_complete_peaks"
    if all(peak.state == ForecastState.INCOMPLETE_FORECAST for peak in peaks):
        return "Pronóstico incompleto", "incomplete_forecast"
    if all(peak.state == ForecastState.UNCERTAIN for peak in peaks):
        return "Incierto", "uncertain"
    if best_ids:
        return f"Mejores picos: {', '.join(best_ids)}", "best_peaks"
    return "Sin olas surfeables", "no_surfable_waves"


def _rollup_state(peaks: list[PeakDayForecast]) -> ForecastState:
    if any(peak.state == ForecastState.RESOLVED for peak in peaks):
        return ForecastState.RESOLVED
    if any(peak.state == ForecastState.UNCERTAIN for peak in peaks):
        return ForecastState.UNCERTAIN
    if peaks and all(peak.state == ForecastState.ANALYSIS_WINDOW_COMPLETED for peak in peaks):
        return ForecastState.ANALYSIS_WINDOW_COMPLETED
    return ForecastState.INCOMPLETE_FORECAST


def _wind_rotation(*, slots, wind_hours, local_date, request, criteria, profiles, full_day: bool = False):
    in_window = [
        hour
        for hour in wind_hours
        if hour.speed_kmh is not None
        and (
            slot_in_calendar_analysis_window(hour.valid_at, local_date)
            if full_day
            else slot_in_analysis_window(hour.valid_at, local_date, request.reference_time)
        )
    ]
    if len(in_window) < 2:
        return None
    in_window.sort(key=lambda hour: hour.valid_at)
    first, last = in_window[0], in_window[-1]
    return {
        "start_intensity": wind_intensity(first.speed_kmh or 0, criteria).value,
        "end_intensity": wind_intensity(last.speed_kmh or 0, criteria).value,
        "start_direction_deg": first.direction_deg,
        "end_direction_deg": last.direction_deg,
    }
