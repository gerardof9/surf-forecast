"""Non-interactive commands and TUI launch."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from surf_forecast.application.forecast_service import (
    ForecastUnavailable,
    PersistenceError,
    load_detail,
    run_forecast,
)
from surf_forecast.application.profile_service import list_profiles
from surf_forecast.application.replay_service import load_fixture, replay_fixture, replay_snapshot
from surf_forecast.domain.models import QueryMode, QueryRequest
from surf_forecast.domain.presentation import CONDITION_LABELS, STATE_LABELS, spanish_reasons
from surf_forecast.presentation.json_output import emit_error, emit_json, stderr
from surf_forecast.storage.snapshots import latest_snapshot, read_snapshot

EXIT_OK = 0
EXIT_DEGRADED = 1
EXIT_USAGE = 2
EXIT_UNAVAILABLE = 3
EXIT_PERSISTENCE = 4
EXIT_REPLAY = 5


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE
    command = getattr(args, "command", None) or "tui"
    try:
        if command == "tui":
            from surf_forecast.presentation.tui.app import run_tui

            return run_tui()
        if command == "forecast":
            return _cmd_forecast(args)
        if command == "detail":
            return _cmd_detail(args)
        if command == "profiles":
            return _cmd_profiles(args)
        if command == "sources":
            return _cmd_sources(args)
        if command == "snapshots":
            return _cmd_snapshots(args)
        if command == "fixtures":
            return _cmd_fixtures(args)
        stderr("Comando no reconocido")
        return EXIT_USAGE
    except ForecastUnavailable as exc:
        return _fail(args, "forecast_unavailable", str(exc), EXIT_UNAVAILABLE)
    except PersistenceError:
        return _fail(args, "snapshot_write_failed", "No se pudo guardar el snapshot", EXIT_PERSISTENCE)
    except ValueError as exc:
        return _fail(args, "configuration_invalid", str(exc), EXIT_USAGE)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="surf_forecast")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("tui")
    forecast = sub.add_parser("forecast")
    _add_common(forecast)
    forecast.add_argument("--refresh", action="store_true")
    forecast.add_argument("--stored-only", action="store_true")
    forecast.add_argument("--fixture", type=Path)
    detail = sub.add_parser("detail")
    detail.add_argument("--date", required=True)
    detail.add_argument("--peak", required=True)
    detail.add_argument("--snapshot")
    detail.add_argument("--json", action="store_true")
    profiles = sub.add_parser("profiles")
    profiles_sub = profiles.add_subparsers(dest="profiles_command")
    profiles_list = profiles_sub.add_parser("list")
    profiles_list.add_argument("--json", action="store_true")
    profiles_validate = profiles_sub.add_parser("validate")
    profiles_validate.add_argument("--json", action="store_true")
    sources = sub.add_parser("sources")
    sources_sub = sources.add_subparsers(dest="sources_command")
    status = sources_sub.add_parser("status")
    status.add_argument("--snapshot")
    status.add_argument("--json", action="store_true")
    snapshots = sub.add_parser("snapshots")
    snaps_sub = snapshots.add_subparsers(dest="snapshots_command")
    show = snaps_sub.add_parser("show")
    show.add_argument("snapshot_id")
    show.add_argument("--json", action="store_true")
    replay = snaps_sub.add_parser("replay")
    replay.add_argument("snapshot_id")
    replay.add_argument("--json", action="store_true")
    fixtures = sub.add_parser("fixtures")
    fix_sub = fixtures.add_subparsers(dest="fixtures_command")
    fix_replay = fix_sub.add_parser("replay")
    fix_replay.add_argument("path", type=Path)
    fix_replay.add_argument("--now", required=True)
    fix_replay.add_argument("--json", action="store_true")
    return parser


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--now")


def _cmd_forecast(args: argparse.Namespace) -> int:
    if args.refresh and args.stored_only:
        return _fail(args, "configuration_invalid", "--refresh y --stored-only no se pueden combinar", EXIT_USAGE)
    fixture = load_fixture(args.fixture) if args.fixture else None
    mode = QueryMode.NORMAL
    if args.refresh:
        mode = QueryMode.FORCE_REFRESH
    if args.stored_only:
        mode = QueryMode.STORED_ONLY
    if fixture is not None:
        mode = QueryMode.FIXTURE_REPLAY
    request = QueryRequest(
        mode=mode,
        reference_time=_parse_now(getattr(args, "now", None)),
        timezone="America/Montevideo",
        fixture_path=str(args.fixture) if args.fixture else None,
        output_mode="json" if args.json else "human",
    )
    _result, presentation, code = run_forecast(request, fixture)
    if args.json:
        emit_json(presentation)
    else:
        _print_forecast(presentation.payload)
    return code


def _cmd_detail(args: argparse.Namespace) -> int:
    payload = load_detail(args.date, args.peak, args.snapshot)
    if args.json:
        emit_json(payload)
    else:
        peak = payload["peak"]
        print(f"{payload['snapshot_id']}  {args.date}  {args.peak}")
        print(f"{peak.get('condition_label')}  {peak.get('state')}")
        for slot in peak.get("reference_slots") or []:
            print(f"  {slot.get('local_hour')}  {slot.get('condition')}  {slot.get('wind_class')}")
        window = peak.get("best_window")
        if window:
            print(f"Ventana: {window['start_at']} – {window['end_at']}")
        else:
            print("Sin ventana de 2 horas")
    return EXIT_OK


def _cmd_profiles(args: argparse.Namespace) -> int:
    profiles = list_profiles()
    payload = {
        "schema_version": "1.0.0",
        "profiles": [
            {
                "peak_id": profile.peak_id,
                "name": profile.name,
                "status": profile.status.value,
                "profile_version": profile.profile_version,
                "validation_errors": profile.validation_errors,
                "estimated_fields": profile.estimated_fields,
            }
            for profile in profiles
        ],
    }
    if getattr(args, "json", False):
        emit_json(payload)
    else:
        for profile in profiles:
            extra = f"  errores: {', '.join(profile.validation_errors)}" if profile.validation_errors else ""
            print(f"{profile.peak_id:16}  {profile.status.value:12}  {profile.name}{extra}")
    return EXIT_OK


def _cmd_sources(args: argparse.Namespace) -> int:
    document = read_snapshot(args.snapshot) if args.snapshot else latest_snapshot()
    if document is None:
        raise ForecastUnavailable("snapshot_not_found")
    sources = document.get("presentation", {}).get("sources") or document.get("source_fetches") or []
    if args.json:
        emit_json({"schema_version": "1.0.0", "snapshot_id": document.get("snapshot_id"), "sources": sources})
    else:
        for source in sources:
            print(
                f"{source.get('source_id')}  {source.get('status')}  "
                f"modelo={source.get('model')}  corrida={source.get('model_run_availability')}"
            )
    return EXIT_OK


def _cmd_snapshots(args: argparse.Namespace) -> int:
    if args.snapshots_command == "show":
        document = read_snapshot(args.snapshot_id)
        if args.json:
            emit_json(document)
        else:
            print(document.get("snapshot_id"))
            print(document.get("created_at"))
            print(document.get("canonical_result_sha256"))
        return EXIT_OK
    if args.snapshots_command == "replay":
        payload, code = replay_snapshot(args.snapshot_id)
        if args.json:
            emit_json(payload)
        else:
            print("coincide" if payload.get("match") else "no coincide")
        return code
    return EXIT_USAGE


def _cmd_fixtures(args: argparse.Namespace) -> int:
    now = _parse_now(args.now)
    payload, code = replay_fixture(args.path, now, json_mode=args.json)
    if args.json:
        emit_json(payload)
    else:
        _print_forecast(payload)
    return code


def _print_forecast(payload: dict[str, Any]) -> None:
    print(f"Consulta {payload.get('query', {}).get('reference_time')}  snapshot {payload.get('snapshot_id')}")
    notice = payload.get("shared_regional_input", {}).get("notice_label")
    if notice:
        print(notice)
    print(payload.get("attribution", {}).get("text", ""))
    for day in payload.get("days", []):
        print(f"\n{day.get('local_date')}  {day.get('headline')}")
        for peak in day.get("peaks", []):
            mark = "*" if peak.get("highlighted") else " "
            label = peak.get("condition_label") or STATE_LABELS.get(peak.get("state"), peak.get("state"))
            print(f" {mark} {peak.get('peak_id'):16} {label}")
            for reason in spanish_reasons(peak.get("reason_codes") or []):
                print(f"     {reason}")


def _parse_now(value: str | None) -> datetime:
    if value is None:
        return datetime.now(ZoneInfo("America/Montevideo"))
    if value.endswith("Z"):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError(" --now debe incluir un desfase UTC")
    return parsed


def _fail(args: argparse.Namespace, code: str, message: str, exit_code: int) -> int:
    if getattr(args, "json", False):
        emit_error(code, message)
    else:
        stderr(message)
    return exit_code
