"""Customer-only remote testing launcher for Wagtopia."""

from __future__ import annotations

import argparse
import atexit
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui.cstc.suite_utils import default_demo_profile, find_open_port, health_check, wait_for_health  # noqa: E402

CUSTOMER_ALLOWED_API_PREFIXES = (
    "/api/v1/clinical-report",
    "/api/v1/store",
    "/api/v1/catalog",
    "/api/v1/analyze",
)

CUSTOMER_BLOCKED_PREFIXES = (
    "/debug/",
    "/api/v1/ppie/",
    "/api/v1/science/",
    "/api/v1/graph/",
)


class _ProcessLogPump(threading.Thread):
    def __init__(self, prefix: str, pipe: io.TextIOBase | None):
        super().__init__(daemon=True)
        self.prefix = prefix
        self.pipe = pipe

    def run(self):
        if self.pipe is None:
            return
        for line in self.pipe:
            text = line.rstrip()
            if text:
                print(f"[{self.prefix}] {text}")


class _CustomerGatewayHandler(SimpleHTTPRequestHandler):
    api_base_url = ""
    static_root = ROOT / "legacy"

    def translate_path(self, path: str) -> str:
        parsed = urllib.parse.urlparse(path)
        clean = parsed.path.lstrip("/")
        target = self.static_root / clean
        if parsed.path == "/":
            target = self.static_root / "index.html"
        return str(target)

    def _proxy(self):
        target = f"{self.api_base_url}{self.path}"
        method = self.command.upper()
        body = None
        if method in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length) if length > 0 else None
        headers = {}
        for key in ("Content-Type", "Accept", "x-api-key"):
            value = self.headers.get(key)
            if value:
                headers[key] = value
        req = urllib.request.Request(url=target, method=method, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                payload = response.read()
                self.send_response(response.status)
                for hk, hv in response.getheaders():
                    if hk.lower() in {"content-length", "connection", "transfer-encoding"}:
                        continue
                    self.send_header(hk, hv)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as exc:
            payload = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", exc.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except Exception as exc:  # noqa: BLE001
            text = str(exc).encode("utf-8")
            self.send_response(HTTPStatus.BAD_GATEWAY)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(text)))
            self.end_headers()
            self.wfile.write(text)

    def _is_blocked(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in CUSTOMER_BLOCKED_PREFIXES)

    def _is_allowed_api(self, path: str) -> bool:
        if path == "/health":
            return True
        return any(path.startswith(prefix) for prefix in CUSTOMER_ALLOWED_API_PREFIXES)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/favicon.ico":
            icon = (
                "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
                "<rect width='32' height='32' rx='6' fill='#1a237e'/>"
                "<text x='16' y='21' text-anchor='middle' font-size='16' fill='white'>W</text>"
                "</svg>"
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(icon)))
            self.end_headers()
            self.wfile.write(icon)
            return
        if self._is_blocked(path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if path.startswith("/api/") or path == "/health":
            if not self._is_allowed_api(path):
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if self._is_blocked(path):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if path.startswith("/api/"):
            if not self._is_allowed_api(path):
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            return self._proxy()
        self.send_error(HTTPStatus.NOT_FOUND, "POST route not found")

    def do_OPTIONS(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/api/") and self._is_allowed_api(path):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type,x-api-key,Accept")
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any):  # noqa: A003
        print(f"[CUSTOMER_GATEWAY] {format % args}")


