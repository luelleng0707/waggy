"""Watch data/ for CSV/manifest changes and hot-reload the repository."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

_observer = None
_debounce_timer: threading.Timer | None = None
_DEBOUNCE_SEC = 0.4


def start_data_watcher(
    data_root: str | Path,
    on_change: Callable[[], None] | None = None,
) -> None:
    """Start a background watchdog observer (no-op if watchdog unavailable)."""
    global _observer
    if _observer is not None:
        return

    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        logger.warning("watchdog not installed — CSV hot reload disabled")
        return

    root = Path(data_root).resolve()

    class _Handler(FileSystemEventHandler):
        def on_any_event(self, event):  # noqa: N802
            if event.is_directory:
                return
            path = Path(str(event.src_path))
            if path.suffix.lower() not in {".csv", ".yaml", ".yml"}:
                return
            if path.name.startswith("."):
                return
            _schedule(on_change)

    observer = Observer()
    observer.schedule(_Handler(), str(root), recursive=True)
    observer.daemon = True
    observer.start()
    _observer = observer
    logger.info("Watching data directory for changes: %s", root)


def _schedule(on_change: Callable[[], None] | None) -> None:
    global _debounce_timer
    if _debounce_timer is not None:
        _debounce_timer.cancel()

    def _fire() -> None:
        logger.info("Data file change detected — reloading platform")
        try:
            from app.data.runtime import reload_platform

            reload_platform(strict=True)
            if on_change:
                on_change()
        except Exception:  # noqa: BLE001
            logger.exception("Hot reload failed — previous dataset retained if swap aborted")

    _debounce_timer = threading.Timer(_DEBOUNCE_SEC, _fire)
    _debounce_timer.daemon = True
    _debounce_timer.start()


def stop_data_watcher() -> None:
    global _observer, _debounce_timer
    if _debounce_timer is not None:
        _debounce_timer.cancel()
        _debounce_timer = None
    if _observer is not None:
        _observer.stop()
        _observer.join(timeout=2)
        _observer = None
