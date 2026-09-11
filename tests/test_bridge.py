"""Unit tests for mock bridge tools + socket round-trip."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

from bridge.client import call
from bridge.server import handle_request, serve_forever
from bridge.tools import ALLOWED_METHODS, MockDocument, ToolDispatcher


class TestToolDispatcher(unittest.TestCase):
    def setUp(self):
        self.disp = ToolDispatcher(MockDocument())

    def test_allowlist(self):
        self.assertIn("create_line", ALLOWED_METHODS)
        self.assertIn("get_document_info", ALLOWED_METHODS)
        self.assertIn("get_selection", ALLOWED_METHODS)
        self.assertNotIn("run_script", ALLOWED_METHODS)

    def test_ping(self):
        self.assertEqual(self.disp.dispatch("ping", {}), {"pong": True})

    def test_document_info_inches(self):
        info = self.disp.dispatch("get_document_info", {})
        self.assertEqual(info["units"], "inches")
        self.assertTrue(info["mock"])

    def test_create_line(self):
        result = self.disp.dispatch(
            "create_line", {"x1": 0, "y1": 0, "x2": 120, "y2": 0}
        )
        self.assertEqual(result["handle"], "line_1")
        self.assertAlmostEqual(result["length_inches"], 120.0)

    def test_unknown_method(self):
        with self.assertRaises(ValueError):
            self.disp.dispatch("run_script", {"code": "nope"})

    def test_missing_params(self):
        with self.assertRaises(ValueError):
            self.disp.dispatch("create_line", {"x1": 0})


class TestHandleRequest(unittest.TestCase):
    def setUp(self):
        self.disp = ToolDispatcher(MockDocument())

    def test_ok_json(self):
        raw = json.dumps(
            {"id": "1", "method": "create_line", "params": {"x1": 0, "y1": 0, "x2": 12, "y2": 0}}
        )
        resp = handle_request(self.disp, raw)
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["id"], "1")
        self.assertAlmostEqual(resp["result"]["length_inches"], 12.0)

    def test_bad_json(self):
        resp = handle_request(self.disp, "{not json")
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"]["code"], "invalid_json")


class TestSocketRoundTrip(unittest.TestCase):
    def test_mock_socket_create_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            sock_path = str(Path(tmp) / "test.sock")
            stop = threading.Event()
            disp = ToolDispatcher(MockDocument())
            t = threading.Thread(
                target=serve_forever,
                kwargs={
                    "socket_path": sock_path,
                    "dispatcher": disp,
                    "stop_event": stop,
                },
                daemon=True,
            )
            t.start()
            # Wait for socket file
            for _ in range(50):
                if Path(sock_path).exists():
                    break
                time.sleep(0.05)
            self.assertTrue(Path(sock_path).exists())
            mode = os.stat(sock_path).st_mode & 0o777
            self.assertEqual(mode, 0o600)

            info = call("get_document_info", socket_path=sock_path)
            self.assertTrue(info["ok"])
            self.assertEqual(info["result"]["units"], "inches")

            resp = call(
                "create_line",
                {"x1": 0, "y1": 0, "x2": 120, "y2": 0},
                socket_path=sock_path,
            )
            self.assertTrue(resp["ok"])
            self.assertEqual(resp["result"]["handle"], "line_1")

            stop.set()
            t.join(timeout=3)


class TestPluginHelpers(unittest.TestCase):
    def test_helpers_mock(self):
        from plugin.python.helpers import create_line, get_document_info

        info = get_document_info()
        self.assertEqual(info["units"], "inches")
        line = create_line(0, 0, 120, 0)
        self.assertTrue(line.get("mock"))
        self.assertAlmostEqual(line["length_inches"], 120.0)


if __name__ == "__main__":
    unittest.main()
