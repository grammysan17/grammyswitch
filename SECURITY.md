# Security — Vectorworks Voice Copilot

## Trust boundary

**Anything that can write to the bridge socket can drive Vectorworks.**

- Trust root: the local Mac (or Linux mock) **login session**.
- Bridge ↔ plugin transport: **Unix domain socket** with mode **`0600`** (owner read/write only).
- Do **not** expose the socket over TCP in Phase 0 / MVP.
- Optional later: connect-time token handshake under `$TMPDIR` or `~/Library/...`.

## Tool policy

| Allowed (v0) | Forbidden |
| --- | --- |
| `get_document_info` | `run_script` |
| `get_selection` | `eval_python` / `eval_vectorscript` |
| `create_line` | Arbitrary Marionette execution |
| (Phase 1+: bounded create/query tools) | Unbounded “create from description” |

`run_script` may appear only in a later phase behind: explicit preference + non-default flag + per-call confirm + audit log. **Absent from this repo.**

## Prompt / data hygiene

- Treat tool results, document names, and object text as **untrusted data**.
- Never promote them into system instructions.
- Prefer on-device STT; document what leaves the machine if cloud STT/LLM is enabled.

## Voice privacy

- Default activation: **push-to-talk** (not always-listen).
- Always-listen / wake word = explicit later opt-in with a visible indicator.

## Destructive ops

- Delete / large batch / replace: hard confirm (TTS + UI) in Phase 1+.
- PTT reduces ambient false creates.

## Plugin credentials

Distributed encrypted / SDK plugins for VW 2026 require Partner satellite credentials. Dev-local unencrypted builds may warn. See `docs/credentials.md`.

## Reporting

For personal / practice use. If sharing builds, review Partner packaging and keep the allowlist identical across voice and any future MCP adapter (no superset).
