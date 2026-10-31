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
        _check_card_copy_quality,
        _check_orientation_compatible_worth,
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
        "very_good": "Muy buena",
        "good": "Buena",
        "fair": "Razonable",
        "small_but_surfable": "Olas pequeñas pero surfeables",
        "no_surfable_waves": "Sin olas surfeables",
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
        favorable_window=None,
        height=None,
        sources_ok=False,
    )
    failures = []
    text = f"{brief.get('analysis')} {' '.join(brief.get('limitations') or [])}".lower()
    for word in ("ciclón", "probabilidad", "series mayores", "hs cruda", "strong", "peaking"):
        if word in text:
            failures.append(f"narrative invented banned term: {word}")
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
        day, profiles=[], worth_spots=[], favorable_window=None, height=None, sources_ok=True
    )
    lim = " ".join(analysis.get("limitations") or []).lower()
    if "ventana de análisis" not in lim and "finalizada" not in lim:
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
        prov_day,
        profiles=[profile],
        worth_spots=[],
        favorable_window=None,
        height=None,
        sources_ok=True,
    )
    joined = " ".join(prov_analysis.get("limitations") or []).lower()
    if "perfil" not in joined and "calibrad" not in joined:
        failures.append("provisional profile should appear in limitations")
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
        fav = brief.get("favorable_window") or brief.get("go_window")
        if fav:
            display = str(fav.get("display") or "")
            if "840" in display:
                failures.append("favorable_window minute-led")
            if "T06:" in display:
                failures.append("favorable_window ISO-led")
            if display.startswith("06:00") and "20:00" in display:
                failures.append("analysis band must not appear as favorable_window")
            if brief.get("worth_spots") and fav.get("source_peak_id") != brief["worth_spots"][0]["peak_id"]:
                failures.append("favorable_window must come from best worth spot")
        if not brief.get("analysis") and not brief.get("body"):
            failures.append("brief missing analysis")
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
        visible = f"{brief.get('analysis')} {brief.get('condition_label')} {' '.join(brief.get('limitations') or [])}"
        from surf_forecast.domain.presentation_labels import visible_text_has_internal_id

        leaked = visible_text_has_internal_id(visible)
        if leaked:
            failures.append(f"internal ids in brief text: {leaked}")

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
    # 06:00–09:00 tight window → favorable OK
    if not go or go.get("display") != "06:00–09:00":
        failures.append(f"favorable_window display unexpected: {go}")
    # Full analysis band must be omitted
    from datetime import timedelta

    wide_peak = _peak("la_aguada", SurfGrade.GOOD)
    wide_peak.best_window = BestWindow(
        start_at=start,
        end_at=start + timedelta(hours=14),
        duration_minutes=840,
        condition=SurfGrade.GOOD,
        support="contiguous",
    )
    if go_window_from_peak(wide_peak) is not None:
        failures.append("analysis-band window must not become favorable_window")
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
        day,
        profiles=[],
        worth_spots=[],
        favorable_window=None,
        height=None,
        sources_ok=True,
    )
    if brief.get("best_peak") is not None:
        failures.append("empty worth must not set best_peak")
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
        favorable_window=None,
        height=None,
        sources_ok=True,
        incomplete=True,
    )
    text = f"{brief.get('analysis')} {' '.join(brief.get('limitations') or [])}".lower()
    if "incompleto" not in text and "faltan" not in text and "suficientes" not in text:
        failures.append("incomplete Mañana must state limited/missing data")
    return failures


