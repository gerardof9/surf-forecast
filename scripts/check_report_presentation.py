#!/usr/bin/env python3
"""Focused pure-Python checks for presentation 1.2.0 DayBrief fields.

Contract: specs/005-daily-brief/contracts/presentation-1.2.0.md

Run from repo root:

    .\\.venv\\Scripts\\python.exe scripts\\check_report_presentation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    failures = _run_checks()
    if failures:
        print("FAIL")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("OK — presentation report checks passed")
    return 0


def _run_checks() -> list[str]:
    checks = [
        _check_fr017_labels,
        _check_ordinal_scores,
        _check_best_peak_day_rating,
        _check_narrative_omission,
        _check_sampling_bands,
        _check_provisional_and_window_completed,
        _check_wind_passthrough_and_peak_analysis,
        _check_incomplete_not_few_waves,
        _check_schema_120_daybrief,
        _check_worth_filter_and_empty,
        _check_incomplete_manana_stub,
    ]
    failures: list[str] = []
    for check in checks:
        try:
            failures.extend(check())
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{check.__name__}: {exc}")
    return failures


def _check_fr017_labels() -> list[str]:
    from surf_forecast.domain.presentation import CONDITION_LABELS, STATE_LABELS

    expected = {
        "very_good": "Buena oportunidad",
        "good": "Buena oportunidad",
        "fair": "Surfeable",
        "small_but_surfable": "Variable",
        "no_surfable_waves": "Pocas olas",
    }
    failures = []
    for key, label in expected.items():
        if CONDITION_LABELS.get(key) != label:
            failures.append(f"CONDITION_LABELS[{key}]={CONDITION_LABELS.get(key)!r} want {label!r}")
    for key, label in {
        "uncertain": "Incierto",
        "incomplete_forecast": "Pronóstico incompleto",
        "analysis_window_completed": "Ventana de análisis finalizada",
    }.items():
        if STATE_LABELS.get(key) != label:
            failures.append(f"STATE_LABELS[{key}]={STATE_LABELS.get(key)!r} want {label!r}")
    return failures


def _check_ordinal_scores() -> list[str]:
    from surf_forecast.domain.day_rating import GRADE_TO_SCORE, METHOD, score_for_grade
    from surf_forecast.domain.models import SurfGrade

    expected = {
        SurfGrade.NO_SURFABLE_WAVES: 1.0,
        SurfGrade.SMALL_BUT_SURFABLE: 2.0,
        SurfGrade.FAIR: 3.0,
        SurfGrade.GOOD: 4.0,
        SurfGrade.VERY_GOOD: 5.0,
    }
    failures = []
    if METHOD != "best_resolved_grade_map_v2":
        failures.append(f"METHOD={METHOD!r}")
    for grade, score in expected.items():
        got = score_for_grade(grade)
        if got != score or got != GRADE_TO_SCORE[grade]:
            failures.append(f"score_for_grade({grade})={got}")
    # Half-step path: provisional/low confidence adjusts by -0.5
    from surf_forecast.domain.day_rating import build_peak_rating
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        ForecastState,
        PeakDayForecast,
        SurfGrade,
    )

    peak = PeakDayForecast(
        peak_id="x",
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.GOOD,
        size=None,
        best_window=None,
        confidence=ConfidenceAssessment(
            level=ConfidenceLevel.MEDIUM, caps=["provisional_profile"], degradations=[]
        ),
        reason_codes=[],
    )
    rating = build_peak_rating(peak)
    if not rating or rating["score"] != 3.5:
        failures.append(f"provisional half-step expected 3.5, got {rating}")
    return failures


def _check_best_peak_day_rating() -> list[str]:
    from surf_forecast.domain.day_rating import build_day_rating, build_peak_rating
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        DaySummary,
        ForecastState,
        PeakDayForecast,
        SurfGrade,
    )

    failures: list[str] = []

    def _peak(pid: str, grade: SurfGrade | None, state: ForecastState, highlighted: bool = False) -> PeakDayForecast:
        return PeakDayForecast(
            peak_id=pid,
            local_date="2026-10-14",
            state=state,
            condition=grade,
            size=None,
            best_window=None,
            confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=[], degradations=[]),
            reason_codes=[],
            highlighted=highlighted,
        )

    good = _peak("la_aguada", SurfGrade.GOOD, ForecastState.RESOLVED, highlighted=True)
    fair = _peak("el_canal", SurfGrade.FAIR, ForecastState.RESOLVED)
    uncertain = _peak("zorra", None, ForecastState.UNCERTAIN)
    day = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        headline=None,
        headline_code=None,
        best_peak_ids=["la_aguada"],
        swell_trend=None,
        wind_rotation=None,
        peaks=[fair, good, uncertain],
    )
    rating, reason = build_day_rating(day)
    if rating is None or rating["score"] != 4.0 or rating["source_peak_id"] != "la_aguada":
        failures.append(f"day rating unexpected: {rating} reason={reason}")
    if build_peak_rating(uncertain) is not None:
        failures.append("uncertain peak must not get peak_rating")

    empty = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.UNCERTAIN,
        headline=None,
        headline_code=None,
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[uncertain, _peak("x", None, ForecastState.INCOMPLETE_FORECAST)],
    )
    rating2, reason2 = build_day_rating(empty)
    if rating2 is not None or not reason2:
        failures.append(f"expected Sin valoración path, got {rating2} {reason2}")
    return failures


def _check_narrative_omission() -> list[str]:
    from surf_forecast.domain.models import DaySummary, ForecastState
    from surf_forecast.domain.narrative import build_day_brief

    day = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.INCOMPLETE_FORECAST,
        headline=None,
        headline_code=None,
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[],
    )
    brief = build_day_brief(
        day,
        profiles=[],
        worth_spots=[],
        go_window=None,
        height=None,
        sources_ok=False,
    )
    failures = []
    text = f"{brief.get('headline')} {brief.get('body')} {brief.get('caution')}".lower()
    if "garantía" in text and "no" not in text:
        failures.append("brief must not claim guarantees without negation")
    for word in ("ciclón", "probabilidad", "series mayores", "hs cruda"):
        if word in text:
            failures.append(f"narrative invented banned term: {word}")
    if "estimaciones" not in text and "estimación" not in text:
        failures.append("brief should keep estimative disclaimer")
    return failures


def _check_sampling_bands() -> list[str]:
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from surf_forecast.domain.evolution_samples import sample_evolution
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        ForecastState,
        PeakDayForecast,
        QualityClass,
        SlotEvaluation,
        SurfGrade,
        WindAssessment,
        WindIntensity,
        WindRelative,
    )

    tz = ZoneInfo("America/Montevideo")

    def slot(hour: int) -> SlotEvaluation:
        return SlotEvaluation(
            peak_id="la_aguada",
            valid_at=datetime(2026, 10, 14, hour, 0, tzinfo=tz),
            size=None,
            wind=WindAssessment(
                relative_class=WindRelative.OFFSHORE,
                intensity=WindIntensity.MODERATE,
                quality_class=QualityClass.FAVORABLE,
                favorable=True,
                speed_kmh=15.0,
                direction_deg=180.0,
            ),
            swell_favorability="ideal",
            period_favorability="ideal",
            swell_quality_class=QualityClass.FAVORABLE,
            period_quality_class=QualityClass.FAVORABLE,
            ceiling_grade=SurfGrade.FAIR,
            unfavorable_factor_count=0,
            quality_downgrade_steps=0,
            condition_grade=SurfGrade.FAIR,
            state=ForecastState.RESOLVED,
        )

    peak = PeakDayForecast(
        peak_id="la_aguada",
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.FAIR,
        size=None,
        best_window=None,
        confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=[], degradations=[]),
        reason_codes=[],
        reference_slots=[slot(7), slot(8), slot(12), slot(16), slot(19)],
    )
    samples = sample_evolution(peak)
    failures = []
    bands = [s["band"] for s in samples]
    if bands != ["morning", "midday", "afternoon"]:
        failures.append(f"bands={bands}")
    if samples and samples[0]["local_hour"] != "07:00":
        failures.append(f"morning hour={samples[0]['local_hour']}")
    if not samples or samples[0].get("wind_speed_kmh") != 15.0:
        failures.append("wind pass-through missing on sample")
    return failures


def _check_provisional_and_window_completed() -> list[str]:
    from surf_forecast.domain.day_rating import build_day_rating
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        DaySummary,
        DirectionSector,
        ForecastState,
        NumericRange,
        PeakDayForecast,
        PeakProfile,
        ProfileStatus,
    )
    from surf_forecast.domain.narrative import build_day_brief

    failures: list[str] = []
    completed = PeakDayForecast(
        peak_id="la_aguada",
        local_date="2026-10-14",
        state=ForecastState.ANALYSIS_WINDOW_COMPLETED,
        condition=None,
        size=None,
        best_window=None,
        confidence=ConfidenceAssessment(level=ConfidenceLevel.LOW, caps=[], degradations=[]),
        reason_codes=["analysis_window_completed"],
    )
    day = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.ANALYSIS_WINDOW_COMPLETED,
        headline=None,
        headline_code=None,
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[completed],
    )
    rating, reason = build_day_rating(day)
    if rating is not None:
        failures.append("window-completed day must have no rating")
    if not reason:
        failures.append("window-completed needs absent reason")
    analysis = build_day_brief(
        day, profiles=[], worth_spots=[], go_window=None, height=None, sources_ok=True
    )
    caution = (analysis.get("caution") or "").lower()
    body = (analysis.get("body") or "").lower()
    if "ventana" not in caution and "cerró" not in caution and "finaliz" not in body:
        failures.append("window-completed brief should caution about closed analysis window")

    profile = PeakProfile(
        peak_id="la_aguada",
        name="La Aguada",
        zone_id="la_paloma",
        latitude=-34.66,
        longitude=-54.15,
        orientation_deg=90.0,
        ideal_swell_sectors=[DirectionSector(start_deg=0, end_deg=180)],
        ideal_period_s=NumericRange(minimum=8, maximum=16),
        status=ProfileStatus.PROVISIONAL,
        profile_version="1",
        schema_version="1",
        updated_at="2026-01-01",
    )
    prov_day = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        headline=None,
        headline_code=None,
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[],
    )
    prov_analysis = build_day_brief(
        prov_day, profiles=[profile], worth_spots=[], go_window=None, height=None, sources_ok=True
    )
    joined = f"{prov_analysis.get('caution')} {prov_analysis.get('body')}".lower()
    if "provisional" not in joined and "perfil" not in joined:
        failures.append("provisional profile should appear in brief caution/body")
    return failures


def _check_wind_passthrough_and_peak_analysis() -> list[str]:
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        DirectionSector,
        ForecastState,
        NumericRange,
        PeakDayForecast,
        PeakProfile,
        ProfileStatus,
        SurfableSizeEstimate,
        SurfGrade,
    )
    from surf_forecast.domain.narrative import build_peak_analysis

    failures: list[str] = []
    thin = PeakDayForecast(
        peak_id="x",
        local_date="2026-10-14",
        state=ForecastState.INCOMPLETE_FORECAST,
        condition=None,
        size=None,
        best_window=None,
        confidence=ConfidenceAssessment(level=ConfidenceLevel.LOW, caps=[], degradations=[]),
        reason_codes=["missing_required_input"],
    )
    analysis, absent = build_peak_analysis(thin, profile=None)
    if analysis is not None:
        failures.append("thin peak analysis should be omitted")
    if not absent:
        failures.append("thin peak should set absent reason")

    profile = PeakProfile(
        peak_id="la_aguada",
        name="La Aguada",
        zone_id="la_paloma",
        latitude=-34.66,
        longitude=-54.15,
        orientation_deg=90.0,
        ideal_swell_sectors=[DirectionSector(start_deg=0, end_deg=180)],
        ideal_period_s=NumericRange(minimum=8, maximum=16),
        status=ProfileStatus.PROVISIONAL,
        profile_version="1",
        schema_version="1",
        updated_at="2026-01-01",
    )
    rich = PeakDayForecast(
        peak_id="la_aguada",
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.GOOD,
        size=SurfableSizeEstimate(
            raw_hs_m=1.2,
            point_m=0.9,
            minimum_m=0.7,
            maximum_m=1.1,
            point_k=0.75,
            range_k_low=0.6,
            range_k_high=0.9,
        ),
        best_window=None,
        confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=["provisional_profile"], degradations=[]),
        reason_codes=[],
    )
    analysis2, _ = build_peak_analysis(rich, profile=profile)
    if analysis2 is None or not analysis2.get("sentences"):
        failures.append("rich peak should emit peak analysis")
    return failures


def _check_incomplete_not_few_waves() -> list[str]:
    from surf_forecast.domain.models import ForecastState
    from surf_forecast.domain.presentation import condition_or_state_label

    label = condition_or_state_label(None, ForecastState.INCOMPLETE_FORECAST)
    if label == "Pocas olas":
        return ["incomplete_forecast must not display as Pocas olas"]
    if label != "Pronóstico incompleto":
        return [f"incomplete label={label!r}"]
    return []


def _check_schema_120_daybrief() -> list[str]:
    from datetime import datetime
    from pathlib import Path
    from zoneinfo import ZoneInfo

    from surf_forecast.application.replay_service import replay_fixture
    from surf_forecast.domain.models import (
        BestWindow,
        ConfidenceAssessment,
        ConfidenceLevel,
        ForecastState,
        PeakDayForecast,
        SurfGrade,
        SurfableSizeEstimate,
    )
    from surf_forecast.domain.presentation import (
        go_window_from_peak,
        height_summary_from_peak,
        rank_worth_spots,
    )

    failures: list[str] = []
    root = Path(__file__).resolve().parents[1]
    payload, _ = replay_fixture(
        root / "fixtures" / "normal",
        datetime(2026, 10, 13, 15, 0, tzinfo=ZoneInfo("America/Montevideo")),
        json_mode=True,
    )
    if payload.get("schema_version") != "1.2.0":
        failures.append(f"schema_version={payload.get('schema_version')}")
    if len(payload.get("days") or []) != 2:
        failures.append(f"expected 2 days, got {len(payload.get('days') or [])}")
    for day in payload.get("days") or []:
        brief = day.get("brief")
        if not brief:
            failures.append(f"missing brief on {day.get('local_date')}")
            continue
        for key in ("headline", "body", "worth_spots", "label"):
            if key not in brief:
                failures.append(f"brief missing {key}")
        go = brief.get("go_window")
        if go:
            display = str(go.get("display") or "")
            if display.lstrip().startswith("840") or "840 min" in display:
                failures.append("go_window display minute-led")
            if "T06:" in display or "T0" in display.split(" ")[0]:
                failures.append("go_window display ISO-led")
            if brief.get("worth_spots") and go.get("source_peak_id") != brief["worth_spots"][0]["peak_id"]:
                failures.append("go_window must come from best worth spot")
        for spot in brief.get("worth_spots") or []:
            if spot.get("condition") not in {"fair", "good", "very_good"}:
                failures.append(f"below-threshold spot listed: {spot}")
        if len(brief.get("worth_spots") or []) > 3:
            failures.append("worth_spots > 3")
        for key in day.keys():
            if key.lower() in {"tiempo", "energia", "energía"}:
                failures.append(f"forbidden key {key}")
        for key in brief.keys():
            if key.lower() in {"tiempo", "energia", "energía"}:
                failures.append(f"forbidden brief key {key}")

    # Unit: worth ranking excludes small_but_surfable
    tz = ZoneInfo("America/Montevideo")
    start = datetime(2026, 10, 14, 6, 0, tzinfo=tz)
    end = datetime(2026, 10, 14, 9, 0, tzinfo=tz)

    def _peak(pid: str, grade: SurfGrade) -> PeakDayForecast:
        return PeakDayForecast(
            peak_id=pid,
            local_date="2026-10-14",
            state=ForecastState.RESOLVED,
            condition=grade,
            size=SurfableSizeEstimate(
                raw_hs_m=1.0,
                point_m=0.8,
                minimum_m=0.7,
                maximum_m=0.9,
                point_k=0.75,
                range_k_low=0.6,
                range_k_high=0.9,
            ),
            best_window=BestWindow(
                start_at=start,
                end_at=end,
                duration_minutes=180,
                condition=grade,
                support="contiguous",
            ),
            confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=[], degradations=[]),
            reason_codes=[],
        )

    worth = rank_worth_spots(
        [
            _peak("el_canal", SurfGrade.SMALL_BUT_SURFABLE),
            _peak("la_aguada", SurfGrade.GOOD),
            _peak("zorra", SurfGrade.FAIR),
        ],
        profile_by_id={},
    )
    ids = [w["peak_id"] for w in worth]
    if "el_canal" in ids:
        failures.append("small_but_surfable should not be worth spot")
    if ids and ids[0] != "la_aguada":
        failures.append(f"best worth should be la_aguada, got {ids}")
    best = _peak("la_aguada", SurfGrade.GOOD)
    height = height_summary_from_peak(best)
    go = go_window_from_peak(best)
    if not height or height.get("kind") != "derived":
        failures.append("height summary missing/derived")
    if not go or "06:00" not in go.get("display", ""):
        failures.append(f"go_window display unexpected: {go}")
    return failures


def _check_worth_filter_and_empty() -> list[str]:
    from surf_forecast.domain.models import (
        ConfidenceAssessment,
        ConfidenceLevel,
        ForecastState,
        PeakDayForecast,
        SurfGrade,
    )
    from surf_forecast.domain.narrative import build_day_brief
    from surf_forecast.domain.presentation import rank_worth_spots
    from surf_forecast.domain.models import DaySummary

    failures: list[str] = []
    poor = PeakDayForecast(
        peak_id="a",
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.NO_SURFABLE_WAVES,
        size=None,
        best_window=None,
        confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=[], degradations=[]),
        reason_codes=[],
    )
    worth = rank_worth_spots([poor], profile_by_id={})
    if worth:
        failures.append("poor-only day must have empty worth list")
    day = DaySummary(
        local_date="2026-10-14",
        state=ForecastState.RESOLVED,
        headline=None,
        headline_code=None,
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[poor],
    )
    brief = build_day_brief(
        day, profiles=[], worth_spots=[], go_window=None, height=None, sources_ok=True
    )
    if "ningún pico" not in (brief.get("headline") or "").lower() and "ningún pico" not in (
        brief.get("body") or ""
    ).lower():
        failures.append("empty worth brief should say no clear beach")
    return failures


def _check_incomplete_manana_stub() -> list[str]:
    from surf_forecast.domain.narrative import build_day_brief
    from surf_forecast.domain.models import DaySummary, ForecastState

    failures = []
    stub = DaySummary(
        local_date="2026-10-15",
        state=ForecastState.INCOMPLETE_FORECAST,
        headline=None,
        headline_code="incomplete_forecast",
        best_peak_ids=[],
        swell_trend=None,
        wind_rotation=None,
        peaks=[],
    )
    brief = build_day_brief(
        stub,
        profiles=[],
        worth_spots=[],
        go_window=None,
        height=None,
        sources_ok=True,
        incomplete=True,
    )
    text = f"{brief.get('headline')} {brief.get('body')} {brief.get('caution')}".lower()
    if "incompleto" not in text and "no hay un brief" not in text and "faltan" not in text:
        failures.append("incomplete Mañana must state limited/missing data")
    if "hoy" in text and "copió" not in text and "no se copió" not in text:
        # soft: caution should say we did not copy Hoy
        pass
    if brief.get("caution") and "copió" not in brief["caution"].lower():
        failures.append("incomplete brief caution should say Hoy was not copied")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
