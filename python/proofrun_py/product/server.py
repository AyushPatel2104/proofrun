"""Local product HTTP server — trusted adapter + static viz UI."""

from __future__ import annotations

import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, Tuple
from urllib.parse import urlparse

from proofrun_py.bridge import project_root
from proofrun_py.product.validate import ValidationError
from proofrun_py.product.workflow import (
    benchmark_workflow,
    catalog_payload,
    generate_input,
    health,
    run_workflow,
)


def _json_bytes(obj: Any, status: int = 200) -> Tuple[int, bytes, str]:
    return status, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8"


def make_handler(static_root: Path) -> type:
    routes_get: Dict[str, Callable[[], Tuple[int, bytes, str]]] = {
        "/api/health": lambda: _json_bytes(health()),
        "/api/catalog": lambda: _json_bytes(catalog_payload()),
    }

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> Dict[str, Any]:
            length = int(self.headers.get("Content-Length") or "0")
            if length <= 0:
                return {}
            if length > 100_000:
                raise ValidationError("Request body too large.")
            raw = self.rfile.read(length)
            try:
                data = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValidationError("Request must be valid JSON.") from exc
            if not isinstance(data, dict):
                raise ValidationError("Request JSON must be an object.")
            return data

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in routes_get:
                status, body, ctype = routes_get[path]()
                self._send(status, body, ctype)
                return
            self._serve_static(path)

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                body = self._read_json()
                if path == "/api/run":
                    payload = run_workflow(body)
                elif path == "/api/generate":
                    payload = generate_input(body)
                elif path == "/api/benchmark":
                    payload = benchmark_workflow(body)
                else:
                    self._send(404, b'{"error":"not found"}', "application/json")
                    return
                self._send(200, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")
            except ValidationError as exc:
                self._send(
                    400,
                    json.dumps({"error": str(exc), "status": "validation_error"}).encode("utf-8"),
                    "application/json; charset=utf-8",
                )
            except Exception:  # noqa: BLE001 — last-resort product boundary
                sys.stderr.write("product server internal error\n")
                self._send(
                    500,
                    json.dumps(
                        {
                            "error": (
                                "Internal product error.\n"
                                "Why: an unexpected failure occurred in the local server.\n"
                                "Fix: retry; if it continues, rebuild the engine and restart the server."
                            ),
                            "status": "internal_error",
                        }
                    ).encode("utf-8"),
                    "application/json; charset=utf-8",
                )

        def _serve_static(self, path: str) -> None:
            if path == "/" or path == "":
                path = "/index.html"
            # Prevent path traversal
            rel = path.lstrip("/").replace("\\", "/")
            if ".." in rel.split("/"):
                self._send(400, b"bad path", "text/plain")
                return
            file_path = (static_root / rel).resolve()
            try:
                file_path.relative_to(static_root.resolve())
            except ValueError:
                self._send(400, b"bad path", "text/plain")
                return
            if not file_path.is_file():
                self._send(404, b"not found", "text/plain")
                return
            data = file_path.read_bytes()
            ctype = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            self._send(200, data, ctype)

    return Handler


def main(host: str = "127.0.0.1", port: int = 8080) -> None:
    root = project_root()
    static_root = root / "viz"
    if not static_root.is_dir():
        raise SystemExit(f"viz directory missing: {static_root}")
    handler = make_handler(static_root)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"ProofRun product server: http://{host}:{port}/")
    print(f"Serving UI from {static_root}")
    print("API: /api/health /api/catalog /api/generate /api/run /api/benchmark")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    h = "127.0.0.1"
    p = 8080
    if len(sys.argv) >= 2:
        p = int(sys.argv[1])
    main(h, p)
