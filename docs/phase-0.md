# Phase 0 checklist

**Goal:** Prove voice/text → intent → bridge → create_line without `run_script`.

## Checklist

- [x] Monorepo scaffold (`bridge`, `intent`, `voice`, `plugin`, `protocol`, `tests`)
- [x] Protocol schema: request/response JSON (newline-delimited)
- [x] Bridge daemon with `BRIDGE_MOCK=1` implementing `get_document_info`, `create_line`, `get_selection`
- [x] Socket mode `0600` when creating real sockets
- [x] Intent parser: “draw a 10 foot line” → `create_line` (feet → inches)
- [x] Voice STT stubs + bake-off matrix docs; CLI accepts text or wav path
- [x] C++ VCOM-style plugin skeleton + Python helpers; Mac build README
- [x] **No** `run_script` / eval anywhere
- [x] `scripts/demo-mock.sh` end-to-end on Linux
- [x] Unit tests for intent + mock bridge
- [x] Docs: README quickstart, credentials, SECURITY
- [ ] Live VW 2026 Mac plugin round-trip (hardware / Partner credentials)
- [ ] STT bake-off on Graham’s Mac (Apple Speech vs Whisper vs cloud)
- [ ] Measure latency stages end-to-end on Mac
- [ ] Decision gate: adapt community socket lineage vs keep greenfield protocol

## Exit criteria

Spoken or typed “draw a 10 foot line” → line in active/mock doc, no `run_script`.

## How to verify on Linux

```bash
bash scripts/demo-mock.sh
python -m pytest tests/ -v
rg -n 'run_script|eval_python|eval_vectorscript' --glob '!**/.venv/**' || true
```
