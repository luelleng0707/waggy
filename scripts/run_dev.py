"""Canonical local developer launcher for Waggy API/debug UI."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HOST = "127.0.0.1"
PORT = 8000


def _port_available(host: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


def main() -> int:
    if not _port_available(HOST, PORT):
        print("WAGGY DEV SERVER", flush=True)
        print("----------------", flush=True)
        print(f"ERROR: {HOST}:{PORT} is already in use.", flush=True)
        print("Stop the existing process or choose a different port.", flush=True)
        return 1

    print("WAGGY DEV SERVER", flush=True)
    print("----------------", flush=True)
    print("API:", flush=True)
    print(f"http://{HOST}:{PORT}", flush=True)
    print("", flush=True)
    print("Health:", flush=True)
    print(f"http://{HOST}:{PORT}/health", flush=True)
    print("", flush=True)
    print("Developer debugger:", flush=True)
    print(f"http://{HOST}:{PORT}/developer", flush=True)
    print("", flush=True)
    print("OpenAPI:", flush=True)
    print(f"http://{HOST}:{PORT}/openapi.json", flush=True)
    print("", flush=True)
    print("Server running...", flush=True)
    print("", flush=True)

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]
    proc = subprocess.Popen(cmd, cwd=str(ROOT), env=env)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        return proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())
