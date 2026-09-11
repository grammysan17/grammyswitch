"""Allowlisted bridge tools. No run_script / eval."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


ALLOWED_METHODS = frozenset(
    {"ping", "get_document_info", "get_selection", "create_line"}
)


@dataclass
class MockDocument:
    """In-memory document used when BRIDGE_MOCK=1."""

    name: str = "Mock Document"
    units: str = "inches"
    units_per_inch: float = 1.0
    vw_version: str = "2026-mock"
    objects: list[dict[str, Any]] = field(default_factory=list)
    selection: list[str] = field(default_factory=list)
    _line_seq: int = 0

    def document_info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "units": self.units,
            "units_per_inch": self.units_per_inch,
            "vw_version": self.vw_version,
            "mock": True,
        }

    def get_selection(self) -> dict[str, Any]:
        objs = [o for o in self.objects if o["handle"] in self.selection]
        return {
            "count": len(objs),
            "objects": [
                {"handle": o["handle"], "type": o["type"]} for o in objs
            ],
        }

    def create_line(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> dict[str, Any]:
        self._line_seq += 1
        handle = f"line_{self._line_seq}"
        length = math.hypot(x2 - x1, y2 - y1)
        obj = {
            "handle": handle,
            "type": "line",
            "x1": float(x1),
            "y1": float(y1),
            "x2": float(x2),
            "y2": float(y2),
            "length_inches": length,
        }
        self.objects.append(obj)
        return {
            "handle": handle,
            "x1": obj["x1"],
            "y1": obj["y1"],
            "x2": obj["x2"],
            "y2": obj["y2"],
            "length_inches": length,
        }


class ToolDispatcher:
    """Dispatch allowlisted methods against a document backend."""

    def __init__(self, document: MockDocument | None = None) -> None:
        self.document = document or MockDocument()

    def dispatch(self, method: str, params: dict[str, Any] | None) -> dict[str, Any]:
        params = params or {}
        if method not in ALLOWED_METHODS:
            raise ValueError(f"unknown_method:{method}")
        if method == "ping":
            return {"pong": True}
        if method == "get_document_info":
            return self.document.document_info()
        if method == "get_selection":
            return self.document.get_selection()
        if method == "create_line":
            required = ("x1", "y1", "x2", "y2")
            missing = [k for k in required if k not in params]
            if missing:
                raise ValueError(f"missing_params:{','.join(missing)}")
            return self.document.create_line(
                float(params["x1"]),
                float(params["y1"]),
                float(params["x2"]),
                float(params["y2"]),
            )
        raise ValueError(f"unknown_method:{method}")
