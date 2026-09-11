# Vectorworks Voice Copilot

Voice-first interface for Vectorworks 2026: speak create commands → bounded tools → live document geometry.

**Phase 0** proves the pipe on Linux (mock) and scaffolds the Mac plugin. No `run_script` / eval.

## Quickstart (< 10 min, Linux mock)

```bash
cd /workspace/grammyswitch

# Optional: venv
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"   # or: pip install pytest

# End-to-end mock demo
bash scripts/demo-mock.sh

# Unit tests
python -m pytest tests/ -v
```

Expected demo output includes `create_line` success with a mock handle.

## Layout

| Path | Purpose |
| --- | --- |
| `bridge/` | Python daemon: Unix socket JSON (newline-delimited); `BRIDGE_MOCK=1` |
| `intent/` | Regex/slot parser (“draw a 10 foot line” → `create_line`) |
| `voice/` | Pluggable STT stubs + bake-off matrix |
| `plugin/` | C++ VCOM skeleton + Python `vs` helpers + Mac build docs |
| `protocol/` | Request/response JSON schema |
| `docs/` | Phase 0 checklist, VW 2026 credentials |
| `scripts/demo-mock.sh` | Start mock bridge → send `create_line` → print success |
| `tests/` | Intent + mock bridge tests (Linux) |

## Document units

Internal / mock document units are **inches**. Spoken feet convert as `feet * 12`.

## Protocol sketch

Client → bridge (one JSON object per line):

```json
{"id":"1","method":"create_line","params":{"x1":0,"y1":0,"x2":120,"y2":0}}
```

Response:

```json
{"id":"1","ok":true,"result":{"handle":"line_1","length_inches":120.0}}
```

See `protocol/README.md`.

## Voice → geometry path

1. PTT / CLI text or wav → STT stub
2. Intent parser → allowlisted tool
3. Bridge (`BRIDGE_MOCK=1` or real socket) → plugin / mock store
4. Ack printed / TTS (later)

## Security

Mac login session is the trust root. Socket `0600`. No TCP. No arbitrary script execution. See `SECURITY.md`.

## License

MIT — see `LICENSE`.
