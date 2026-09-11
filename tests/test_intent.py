"""Unit tests for intent parser."""

from __future__ import annotations

import math
import unittest

from intent.parser import (
    DOCUMENT_UNITS,
    INCHES_PER_FOOT,
    ParseError,
    feet_to_inches,
    parse_utterance,
)


class TestUnits(unittest.TestCase):
    def test_document_units_inches(self):
        self.assertEqual(DOCUMENT_UNITS, "inches")

    def test_feet_to_inches(self):
        self.assertEqual(feet_to_inches(10), 120.0)
        self.assertEqual(feet_to_inches(1), INCHES_PER_FOOT)


class TestParseCreateLine(unittest.TestCase):
    def test_draw_ten_foot_line(self):
        intent = parse_utterance("draw a 10 foot line")
        self.assertEqual(intent.method, "create_line")
        self.assertEqual(intent.params["x1"], 0.0)
        self.assertEqual(intent.params["y1"], 0.0)
        self.assertEqual(intent.params["x2"], 120.0)
        self.assertEqual(intent.params["y2"], 0.0)

    def test_create_ft_synonym(self):
        intent = parse_utterance("create a 10 ft line")
        self.assertEqual(intent.params["x2"], 120.0)

    def test_line_n_feet_long(self):
        intent = parse_utterance("draw a line 5 feet long")
        self.assertEqual(intent.params["x2"], 60.0)

    def test_inch_units(self):
        intent = parse_utterance("make a 120 inch line")
        self.assertEqual(intent.params["x2"], 120.0)

    def test_decimal_feet(self):
        intent = parse_utterance("draw a 2.5 foot line")
        self.assertAlmostEqual(intent.params["x2"], 30.0)


class TestParseQueries(unittest.TestCase):
    def test_document_info(self):
        intent = parse_utterance("what units are we in?")
        self.assertEqual(intent.method, "get_document_info")

    def test_selection(self):
        intent = parse_utterance("what's selected?")
        self.assertEqual(intent.method, "get_selection")


class TestParseErrors(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(ParseError):
            parse_utterance("")

    def test_unknown(self):
        with self.assertRaises(ParseError):
            parse_utterance("make the façade better")


class TestLengthMath(unittest.TestCase):
    def test_horizontal_length(self):
        intent = parse_utterance("draw a 10 foot line")
        p = intent.params
        length = math.hypot(p["x2"] - p["x1"], p["y2"] - p["y1"])
        self.assertAlmostEqual(length, 120.0)


if __name__ == "__main__":
    unittest.main()
