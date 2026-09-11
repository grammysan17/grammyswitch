# VW plugin skeleton (Mac)

C++ VCOM-style socket listener + Python `vs` helpers for Vectorworks 2026.

**This tree does not include `run_script` / eval.** Tools are allowlisted: `get_document_info`, `get_selection`, `create_line`.

## Layout

| Path | Role |
| --- | --- |
| `src/` | C++ skeleton: socket accept, command queue, idle pump comments |
| `python/` | Bounded `vs` helpers (create_line, get_document_info, get_selection) |
| `docs/MAC_BUILD.md` | Xcode / VW SDK build notes |

## Threading (critical)

- Socket thread **must not** call VW drawing APIs directly.
- Queue commands; pump on idle / main-thread timer; return async results with request IDs.
- See comments in `src/BridgePlugin.cpp`.

## Linux note

C++ does not build against VW SDK on this Linux box. Use `BRIDGE_MOCK=1` for protocol demos. Compile on Mac with SDK.
