"""Canonical local developer launcher for Waggy API/debug UI."""

from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PREFERRED_PORT = 8000


def _port_available(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


def _find_open_port(host: str, preferred: int, *, max_port: int = 9000) -> int:
    for port in range(preferred, max_port + 1):
        if _port_available(host, port):
            return port
    raise RuntimeError(f"No open port found in range {preferred}-{max_port}")


def _http_json(url: str, timeout: float = 2.0) -> tuple[int, dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return response.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            payload = {"detail": raw[:300]}
        return exc.code, payload
    except Exception as exc:  # noqa: BLE001
        return 0, {"detail": str(exc)}


def _http_text(url: str, timeout: float = 2.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"Accept": "text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        return 0, str(exc)


def _probe_api(host: str, port: int) -> str:
    """Classify a listener: current | stale | other | down."""
    status, health = _http_json(f"http://{host}:{port}/health")
    if status == 0:
        return "down"
    catalog_status, _catalog = _http_json(f"http://{host}:{port}/api/v1/presentation/catalog?weight_kg=30")
    if catalog_status == 404:
        return "stale"
    page_status, page = _http_text(f"http://{host}:{port}/")
    if page_status != 200 or "workbench.js" not in page:
        return "stale"
    if status == 200 and catalog_status == 200 and "demo_catalog" in health:
        return "current"
    return "other"


def _print_urls(host: str, port: int, *, demo_on: bool, reused: bool, stale_note: str = "") -> None:
    print("WAGGY DEV SERVER", flush=True)
    print("----------------", flush=True)
    if stale_note:
        print(stale_note, flush=True)
        print("", flush=True)
    if reused:
        print(f"Reusing current API on {host}:{port}", flush=True)
        print("", flush=True)
    print("UNIFIED DEMO:", flush=True)
    print(f"http://{host}:{port}/", flush=True)
    print("", flush=True)
    print("CUSTOMER:", flush=True)
    print(f"http://{host}:{port}/", flush=True)
    print("  (same workbench — use the role selector)", flush=True)
    print("", flush=True)
    print("CLASSIC CUSTOMER:", flush=True)
    print(f"http://{host}:{port}/classic", flush=True)
    print("", flush=True)
    print("BUSINESS:", flush=True)
    print(f"http://{host}:{port}/business", flush=True)
    print("  (legacy page; also a role on the unified demo)", flush=True)
    print("", flush=True)
    print("DEVELOPER:", flush=True)
    print(f"http://{host}:{port}/developer", flush=True)
    print("  (legacy page; also a role on the unified demo)", flush=True)
    print("", flush=True)
    print("API:", flush=True)
    print(f"http://{host}:{port}", flush=True)
    print("", flush=True)
    print("HEALTH:", flush=True)
    print(f"http://{host}:{port}/health", flush=True)
    print("", flush=True)
    print(f"DEMO CATALOG: {'ON (WAGTOPIA_DEMO_MODE=true)' if demo_on else 'OFF'}", flush=True)
    print("Open the UNIFIED DEMO URL above. Role switcher is on that page. Do not assume port 8000.", flush=True)
    print("Server running until stopped (Ctrl+C)...", flush=True)
    print("", flush=True)


def main() -> int:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("WAGTOPIA_DEMO_MODE", "true")
    env.setdefault("PPIE_DEBUG", "true")
    demo_on = str(env.get("WAGTOPIA_DEMO_MODE", "")).strip().lower() in {"1", "true", "yes", "on"}

    port = PREFERRED_PORT
    reused = False
    stale_note = ""
    if not _port_available(HOST, PREFERRED_PORT):
        kind = _probe_api(HOST, PREFERRED_PORT)
        health_status, health = _http_json(f"http://{HOST}:{PREFERRED_PORT}/health")
        demo_live = bool(health.get("demo_catalog")) if health_status == 200 else False
        if kind == "current" and (not demo_on or demo_live):
            reused = True
            _print_urls(HOST, port, demo_on=demo_live, reused=True)
            print("Existing process is current. This launcher will stay attached until Ctrl+C.", flush=True)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                return 0
        stale_note = (
            f"NOTE: http://{HOST}:{PREFERRED_PORT} is a {kind} API "
            f"(health={health_status}, demo_catalog={health.get('demo_catalog', 'missing')}). "
            "Starting the current interview API on a free port. Use the URLs below."
        )
        port = _find_open_port(HOST, PREFERRED_PORT + 1)

    env["WAGTOPIA_BIND_PORT"] = str(port)
    env["WAGTOPIA_BIND_HOST"] = HOST
    _print_urls(HOST, port, demo_on=demo_on, reused=reused, stale_note=stale_note)

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        HOST,
        "--port",
        str(port),
    ]
    proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())
