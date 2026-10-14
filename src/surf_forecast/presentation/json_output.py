"""JSON serializer for the shared presentation model."""

from __future__ import annotations

import json
import sys
from typing import Any

from surf_forecast.domain.presentation import ForecastPresentation


def emit_json(payload: dict[str, Any] | ForecastPresentation) -> None:
    document = payload.payload if isinstance(payload, ForecastPresentation) else payload
    sys.stdout.write(json.dumps(document, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def emit_error(code: str, message: str, details: dict[str, Any] | None = None) -> None:
    emit_json(
        {
            "schema_version": "1.0.0",
            "error": {"code": code, "message": message, "details": details or {}},
        }
    )


def stderr(message: str) -> None:
    sys.stderr.write(message + "\n")
