"""CLI client for the bridge socket."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import uuid
from typing import Any


DEFAULT_SOCKET = "/tmp/vw-voice-bridge.sock"


def call(
    method: str,
    params: dict[str, Any] | None = None,
    *,
    socket_path: str | None = None,
    timeout: float = 5.0,
    req_id: str | None = None,
) -> dict[str, Any]:
    path = socket_path or os.environ.get("BRIDGE_SOCKET") or DEFAULT_SOCKET
    req = {
        "id": req_id or str(uuid.uuid4()),
        "method": method,
        "params": params or {},
    }
    line = json.dumps(req) + "\n"
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(path)
        sock.sendall(line.encode("utf-8"))
        buf = b""
        while b"\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
    finally:
        sock.close()
    text = buf.decode("utf-8", errors="replace").strip().split("\n", 1)[0]
    if not text:
        raise RuntimeError("empty response from bridge")
    return json.loads(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VW Voice Copilot bridge client")
    parser.add_argument("method", help="Tool method name")
    parser.add_argument(
        "--params",
        default="{}",
        help="JSON object of params",
    )
    parser.add_argument(
        "--socket",
        default=None,
        help="Unix socket path (or BRIDGE_SOCKET)",
    )
    args = parser.parse_args(argv)
    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        print(f"invalid --params JSON: {exc}", file=sys.stderr)
        return 2
    try:
        resp = call(args.method, params, socket_path=args.socket)
    except Exception as exc:  # noqa: BLE001
        print(f"client error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
