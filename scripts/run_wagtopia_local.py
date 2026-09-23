"""One-click local multi-interface launcher for Wagtopia (Windows-safe)."""

from __future__ import annotations

import argparse
import atexit
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import os
from pathlib import Path
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
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = ROOT / "waggy-frontend"
LEGACY_ROOT = ROOT / "legacy"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ui.cstc.suite_utils import (  # noqa: E402
    default_demo_profile,
    find_open_port,
    health_check,
    wait_for_health,
)


def resolve_workbench_static_path(
    pathname: str,
    *,
    frontend_root: Path | None = None,
    legacy_root: Path | None = None,
) -> Path:
    """Map a UI request onto waggy-frontend, with legacy debug/archive fallback."""
    frontend = (frontend_root or FRONTEND_ROOT).resolve()
    legacy = (legacy_root or LEGACY_ROOT).resolve()
    path = urllib.parse.urlparse(pathname).path or "/"
    if path in {"/", "/demo", "/classic", "/business", "/developer", "/index.html"}:
        return frontend / "index.html"
    aliases = {
        "/workbench.js": frontend / "src" / "workbench.js",
        "/workbench.css": frontend / "src" / "styles" / "workbench.css",
        "/theme.css": frontend / "src" / "styles" / "theme.css",
    }
    if path in aliases:
        return aliases[path]
    if path.startswith("/src/"):
        target = (frontend / path[1:]).resolve()
        try:
            target.relative_to(frontend)
        except ValueError:
            return frontend / "index.html"
        return target
    if path == "/debug/calculation":
        return legacy / "debug" / "calculation.html"
    rel = path.lstrip("/")
    candidate = frontend / rel
    if candidate.is_file():
        return candidate
    return legacy / rel


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


class _LegacyGatewayHandler(SimpleHTTPRequestHandler):
    api_base_url = ""
    static_root = LEGACY_ROOT
    frontend_root = FRONTEND_ROOT

    def translate_path(self, path: str) -> str:
        return str(
            resolve_workbench_static_path(
                path,
                frontend_root=self.frontend_root,
                legacy_root=self.static_root,
            )
        )

    def _proxy(self):
        target = f"{self.api_base_url}{self.path}"
        method = self.command.upper()
        body = None
        if method in {"POST", "PUT", "PATCH"}:
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length) if length > 0 else None
        headers = {}
        for key in ("Content-Type", "Accept", "x-api-key", "x-wagtopia-access-key", "Cookie"):
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

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/favicon.ico":
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
        if self.path.startswith("/api/") or self.path.startswith("/health"):
            return self._proxy()
        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self._proxy()
        self.send_error(HTTPStatus.NOT_FOUND, "POST route not found")

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type,x-api-key,x-wagtopia-access-key,Accept")
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: Any):
        print(f"[LEGACY_UI] {format % args}")


