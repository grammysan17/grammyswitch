"""CLI: parse utterance → optional bridge call."""

from __future__ import annotations

import argparse
import json
import sys

from intent.parser import ParseError, parse_utterance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse voice utterance to tool call")
    parser.add_argument("utterance", nargs="?", help="Utterance text")
    parser.add_argument("--text", dest="text_flag", help="Utterance text (alt)")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send parsed tool call to bridge via bridge.client",
    )
    parser.add_argument("--socket", default=None, help="Bridge socket path")
    args = parser.parse_args(argv)
    utterance = args.text_flag or args.utterance
    if not utterance:
        print("utterance required", file=sys.stderr)
        return 2
    try:
        intent = parse_utterance(utterance)
    except ParseError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    payload = intent.to_tool_call()
    print(json.dumps({"ok": True, "intent": payload}, indent=2))
    if args.send:
        from bridge.client import call

        resp = call(intent.method, intent.params, socket_path=args.socket)
        print(json.dumps(resp, indent=2))
        return 0 if resp.get("ok") else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
