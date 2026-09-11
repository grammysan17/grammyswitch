"""Guardrail: repo must not introduce run_script / eval tool surfaces."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = ("run_script", "eval_python", "eval_vectorscript")
SKIP_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", "GrammySwitch"}


class TestNoRunScript(unittest.TestCase):
    def test_no_forbidden_api_names_as_methods(self):
        """Fail if allowlisted code defines forbidden tool method strings as APIs.

        Mentions in SECURITY/docs as 'forbidden' are OK; executable allowlists must not include them.
        """
        from bridge.tools import ALLOWED_METHODS

        for name in FORBIDDEN:
            self.assertNotIn(name, ALLOWED_METHODS)

    def test_protocol_enum_clean(self):
        schema = (ROOT / "protocol" / "schema.json").read_text(encoding="utf-8")
        for name in FORBIDDEN:
            self.assertNotIn(f'"{name}"', schema)


if __name__ == "__main__":
    unittest.main()