class RemoteInterfaceSuite:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.api_process: subprocess.Popen[str] | None = None
        self.ngrok_process: subprocess.Popen[str] | None = None
        self.gateway_server: ThreadingHTTPServer | None = None
        self.gateway_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.api_port = args.api_port
        self.ui_port = args.ui_port
        self.public_url: str | None = None

    @property
    def api_base_url(self) -> str:
        return f"http://{self.args.api_host}:{self.api_port}"

    @property
    def customer_url(self) -> str:
        return f"http://127.0.0.1:{self.ui_port}/"

    @property
    def developer_url(self) -> str:
        return f"http://127.0.0.1:{self.ui_port}/debug/calculation?debug=1"

    def run(self) -> int:
        self._register_signal_handlers()
        atexit.register(self.shutdown)
        self._ensure_api()
        self._start_customer_gateway()
        self._verify_customer_surface()
        if not self.args.no_tunnel:
            self._start_ngrok_if_available()
        self._print_status()
        if self.args.smoke_seconds > 0:
            time.sleep(self.args.smoke_seconds)
            return 0
        self._wait_forever()
        return 0

    def _ensure_api(self):
        ok, _ = health_check(self.api_base_url)
        if ok:
            print(f"[API] Reusing existing server at {self.api_base_url}")
            return
        if not _port_unused(self.args.api_host, self.api_port):
            new_port = find_open_port(self.args.api_host, self.api_port + 1)
            print(f"[API] Preferred port {self.api_port} busy; using {new_port}")
            self.api_port = new_port
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        if self.args.api_debug:
            env["PPIE_DEBUG"] = "true"
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.api.main:app",
            "--host",
            self.args.api_host,
            "--port",
            str(self.api_port),
        ]
        self.api_process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _ProcessLogPump("API", self.api_process.stdout).start()
        _ProcessLogPump("API_ERR", self.api_process.stderr).start()
        ok, detail = wait_for_health(self.api_base_url, timeout_seconds=60.0)
        if not ok:
            raise RuntimeError(f"API failed health check: {detail}")

    def _start_customer_gateway(self):
        if not _port_unused("127.0.0.1", self.ui_port):
            self.ui_port = find_open_port("127.0.0.1", self.ui_port + 1)
            print(f"[CUSTOMER_GATEWAY] Preferred UI port busy; using {self.ui_port}")
        handler_cls = type(
            "CustomerGatewayHandler",
            (_CustomerGatewayHandler,),
            {"api_base_url": self.api_base_url, "static_root": ROOT / "legacy"},
        )
        self.gateway_server = ThreadingHTTPServer(("127.0.0.1", self.ui_port), handler_cls)
        self.gateway_thread = threading.Thread(
            target=self.gateway_server.serve_forever,
            daemon=True,
            name="customer-gateway",
        )
        self.gateway_thread.start()

    def _verify_customer_surface(self):
        self._wait_url(self.customer_url)
        self._wait_url(f"http://127.0.0.1:{self.ui_port}/health")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.ui_port}/api/v1/store?weight_kg=30",
            headers={"Accept": "application/json", "x-api-key": self.args.api_key},
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                raise RuntimeError("Customer API proxy check failed")

    def _wait_url(self, url: str, timeout_seconds: float = 20.0):
        deadline = time.time() + timeout_seconds
        last_error = "unavailable"
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(url, timeout=3) as response:
                    if response.status < 500:
                        return
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                time.sleep(0.3)
        raise RuntimeError(f"Failed to load {url}: {last_error}")

    def _start_ngrok_if_available(self):
        ngrok_bin = shutil.which("ngrok")
        if not ngrok_bin:
            print("[NGROK] Not installed. Skipping tunnel startup.")
            return
        cmd = [ngrok_bin, "http", str(self.ui_port), "--log", "stdout"]
        self.ngrok_process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _ProcessLogPump("NGROK", self.ngrok_process.stdout).start()
        _ProcessLogPump("NGROK_ERR", self.ngrok_process.stderr).start()
        self.public_url = _wait_for_ngrok_url(timeout_seconds=30.0)

    def _print_status(self):
        demo_key, demo_profile = default_demo_profile()
        print("")
        print("============================================================")
        print("WAGTOPIA REMOTE TEST URL")
        print("============================================================")
        if self.public_url:
            print(f"Customer:\n{self.public_url}/")
        else:
            print("Customer:\n<ngrok unavailable>")
        print("")
        print(f"Local:\n{self.customer_url}")
        print("")
        print(f"Developer:\n{self.developer_url}")
        print("")
        print(f"API:\nLOCAL ONLY - {self.api_base_url}")
        print("")
        print(f"Demo profile:\n{demo_key} ({demo_profile.name})")
        print("============================================================")
        print("")

    def _wait_forever(self):
        while not self.stop_event.is_set():
            if self.api_process is not None and self.api_process.poll() is not None:
                raise RuntimeError("API process terminated unexpectedly.")
            if self.ngrok_process is not None and self.ngrok_process.poll() is not None:
                print("[NGROK] Tunnel process exited.")
                self.ngrok_process = None
            time.sleep(0.5)

    def _register_signal_handlers(self):
        def _handler(signum, _frame):
            print(f"\n[REMOTE_SUITE] Received signal {signum}; shutting down.")
            self.stop_event.set()
            self.shutdown()
            raise SystemExit(0)

        signal.signal(signal.SIGINT, _handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, _handler)

    def shutdown(self):
        if self.gateway_server is not None:
            try:
                self.gateway_server.shutdown()
                self.gateway_server.server_close()
            except Exception:  # noqa: BLE001
                pass
            self.gateway_server = None
        if self.ngrok_process is not None and self.ngrok_process.poll() is None:
            self.ngrok_process.terminate()
            try:
                self.ngrok_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ngrok_process.kill()
            self.ngrok_process = None
        if self.api_process is not None and self.api_process.poll() is None:
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
            self.api_process = None


def _port_unused(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def _wait_for_ngrok_url(timeout_seconds: float) -> str | None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            for tunnel in payload.get("tunnels") or []:
                url = str(tunnel.get("public_url") or "")
                if url.startswith("https://"):
                    return url.rstrip("/")
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.5)
    return None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Wagtopia customer-only remote testing suite.")
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--ui-port", type=int, default=8080)
    parser.add_argument("--api-key", default="wagtopia-demo-key")
    parser.add_argument("--api-debug", dest="api_debug", action="store_true", default=True)
    parser.add_argument("--no-api-debug", dest="api_debug", action="store_false")
    parser.add_argument("--no-tunnel", action="store_true", help="Skip ngrok startup.")
    parser.add_argument(
        "--smoke-seconds",
        type=int,
        default=0,
        help="Auto-shutdown after N seconds for smoke checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    suite = RemoteInterfaceSuite(args)
    try:
        return suite.run()
    except Exception as exc:  # noqa: BLE001
        print(f"[REMOTE_SUITE] Startup failed: {exc}")
        suite.shutdown()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
