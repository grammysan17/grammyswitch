"""Regex / slot parser for Phase 0 voice utterances.

Document units: inches. Spoken feet → inches (×12).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# Internal document unit for mock + Phase 0.
DOCUMENT_UNITS = "inches"
INCHES_PER_FOOT = 12.0


class ParseError(ValueError):
    """Utterance could not be mapped to an allowlisted tool."""


@dataclass(frozen=True)
class Intent:
    method: str
    params: dict[str, Any]
    utterance: str
    confidence: float = 1.0

    def to_tool_call(self) -> dict[str, Any]:
        return {"method": self.method, "params": self.params}


_NUM = r"(?P<n>\d+(?:\.\d+)?)"
_UNIT = r"(?P<unit>feet|foot|ft|'|inches|inch|in|\")"


def feet_to_inches(feet: float) -> float:
    return float(feet) * INCHES_PER_FOOT


def to_document_units(value: float, unit: str) -> float:
    u = unit.lower().strip()
    if u in {"feet", "foot", "ft", "'"}:
        return feet_to_inches(value)
    if u in {"inches", "inch", "in", '"'}:
        return float(value)
    raise ParseError(f"unsupported unit: {unit}")


def parse_utterance(text: str) -> Intent:
    """Parse a natural utterance into an allowlisted Intent.

    Supported Phase 0 patterns (examples):
    - "draw a 10 foot line"
    - "create a 10 ft line"
    - "draw a line 10 feet long"
    - "make a 120 inch line"
    - "what units are we in?" / "document info" → get_document_info
    - "what's selected?" → get_selection
    """
    raw = (text or "").strip()
    if not raw:
        raise ParseError("empty utterance")
    lowered = raw.lower().rstrip(".!?")

    # Queries
    if re.search(
        r"\b(document info|what units|units are we|file name|vw version)\b",
        lowered,
    ):
        return Intent("get_document_info", {}, raw, confidence=0.95)
    if re.search(r"\b(what('?s| is) selected|get selection|selection)\b", lowered):
        return Intent("get_selection", {}, raw, confidence=0.9)

    # create_line patterns
    # "draw/create/make a 10 foot line" or "draw a line 10 feet long"
    m = re.search(
        rf"\b(?:draw|create|make)\s+(?:a\s+)?{_NUM}\s*{_UNIT}\s+line\b",
        lowered,
    )
    if not m:
        m = re.search(
            rf"\b(?:draw|create|make)\s+(?:a\s+)?line\s+(?:of\s+)?{_NUM}\s*{_UNIT}"
            r"(?:\s+long)?\b",
            lowered,
        )
    if not m:
        m = re.search(
            rf"\b(?:draw|create|make)\s+(?:a\s+)?line\b.*?{_NUM}\s*{_UNIT}",
            lowered,
        )
    if m:
        length = to_document_units(float(m.group("n")), m.group("unit"))
        # Default: horizontal line from origin along +X.
        params = {"x1": 0.0, "y1": 0.0, "x2": length, "y2": 0.0}
        return Intent("create_line", params, raw, confidence=0.95)

    raise ParseError(f"unrecognized utterance: {raw!r}")
