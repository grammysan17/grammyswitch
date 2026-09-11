"""Unix socket bridge server (newline-delimited JSON)."""

from __future__ import annotations

import json
import os
import socket
import stat
import sys
import threading
from pathlib import Path
from typing import Any

from bridge.tools import ToolDispatcher


DEFAULT_SOCKET = "/tmp/vw-voice-bridge.sock"


def make_response(
    req_id: str, *, ok: bool, result: Any = None, error: dict | None = None
) -> dict:
    out: dict[str, Any] = {"id": req_id, "ok": ok}
    if ok:
        out["result"] = result
    else:
        out["error"] = error or {"code": "error", "message": "unknown"}
    return out


def handle_request(dispatcher: ToolDispatcher, raw: str) -> dict:
    try:
        req = json.loads(raw)
    except json.JSONDecodeError as exc:
        return make_response(
            "?",
            ok=False,
            error={"code": "invalid_json", "message": str(exc)},
        )
    req_id = str(req.get("id", "?"))
    method = req.get("method")
    params = req.get("params") or {}
    if not method or not isinstance(method, str):
        return make_response(
            req_id,
            ok=False,
            error={"code": "invalid_request", "message": "method required"},
        )
    try:
        result = dispatcher.dispatch(method, params)
        return make_response(req_id, ok=True, result=result)
    except ValueError as exc:
        msg = str(exc)
        code = msg.split(":", 1)[0] if ":" in msg else "error"
        return make_response(
            req_id, ok=False, error={"code": code, "message": msg}
        )
    except Exception as exc:  # noqa: BLE001 — surface unexpected to client
        return make_response(
            req_id,
            ok=False,
            error={"code": "internal", "message": str(exc)},
        )


def _set_socket_mode_0600(path: str) -> None:
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def _client_loop(
    conn: socket.socket, dispatcher: ToolDispatcher, stop: threading.Event
) -> None:
    with conn:
        buf = b""
        conn.settimeout(1.0)
        while not stop.is_set():
            try:
                chunk = conn.recv(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode("utf-8", errors="replace").strip()
                if not text:
                    continue
                resp = handle_request(dispatcher, text)
                payload = (json.dumps(resp) + "\n").encode("utf-8")
                try:
                    conn.sendall(payload)
                except OSError:
                    return


def serve_forever(
    socket_path: str,
    dispatcher: ToolDispatcher | None = None,
    stop_event: threading.Event | None = None,
) -> None:
    """Bind Unix socket at socket_path with mode 0600 and serve clients."""
    dispatcher = dispatcher or ToolDispatcher()
    stop = stop_event or threading.Event()
    path = Path(socket_path)
    if path.exists():
        path.unlink()

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    _set_socket_mode_0600(socket_path)
    server.listen(8)
    server.settimeout(1.0)
    print(f"bridge listening on {socket_path} mode={oct(os.stat(socket_path).st_mode & 0o777)}", flush=True)

    threads: list[threading.Thread] = []
    try:
        while not stop.is_set():
            try:
                conn, _ = server.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            t = threading.Thread(
                target=_client_loop, args=(conn, dispatcher, stop), daemon=True
            )
            t.start()
            threads.append(t)
    finally:
        stop.set()
        try:
            server.close()
        except OSError:
            pass
        if path.exists():
            try:
                path.unlink()
            except OSError:
                pass


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mock = os.environ.get("BRIDGE_MOCK", "").strip() in {"1", "true", "True", "yes"}
    socket_path = os.environ.get("BRIDGE_SOCKET") or (
        argv[0] if argv else DEFAULT_SOCKET
    )
    if mock:
        # Prefer explicit path; demo script may pass a temp path via env.
        print(f"BRIDGE_MOCK=1 socket={socket_path}", flush=True)
    dispatcher = ToolDispatcher()
    try:
        serve_forever(socket_path, dispatcher)
    except KeyboardInterrupt:
        print("bridge stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
