# Bridge protocol

## Transport

- **Newline-delimited JSON** over a **Unix domain socket**.
- One request object per line; one response object per line (same `id`).
- Real sockets are created with mode **`0600`**.
- Environment:
  - `BRIDGE_MOCK=1` — in-process / temp-socket mock (Linux CI & demo)
  - `BRIDGE_SOCKET` — path to socket (default: `/tmp/vw-voice-bridge.sock` or mock temp path)

## Units

Document coordinates are **inches**.

| Spoken | Document |
| --- | --- |
| 1 foot / 1 ft / 1' | 12 inches |
| 10 foot line | length 120.0 |

## Methods (Phase 0)

### `ping`

Params: `{}` → `{ "pong": true }`

### `get_document_info`

Params: `{}`

```json
{"id":"1","method":"get_document_info","params":{}}
```

```json
{"id":"1","ok":true,"result":{"name":"Mock Document","units":"inches","units_per_inch":1.0,"vw_version":"2026-mock","mock":true}}
```

### `get_selection`

Params: `{}` → `{ "count": 0, "objects": [] }` (mock starts empty; after creates, optional tracking).

### `create_line`

Params: `{ "x1", "y1", "x2", "y2" }` in inches.

```json
{"id":"2","method":"create_line","params":{"x1":0,"y1":0,"x2":120,"y2":0}}
```

```json
{"id":"2","ok":true,"result":{"handle":"line_1","x1":0,"y1":0,"x2":120,"y2":0,"length_inches":120.0}}
```

## Errors

```json
{"id":"3","ok":false,"error":{"code":"unknown_method","message":"..."}}
```

## Forbidden

No `run_script`, `eval`, or arbitrary code methods in this protocol.
