#!/usr/bin/env bash
# End-to-end Phase 0 mock: start bridge → create_line via intent → print success.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export BRIDGE_MOCK=1

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

SOCK="$(mktemp -u /tmp/vw-voice-bridge.XXXXXX).sock"
export BRIDGE_SOCKET="$SOCK"
cleanup() {
  if [[ -n "${BRIDGE_PID:-}" ]] && kill -0 "$BRIDGE_PID" 2>/dev/null; then
    kill "$BRIDGE_PID" 2>/dev/null || true
    wait "$BRIDGE_PID" 2>/dev/null || true
  fi
  rm -f "$SOCK"
}
trap cleanup EXIT

echo "==> Starting mock bridge on $SOCK"
"$PYTHON" -m bridge.server "$SOCK" &
BRIDGE_PID=$!

for _ in $(seq 1 50); do
  if [[ -S "$SOCK" ]]; then
    break
  fi
  sleep 0.05
done
if [[ ! -S "$SOCK" ]]; then
  echo "ERROR: bridge socket did not appear: $SOCK" >&2
  exit 1
fi

MODE=$(stat -c '%a' "$SOCK" 2>/dev/null || stat -f '%OLp' "$SOCK")
echo "==> Socket ready (mode=$MODE)"

echo "==> get_document_info"
"$PYTHON" -m bridge.client get_document_info --socket "$SOCK"

echo "==> Intent: draw a 10 foot line"
INTENT_JSON=$("$PYTHON" -m intent.cli "draw a 10 foot line")
echo "$INTENT_JSON"

echo "==> create_line via bridge client (120 inches)"
RESP=$("$PYTHON" -m bridge.client create_line \
  --params '{"x1":0,"y1":0,"x2":120,"y2":0}' \
  --socket "$SOCK")
echo "$RESP"

export DEMO_RESP="$RESP"
"$PYTHON" -c '
import json, os
resp = json.loads(os.environ["DEMO_RESP"])
assert resp.get("ok") is True, resp
result = resp["result"]
assert result.get("handle"), result
assert abs(float(result["length_inches"]) - 120.0) < 1e-6, result
print("SUCCESS: create_line mock OK — handle=%s length_inches=%s" % (
    result["handle"], result["length_inches"]))
'

echo "==> Demo complete"
