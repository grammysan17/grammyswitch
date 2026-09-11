"""Bounded Python helpers intended to run *inside* Vectorworks via vs.

On Linux / without VW these functions degrade to pure-Python mocks for unit tests.
They never expose run_script / eval.
"""

from __future__ import annotations

import math
from typing import Any


def _vs():
    try:
        import vs  # type: ignore  # provided inside Vectorworks

        return vs
    except ImportError:
        return None


def get_document_info() -> dict[str, Any]:
    vs = _vs()
    if vs is None:
        return {
            "name": "Mock Document",
            "units": "inches",
            "units_per_inch": 1.0,
            "vw_version": "2026-mock",
            "mock": True,
        }
    # VW_SDK / vs TODO: map real document name + units preference.
    name = getattr(vs, "GetDocumentFileName", lambda: "Untitled")()
    return {
        "name": name,
        "units": "inches",
        "units_per_inch": 1.0,
        "vw_version": "2026",
        "mock": False,
    }


def get_selection() -> dict[str, Any]:
    vs = _vs()
    if vs is None:
        return {"count": 0, "objects": []}
    # VW_SDK / vs TODO: walk selection with ForEachObject / FSActLayer patterns.
    return {"count": 0, "objects": []}


def create_line(x1: float, y1: float, x2: float, y2: float) -> dict[str, Any]:
    """Create a 2D line. Coordinates in document inches."""
    length = math.hypot(x2 - x1, y2 - y1)
    vs = _vs()
    if vs is None:
        return {
            "handle": "mock_line",
            "x1": float(x1),
            "y1": float(y1),
            "x2": float(x2),
            "y2": float(y2),
            "length_inches": length,
            "mock": True,
        }
    # Typical vs pattern (verify against VW 2026 docs):
    # h = vs.MoveTo(x1, y1); vs.LineTo(x2, y2)  — exact API is VW_SDK TODO.
    handle = None
    try:
        vs.MoveTo(float(x1), float(y1))
        vs.LineTo(float(x2), float(y2))
        handle = "vw_line"  # VW_SDK TODO: capture real handle from vs
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc), "ok": False}
    return {
        "handle": str(handle),
        "x1": float(x1),
        "y1": float(y1),
        "x2": float(x2),
        "y2": float(y2),
        "length_inches": length,
        "mock": False,
    }
