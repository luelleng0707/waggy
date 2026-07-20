"""Developer boot helpers — banner / local-dev detection (no clinical math)."""

from __future__ import annotations

import os
import sys
import threading
import uuid
import webbrowser
from typing import Any

from app.data.engine_trace import is_engine_debug

# Stable for process lifetime; changes on uvicorn --reload worker restart.
BOOT_ID = uuid.uuid4().hex[:10]


def is_reload_process() -> bool:
    """True when uvicorn was started with --reload (best-effort)."""
    joined = " ".join(sys.argv).lower()
    return "--reload" in joined


def is_local_dev_boot() -> bool:
    """True when developer tooling should print banner / soft-enable console page."""
    if is_engine_debug():
        return True
    if is_reload_process():
        return True
    raw = str(os.getenv("PPIE_DEV_BOOT", "")).strip().lower()
    return raw in ("1", "true", "yes", "on")


def should_open_browser() -> bool:
    raw = str(os.getenv("PPIE_OPEN_BROWSER", "true")).strip().lower()
    return raw in ("1", "true", "yes", "on")


def developer_banner(*, host: str = "127.0.0.1", port: int = 8000) -> str:
    base = f"http://{host}:{port}"
    return (
        "\n"
        "=========================================\n"
        "PPIE Developer Mode Enabled\n"
        "\n"
        f"Validation Console:\n"
        f"{base}/debug/calculation?debug=1\n"
        "\n"
        f"Engine Trace:\n"
        f"{base}/api/v1/ppie/trace?debug=1\n"
        "\n"
        f"Repository Browser:\n"
        f"{base}/api/v1/ppie/debug/repository?debug=1\n"
        "\n"
        f"Boot id: {BOOT_ID}\n"
        "=========================================\n"
    )


def print_developer_banner(*, host: str = "127.0.0.1", port: int = 8000) -> None:
    if not is_local_dev_boot():
        return
    print(developer_banner(host=host, port=port), flush=True)


def maybe_open_validation_console(*, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Open Validation Console once in a background thread (local/dev only)."""
    if not is_local_dev_boot() or not should_open_browser():
        return
    if str(os.getenv("PPIE_BROWSER_OPENED", "")).strip() == "1":
        return
    os.environ["PPIE_BROWSER_OPENED"] = "1"
    url = f"http://{host}:{port}/debug/calculation?debug=1"

    def _open() -> None:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass

    threading.Timer(1.2, _open).start()


def debug_status_payload(repo: Any) -> dict[str, Any]:
    return {
        "schema": "ppie_debug_status.v1",
        "boot_id": BOOT_ID,
        "debug_env": is_engine_debug(),
        "local_dev_boot": is_local_dev_boot(),
        "reload": is_reload_process(),
        "csv_hash": getattr(repo, "csv_hash", None),
        "data_version": getattr(repo, "version", None),
        "loaded_at": getattr(repo, "loaded_at", None),
        "console_url": "/debug/calculation?debug=1",
        "trace_url": "/api/v1/ppie/trace?debug=1",
    }
