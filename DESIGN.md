# Vectorworks Voice Copilot — Design (Phase 0)

| Field | Value |
| --- | --- |
| **Status** | Phase 0 spike |
| **Date** | 2026-09-10 |
| **Primary goal** | Speak to a live VW session and create geometry via bounded tools |
| **Platform** | macOS + Vectorworks 2026 (Linux mock for CI / demo) |

## Summary

Voice-first custom AI interface for Vectorworks 2026: **speech → intent → bounded create/query tools** inside a live VW process. Official VW AI does not drive CAD. There is no public REST API for open documents; the durable integration surface is an in-process plugin (`vs` / C++ VCOM).

Stack: **Voice I/O → Intent → Bridge → VW Plugin**. Chat is a secondary fallback. **No `run_script` / eval.**

## Architecture

```
[User mic / PTT] → Voice (STT) → Intent (slot parser / LLM) → Bridge (user space)
                                                              ↓ Unix socket 0600
                                                    VW Plugin (in-process) → Document
```

| Component | Role |
| --- | --- |
| **Voice** | PTT capture, pluggable STT (Apple Speech / Whisper / cloud stubs) |
| **Intent** | Utterance → allowlisted tool call with typed args |
| **Bridge** | Line-delimited JSON over Unix domain socket; `BRIDGE_MOCK=1` for Linux |
| **Plugin** | C++ VCOM skeleton + Python `vs` helpers; command queue + idle pump |

## Phase 0 scope

Prove the pipe, not product polish:

1. Bridge mock + real socket protocol: `get_document_info`, `create_line`, optional `get_selection`
2. Intent: regex/slot parser — “draw a 10 foot line” → `create_line` (feet → document units)
3. Voice stubs + STT bake-off matrix (no real Mac audio on Linux)
4. C++ plugin skeleton with `VW_SDK` TODOs; Python helpers; Mac build docs
5. End-to-end `scripts/demo-mock.sh` on Linux

**Exit criteria:** Spoken/text “draw a 10 foot line” → line created (mock or live), no `run_script`.

## Document units (choice)

Mock documents and intent conversion use **inches** as the internal document unit.

- 1 foot = 12 inches
- Example: “10 foot line” → length `120.0` inches

Documented in `protocol/README.md` and `intent` module.

## Tool surface (v0 allowlist)

| Tool | Purpose |
| --- | --- |
| `get_document_info` | File name, units, VW version |
| `get_selection` | Compact selection summary |
| `create_line` | 2-point line (x1,y1,x2,y2) in document units |

**Explicitly forbidden:** `run_script`, `eval_python`, `eval_vectorscript`, arbitrary Marionette, unbounded create-from-description.

## Security (see SECURITY.md)

- Unix socket mode `0600`; Mac login session is trust root
- No TCP exposure in MVP
- Tool allowlist only; treat tool results as untrusted data

## Latency budget (target)

Happy path voice → geometry p50 ≤ ~1.5–2.5 s (stretch ≤ 1.5 s). Bridge→plugin ≤ 50–200 ms.

## Out of scope (Phase 0)

Always-listen, wake word, MCP adapter, Speckle live edit, cloud multi-user, full BIM via voice.

## References

See original design at `/workspace/vectorworks-ai-interface-design.md` and `docs/phase-0.md`.