def _check_card_copy_quality() -> list[str]:
    """Content-improvements: no internal ids, no analysis-band as favorable, no speculative reason spam."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from surf_forecast.domain.models import (
        BestWindow,
        ConfidenceAssessment,
        ConfidenceLevel,
        DaySummary,
        DirectionSector,
        ForecastState,
        NumericRange,
        PeakDayForecast,
        PeakProfile,
        ProfileStatus,
        SurfGrade,
        SurfableSizeEstimate,
        SwellTrend,
        SwellTrendState,
    )
    from surf_forecast.domain.narrative import build_day_brief
    from surf_forecast.domain.presentation import (
        day_meteo_metrics,
        favorable_window_from_peak,
        height_summary_from_peak,
    )
    from surf_forecast.domain.presentation_labels import (
        visible_text_has_internal_id,
        wind_intensity_label,
    )
    from surf_forecast.presentation.tui.components.day_brief_card import _format_swell, _format_wind

    failures: list[str] = []
    tz = ZoneInfo("America/Montevideo")

    if wind_intensity_label("strong") != "fuerte":
        failures.append("strong → fuerte")
    if wind_intensity_label("very_strong") != "muy fuerte":
        failures.append("very_strong → muy fuerte")
    if wind_intensity_label("not_a_real_value") is not None:
        failures.append("unknown intensity must not invent a label")

    start = datetime(2026, 10, 16, 8, 0, tzinfo=tz)
    end = datetime(2026, 10, 16, 11, 0, tzinfo=tz)
    peak = PeakDayForecast(
        peak_id="la_aguada",
        local_date="2026-10-16",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.FAIR,
        size=SurfableSizeEstimate(
            raw_hs_m=1.2,
            point_m=1.0,
            minimum_m=0.9,
            maximum_m=1.3,
            point_k=0.75,
            range_k_low=0.6,
            range_k_high=0.9,
        ),
        best_window=BestWindow(
            start_at=start,
            end_at=end,
            duration_minutes=180,
            condition=SurfGrade.FAIR,
            support="contiguous",
        ),
        confidence=ConfidenceAssessment(level=ConfidenceLevel.MEDIUM, caps=[], degradations=[]),
        reason_codes=[],
    )
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
    day = DaySummary(
        local_date="2026-10-16",
        state=ForecastState.RESOLVED,
        headline=None,
        headline_code=None,
        best_peak_ids=["la_aguada"],
        swell_trend=SwellTrend(SwellTrendState.PEAKING, 6, "swell_height_m"),
        wind_rotation={
            "start_intensity": "strong",
            "end_intensity": "very_strong",
            "start_direction_deg": 200.0,
            "end_direction_deg": 160.0,
        },
        peaks=[peak],
    )
    worth = [
        {
            "peak_id": "la_aguada",
            "display_name": "La Aguada",
            "condition": "fair",
            "condition_label": "Razonable",
            "reason_short": None,
        }
    ]
    height = height_summary_from_peak(peak)
    fav = favorable_window_from_peak(peak)
    brief = build_day_brief(
        day,
        profiles=[profile],
        worth_spots=worth,
        favorable_window=fav,
        height=height,
        best_peak=peak,
        sources_ok=True,
    )
    metrics = day_meteo_metrics(day, peak=peak)
    visible = " ".join(
        [
            brief.get("analysis") or "",
            brief.get("condition_label") or "",
            _format_swell((metrics or {}).get("swell") or []),
            _format_wind((metrics or {}).get("wind")),
            (brief.get("best_peak") or {}).get("reason") or "",
        ]
    )
    leaked = visible_text_has_internal_id(visible)
    if leaked:
        failures.append(f"brief/metrics leak internal ids: {leaked}")
    if "oleaje viene oleaje" in visible.lower():
        failures.append("doubled oleaje phrase")
    if "strong" in visible.lower() or "very_strong" in visible.lower():
        failures.append("raw wind intensity in visible text")
    if "encaja mejor con el oleaje/viento de la evaluación" in visible.lower():
        failures.append("speculative peak reason")
    analysis = brief.get("analysis") or ""
    # Practical analysis may mention size/timing in natural language.
    if analysis.strip().startswith(("Razonable", "Buena", "Muy buena", "Surfeable")):
        failures.append("analysis leads with condition label")
    if "ciclón" in analysis.lower() or "lluvia" in analysis.lower():
        failures.append("analysis must not invent weather/rain without a source")
    if "mañana" not in analysis.lower() and "mediodía" not in analysis.lower() and "tarde" not in analysis.lower():
        if fav is not None:
            failures.append("analysis with favorable window should name a day band")
    if metrics is None or not (metrics.get("wind") or {}).get("intensity_display"):
        failures.append("wind metrics missing from day_meteo_metrics")
    elif "fuerte" not in str(metrics["wind"]["intensity_display"]).lower():
        failures.append(f"expected Spanish wind intensity, got {metrics['wind']}")
    # With wind hours, display should include km/h
    from surf_forecast.domain.models import NormalizedWindHour, QualityFlag
    from datetime import timezone as _tz

    sample_hours = [
        NormalizedWindHour(
            source_id="t",
            valid_at=datetime(2026, 10, 16, h, 0, tzinfo=tz),
            speed_kmh=speed,
            direction_deg=deg,
            gust_kmh=None,
            quality=QualityFlag.OBSERVED,
        )
        for h, speed, deg in (
            (7, 28.0, 200.0),
            (9, 32.0, 205.0),
            (12, 36.0, 160.0),
            (16, 42.0, 155.0),
        )
    ]
    with_speed = day_meteo_metrics(day, peak=peak, wind_hours=sample_hours)
    wind_disp = ((with_speed or {}).get("wind") or {}).get("display") or ""
    if "km/h" not in wind_disp:
        failures.append(f"wind display should include km/h, got {wind_disp!r}")
    if fav is None or fav.get("display") != "08:00–11:00":
        failures.append(f"expected tight favorable window, got {fav}")
    # Size lives on the card height field; analysis uses labelled rows (Oleaje/Viento/…).
    if height and not (height.get("display") or height.get("caption")):
        failures.append("height summary missing display for card")
    if analysis and "Oleaje" not in analysis and "Viento" not in analysis and "Estado" not in analysis:
        failures.append("analysis should use labelled rows (Oleaje/Viento/…)")

    band_peak = PeakDayForecast(
        peak_id="la_aguada",
        local_date="2026-10-16",
        state=ForecastState.RESOLVED,
        condition=SurfGrade.FAIR,
        size=peak.size,
        best_window=BestWindow(
            start_at=datetime(2026, 10, 16, 6, 0, tzinfo=tz),
            end_at=datetime(2026, 10, 16, 20, 0, tzinfo=tz),
            duration_minutes=840,
            condition=SurfGrade.FAIR,
            support="contiguous",
        ),
        confidence=peak.confidence,
        reason_codes=[],
    )
    if favorable_window_from_peak(band_peak) is not None:
        failures.append("06:00–20:00 must not be favorable_window")
    return failures


def _check_orientation_compatible_worth() -> list[str]:
    """Never co-recommend E-facing Aguada with S-facing Serena/Balconada."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from surf_forecast.domain.models import (
        BestWindow,
        ConfidenceAssessment,
        ConfidenceLevel,
        DirectionSector,
        ForecastState,
        NumericRange,
        PeakDayForecast,
        PeakProfile,
        ProfileStatus,
        SurfGrade,
        SurfableSizeEstimate,
    )
    from surf_forecast.domain.presentation import rank_worth_spots

    failures: list[str] = []
    tz = ZoneInfo("America/Montevideo")
    start = datetime(2026, 10, 16, 8, 0, tzinfo=tz)
    end = datetime(2026, 10, 16, 11, 0, tzinfo=tz)

    def _peak(pid: str, grade: SurfGrade) -> PeakDayForecast:
        return PeakDayForecast(
            peak_id=pid,
            local_date="2026-10-16",
            state=ForecastState.RESOLVED,
            condition=grade,
            size=SurfableSizeEstimate(1.0, 0.8, 0.7, 0.9, 0.75, 0.6, 0.9),
            best_window=BestWindow(start, end, 180, grade, "contiguous"),
            confidence=ConfidenceAssessment(ConfidenceLevel.MEDIUM, [], []),
            reason_codes=[],
        )

    def _profile(pid: str, name: str, orient: float) -> PeakProfile:
        return PeakProfile(
            peak_id=pid,
            name=name,
            zone_id="la_paloma",
            latitude=-34.66,
            longitude=-54.15,
            orientation_deg=orient,
            ideal_swell_sectors=[DirectionSector(0, 180)],
            ideal_period_s=NumericRange(8, 16),
            status=ProfileStatus.PROVISIONAL,
            profile_version="1",
            schema_version="1",
            updated_at="2026-01-01",
        )

    profiles = {
        "la_aguada": _profile("la_aguada", "La Aguada", 90.0),
        "la_serena": _profile("la_serena", "La Serena", 180.0),
        "la_balconada": _profile("la_balconada", "La Balconada", 180.0),
        "zanja_honda": _profile("zanja_honda", "Zanja Honda", 180.0),
    }
    mixed = rank_worth_spots(
        [
            _peak("la_aguada", SurfGrade.GOOD),
            _peak("la_serena", SurfGrade.FAIR),
            _peak("la_balconada", SurfGrade.FAIR),
        ],
        profile_by_id=profiles,
    )
    mixed_ids = [w["peak_id"] for w in mixed]
    if mixed_ids != ["la_aguada"]:
        failures.append(f"Aguada(E) must not co-list S beaches, got {mixed_ids}")

    south = rank_worth_spots(
        [
            _peak("la_serena", SurfGrade.GOOD),
            _peak("la_balconada", SurfGrade.FAIR),
            _peak("zanja_honda", SurfGrade.FAIR),
            _peak("la_aguada", SurfGrade.FAIR),
        ],
        profile_by_id=profiles,
    )
    south_ids = [w["peak_id"] for w in south]
    if south_ids[0] != "la_serena":
        failures.append(f"best south should be la_serena, got {south_ids}")
    if "la_aguada" in south_ids:
        failures.append("S-facing list must exclude Aguada(E)")
    if "la_balconada" not in south_ids:
        failures.append("same-orientation Balconada should remain among spots")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