class LocalInterfaceSuite:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.api_process: subprocess.Popen[str] | None = None
        self.desktop_process: subprocess.Popen[str] | None = None
        self.gateway_server: ThreadingHTTPServer | None = None
        self.gateway_thread: threading.Thread | None = None
        self.api_reused = False
        self.stop_event = threading.Event()
        self.processes_started: list[str] = []
        self.api_port = args.api_port
        self.ui_port = args.ui_port

    @property
    def api_base_url(self) -> str:
        return f"http://{self.args.api_host}:{self.api_port}"

    @property
    def customer_url(self) -> str:
        return f"http://127.0.0.1:{self.ui_port}/"

    @property
    def business_url(self) -> str:
        return f"http://127.0.0.1:{self.ui_port}/business"

    @property
    def developer_url(self) -> str:
        return f"http://127.0.0.1:{self.ui_port}/developer"

    def run(self) -> int:
        self._register_signal_handlers()
        atexit.register(self.shutdown)
        self._ensure_api()
        self._start_legacy_gateway()
        self._wait_gateway_pages()
        self._open_browsers()
        self._launch_desktop()
        self._print_status()

        if self.args.smoke_seconds > 0:
            time.sleep(self.args.smoke_seconds)
            return 0

        self._wait_forever()
        return 0

    def _ensure_api(self):
        ok, detail = health_check(self.api_base_url)
        if ok:
            self.api_reused = True
            print(f"[API] Reusing existing server at {self.api_base_url} (health={detail})")
            return

        if not _port_unused(self.args.api_host, self.api_port):
            new_port = find_open_port(self.args.api_host, self.api_port + 1)
            print(f"[API] Preferred port {self.api_port} busy; using {new_port}")
            self.api_port = new_port

        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        env["WAGTOPIA_DEMO_MODE"] = "true" if self.args.demo_mode else "false"
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
        print(f"[API] Starting: {' '.join(cmd)}")
        self.api_process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.processes_started.append("api")
        _ProcessLogPump("API", self.api_process.stdout).start()
        _ProcessLogPump("API_ERR", self.api_process.stderr).start()
        ok, detail = wait_for_health(self.api_base_url, timeout_seconds=60.0)
        if not ok:
            raise RuntimeError(f"API failed health check: {detail}")

    def _start_legacy_gateway(self):
        if not _port_unused("127.0.0.1", self.ui_port):
            self.ui_port = find_open_port("127.0.0.1", self.ui_port + 1)
            print(f"[LEGACY_UI] Preferred UI port busy; using {self.ui_port}")

        handler_cls = type(
            "LegacyGatewayHandler",
            (_LegacyGatewayHandler,),
            {
                "api_base_url": self.api_base_url,
                "static_root": LEGACY_ROOT,
                "frontend_root": FRONTEND_ROOT,
            },
        )
        self.gateway_server = ThreadingHTTPServer(("127.0.0.1", self.ui_port), handler_cls)
        self.gateway_thread = threading.Thread(
            target=self.gateway_server.serve_forever,
            daemon=True,
            name="legacy-gateway",
        )
        self.gateway_thread.start()
        self.processes_started.append("legacy_ui_gateway")

    def _wait_gateway_pages(self):
        self._wait_url(self.customer_url)
        self._wait_url(self.business_url)
        self._wait_url(self.developer_url)

    def _wait_url(self, url: str, timeout_seconds: float = 20.0):
        deadline = time.time() + timeout_seconds
        last_error = "unavailable"
        while time.time() < deadline:
            try:
                req = urllib.request.Request(url, headers={"Accept": "text/html"})
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status < 500:
                        return
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                time.sleep(0.3)
        raise RuntimeError(f"Failed to load {url}: {last_error}")

    def _open_browsers(self):
        if self.args.no_browser:
            return
        _safe_browser_open(self.customer_url)

    def _launch_desktop(self):
        if self.args.no_desktop:
            return
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        env["WAGTOPIA_API_BASE_URL"] = self.api_base_url
        if self.args.api_key:
            env["WAGTOPIA_API_KEY"] = self.args.api_key
        env["WAGTOPIA_DEMO_MODE"] = "true" if self.args.demo_mode else "false"
        cmd = [sys.executable, "-m", "app.ui.cstc"]
        print(f"[CSTC_DESKTOP] Starting: {' '.join(cmd)}")
        self.desktop_process = subprocess.Popen(
            cmd,
            cwd=str(ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.processes_started.append("cstc_desktop")
        _ProcessLogPump("CSTC", self.desktop_process.stdout).start()
        _ProcessLogPump("CSTC_ERR", self.desktop_process.stderr).start()
        time.sleep(1.0)
        if self.desktop_process.poll() is not None:
            raise RuntimeError("CSTC desktop process exited immediately.")

    def _print_status(self):
        _demo_key, demo_profile = default_demo_profile()
        print("")
        print("WAGTOPIA LOCAL DEMO")
        print("")
        print("CUSTOMER:")
        print(self.customer_url)
        print("")
        print("BUSINESS:")
        print(self.business_url)
        print("")
        print("DEVELOPER:")
        print(self.developer_url)
        print("")
        print("API:")
        print(f"{self.api_base_url}/docs")
        print("")
        print("HEALTH:")
        print(f"{self.api_base_url}/health")
        print("")
        print(f"DEMO CATALOG: {'ON (WAGTOPIA_DEMO_MODE=true)' if self.args.demo_mode else 'OFF'}")
        print(f"Demo profile: {demo_profile.name} (DEMO DATA)")
        print("")

    def _wait_forever(self):
        while not self.stop_event.is_set():
            if self.api_process is not None and self.api_process.poll() is not None:
                raise RuntimeError("API process terminated unexpectedly.")
            if self.desktop_process is not None and self.desktop_process.poll() is not None:
                print("[CSTC_DESKTOP] Window closed; shutting down suite.")
                self.stop_event.set()
                break
            time.sleep(0.5)

    def _register_signal_handlers(self):
        def _handler(signum, _frame):
            print(f"\n[SUITE] Received signal {signum}; shutting down.")
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

        if self.desktop_process is not None and self.desktop_process.poll() is None:
            self.desktop_process.terminate()
            try:
                self.desktop_process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.desktop_process.kill()
            self.desktop_process = None

        if self.api_process is not None and self.api_process.poll() is None:
            self.api_process.terminate()
            try:
                self.api_process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                self.api_process.kill()
            self.api_process = None


def _safe_browser_open(url: str):
    try:
        webbrowser.open(url, new=2)
    except Exception as exc:  # noqa: BLE001
        print(f"[BROWSER] Failed to open {url}: {exc}")


def _port_unused(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Wagtopia local interface suite.")
    parser.add_argument("--api-host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--ui-port", type=int, default=8080)
    parser.add_argument("--api-key", default="")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--no-desktop", action="store_true")
    parser.add_argument("--demo-mode", dest="demo_mode", action="store_true", default=True)
    parser.add_argument("--no-demo-mode", dest="demo_mode", action="store_false")
    parser.add_argument("--api-debug", dest="api_debug", action="store_true", default=True)
    parser.add_argument("--no-api-debug", dest="api_debug", action="store_false")
    parser.add_argument(
        "--smoke-seconds",
        type=int,
        default=0,
        help="Auto-shutdown after N seconds (for CI/manual smoke checks).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    suite = LocalInterfaceSuite(args)
    try:
        return suite.run()
    except Exception as exc:  # noqa: BLE001
        print(f"[SUITE] Startup failed: {exc}")
        suite.shutdown()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
