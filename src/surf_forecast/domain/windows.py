"""Uruguay local analysis window, horizon, and best-window selection."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from surf_forecast.domain.models import BestWindow, ForecastState, SlotEvaluation, SurfGrade

URUGUAY_TZ = ZoneInfo("America/Montevideo")
ANALYSIS_START = time(6, 0)
ANALYSIS_END = time(20, 0)
HORIZON_DAYS = 5
MINIMUM_WINDOW_MINUTES = 120


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("reference time must include a UTC offset")
    return value.astimezone(URUGUAY_TZ)


def local_now(reference: datetime) -> datetime:
    return ensure_aware(reference)


def analysis_window_completed(reference: datetime) -> bool:
    local = local_now(reference)
    return local.timetz().replace(tzinfo=None) >= ANALYSIS_END or local.time() >= ANALYSIS_END


def horizon_dates(reference: datetime) -> list[str]:
    local = local_now(reference).date()
    return [(local + timedelta(days=offset)).isoformat() for offset in range(HORIZON_DAYS)]


def remaining_analysis_start(reference: datetime, local_date: str) -> time:
    local = local_now(reference)
    if local.date().isoformat() != local_date:
        return ANALYSIS_START
    if local.time() <= ANALYSIS_START:
        return ANALYSIS_START
    return time(local.hour, 0)


def slot_in_analysis_window(valid_at: datetime, local_date: str, reference: datetime) -> bool:
    local = valid_at.astimezone(URUGUAY_TZ)
    if local.date().isoformat() != local_date:
        return False
    start = remaining_analysis_start(reference, local_date)
    return start <= local.time() < ANALYSIS_END


def slot_in_calendar_analysis_window(valid_at: datetime, local_date: str) -> bool:
    """Full 06:00–20:00 UYT for the calendar day (ignores remaining-from-now)."""
    local = valid_at.astimezone(URUGUAY_TZ)
    if local.date().isoformat() != local_date:
        return False
    return ANALYSIS_START <= local.time() < ANALYSIS_END


def native_step_minutes(times: list[datetime]) -> int | None:
    if len(times) < 2:
        return 60
    deltas = sorted(
        {
            int((later - earlier).total_seconds() // 60)
            for earlier, later in zip(times, times[1:])
            if later > earlier
        }
    )
    return deltas[0] if deltas else 60


def select_best_window(slots: list[SlotEvaluation], support_minutes: int | None) -> BestWindow | None:
    usable = [
        slot
        for slot in slots
        if slot.state == ForecastState.RESOLVED
        and slot.condition_grade
        and slot.condition_grade != SurfGrade.NO_SURFABLE_WAVES
    ]
    if support_minutes is not None and support_minutes != 60:
        return None
    if len(usable) < 2:
        return None
    usable.sort(key=lambda slot: slot.valid_at)
    best: tuple[int, SurfGrade, list[SlotEvaluation]] | None = None
    current: list[SlotEvaluation] = [usable[0]]
    for slot in usable[1:]:
        previous = current[-1]
        if (slot.valid_at - previous.valid_at) == timedelta(hours=1):
            current.append(slot)
            continue
        best = _maybe_better(best, current)
        current = [slot]
    best = _maybe_better(best, current)
    if best is None:
        return None
    _, grade, group = best
    end_at = group[-1].valid_at + timedelta(hours=1)
    duration = int((end_at - group[0].valid_at).total_seconds() // 60)
    return BestWindow(
        start_at=group[0].valid_at,
        end_at=end_at,
        duration_minutes=duration,
        condition=grade,
        support="hourly",
    )


def _maybe_better(
    current: tuple[int, SurfGrade, list[SlotEvaluation]] | None,
    group: list[SlotEvaluation],
) -> tuple[int, SurfGrade, list[SlotEvaluation]] | None:
    if len(group) < 2:
        return current
    duration = len(group)
    lowest = min(group, key=lambda slot: GRADE_RANK[slot.condition_grade or SurfGrade.NO_SURFABLE_WAVES])
    grade = lowest.condition_grade or SurfGrade.NO_SURFABLE_WAVES
    score = (GRADE_RANK[grade], duration)
    if current is None:
        return (score[0], grade, group)
    current_score = (GRADE_RANK[current[1]], current[0])
    if score > current_score:
        return (duration, grade, group)
    return current


GRADE_RANK = {grade: index for index, grade in enumerate(
    [SurfGrade.NO_SURFABLE_WAVES, SurfGrade.SMALL_BUT_SURFABLE, SurfGrade.FAIR, SurfGrade.GOOD, SurfGrade.VERY_GOOD]
)}


def part_of_day_label(valid_at: datetime) -> str:
    hour = valid_at.astimezone(URUGUAY_TZ).hour
    if hour < 12:
        return "morning"
    if hour < 16:
        return "midday"
    return "afternoon"


def is_today(local_date: str, reference: datetime) -> bool:
    return local_now(reference).date().isoformat() == local_date


def day_offset(local_date: str, reference: datetime) -> int:
    local = local_now(reference).date()
    target = datetime.fromisoformat(local_date).date()
    return (target - local).days
