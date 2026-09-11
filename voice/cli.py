"""Voice CLI: text or wav → STT stub → optional intent parse."""

from __future__ import annotations

import argparse
import json
import sys

from voice.stt import get_backend, list_backends


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PTT-oriented STT CLI (stubs OK on Linux)")
    parser.add_argument("--backend", default="passthrough", choices=list_backends())
    parser.add_argument("--text", help="Utterance text (simulates PTT transcript)")
    parser.add_argument("--wav", help="Path to wav (stub on Linux)")
    parser.add_argument(
        "--parse",
        action="store_true",
        help="Run intent parser on transcript",
    )
    args = parser.parse_args(argv)
    if not args.text and not args.wav:
        print("provide --text or --wav", file=sys.stderr)
        return 2
    backend = get_backend(args.backend)
    if args.text:
        tr = backend.transcribe_text(args.text)
    else:
        tr = backend.transcribe_wav(args.wav)
    out = {
        "text": tr.text,
        "confidence": tr.confidence,
        "backend": tr.backend,
        "meta": tr.meta,
    }
    if args.parse and tr.text and not tr.text.startswith("["):
        from intent.parser import ParseError, parse_utterance

        try:
            intent = parse_utterance(tr.text)
            out["intent"] = intent.to_tool_call()
        except ParseError as exc:
            out["intent_error"] = str(exc)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
