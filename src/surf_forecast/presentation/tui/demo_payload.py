"""Fixed presentation payload for --demo (no network). Brief method step 0."""

from __future__ import annotations

from typing import Any


def build_demo_payload() -> dict[str, Any]:
    """Two-day DayBrief payload matching schema 1.2.0 with labelled analysis."""
    hoy_brief = {
        "label": "Hoy",
        "condition": "fair",
        "condition_label": "Razonable",
        "height": {
            "minimum_m": 1.1,
            "maximum_m": 1.6,
            "display": "1,1–1,6 m",
            "kind": "derived",
            "caption": "Rango estimado de ola surfeable",
        },
        "metrics": {
            "swell": [{"dir_label": "E", "period_s": 8, "period_display": "8 s"}],
            "wind": {
                "display": "SSW 25–33 km/h",
                "dir_display": "SSW 25–33 km/h",
                "intensity_display": "Fuerte",
                "start_dir": "SSW",
                "end_dir": "SSW",
                "start_intensity": "fuerte",
                "end_intensity": "fuerte",
            },
        },
        "rating": {"score": 3.0},
        "analysis": (
            "Oleaje   Del E, 8 s, en descenso.\n"
            "Viento   SSW fuerte.\n"
            "Mejor    Por la tarde, 16:00–20:00.\n"
            "Lectura  Con ese viento la forma tiende a verse más picada"
        ),
        "best_peak": {
            "peak_id": "la_aguada",
            "display_name": "La Aguada",
            "condition": "fair",
            "condition_label": "Razonable",
            "reason": None,
        },
        "favorable_window": {
            "display": "16:00–20:00",
            "start_local": "16:00",
            "end_local": "20:00",
        },
        "limitations": [],
        "headline": "Razonable",
        "body": "Oleaje   Del E, 8 s, en descenso.",
        "caution": None,
        "go_window": {"display": "16:00–20:00"},
        "worth_spots": [
            {
                "peak_id": "la_aguada",
                "display_name": "La Aguada",
                "condition": "fair",
                "condition_label": "Razonable",
                "reason_short": None,
            }
        ],
        "empty_spots_message": None,
    }
    manana_brief = {
        "label": "Mañana",
        "condition": "good",
        "condition_label": "Buena",
        "height": {
            "minimum_m": 1.5,
            "maximum_m": 2.1,
            "display": "1,5–2,1 m",
            "kind": "derived",
            "caption": "Rango estimado de ola surfeable",
        },
        "metrics": {
            "swell": [{"dir_label": "E", "period_s": 9, "period_display": "9 s"}],
            "wind": {
                "display": "SSW 28–39 km/h",
                "dir_display": "SSW 28–39 km/h",
                "intensity_display": "Muy fuerte → fuerte",
                "start_dir": "SSW",
                "end_dir": "S",
                "start_intensity": "muy fuerte",
                "end_intensity": "fuerte",
            },
        },
        "rating": {"score": 4.0},
        "analysis": (
            "Oleaje   Del E, 9 s, en aumento.\n"
            "Viento   SSW→S muy fuerte→fuerte.\n"
            "Mejor    Por la mañana.\n"
            "Lectura  Con ese viento la forma tiende a verse más picada"
        ),
        "best_peak": {
            "peak_id": "la_aguada",
            "display_name": "La Aguada",
            "condition": "good",
            "condition_label": "Buena",
            "reason": None,
        },
        "favorable_window": None,
        "limitations": [],
        "headline": "Buena",
        "body": "Oleaje   Del E, 9 s, en aumento.",
        "caution": None,
        "go_window": None,
        "worth_spots": [
            {
                "peak_id": "la_aguada",
                "display_name": "La Aguada",
                "condition": "good",
                "condition_label": "Buena",
                "reason_short": None,
            }
        ],
        "empty_spots_message": None,
    }
    return {
        "schema_version": "1.2.0",
        "overall_status": "complete",
        "snapshot_id": "demo_fixed",
        "query": {
            "mode": "demo",
            "timezone": "America/Montevideo",
            "horizon_start": "2026-10-16",
            "horizon_end": "2026-10-17",
        },
        "query_times": {"executed_at_local": "2026-10-16 15:00 UYT"},
        "data_times": {
            "meteorological_updated_at_local": "2026-10-16 14:00 UYT",
            "label": "Actualización de datos (no es la hora de consulta)",
        },
        "days": [
            {
                "local_date": "2026-10-16",
                "display_title": "Viernes 16/10",
                "state": "resolved",
                "day_rating": {"score": 3.0, "source_peak_id": "la_aguada"},
                "brief": hoy_brief,
            },
            {
                "local_date": "2026-10-17",
                "display_title": "Sábado 17/10",
                "state": "resolved",
                "day_rating": {"score": 4.0, "source_peak_id": "la_aguada"},
                "brief": manana_brief,
            },
        ],
        "attribution": {
            "text": "Datos: Open-Meteo (CC BY 4.0)",
            "provider_url": "https://open-meteo.com/",
        },
        "shared_regional_input": {
            "notice_label": "Los picos cercanos comparten la misma celda regional del modelo."
        },
    }
