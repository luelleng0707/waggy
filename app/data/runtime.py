"""Process-wide data platform singleton + hot reload."""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable

from app.data.cache import PlatformMeta
from app.data.repository import DataPlatform, DataRepository

logger = logging.getLogger(__name__)

_lock = threading.RLock()
_platform: DataPlatform | None = None
_data_root: Path | None = None
_on_reload: list[Callable[[DataPlatform], None]] = []


def register_reload_hook(callback: Callable[[DataPlatform], None]) -> None:
    with _lock:
        _on_reload.append(callback)


def bootstrap(data_root: str | Path, *, strict: bool = True) -> DataPlatform:
    global _platform, _data_root
    root = Path(data_root)
    platform = DataPlatform(root, strict=strict)
    with _lock:
        _platform = platform
        _data_root = root
    logger.info(
        "Data platform ready version=%s hash=%s files=%s",
        platform.version,
        platform.csv_hash,
        platform.file_count,
    )
    return platform


def get_platform() -> DataPlatform:
    with _lock:
        if _platform is None:
            raise RuntimeError("Data platform not bootstrapped — call bootstrap(data_dir) first")
        return _platform


def get_repository(data_root: str | Path | None = None) -> DataRepository:
    with _lock:
        root = Path(data_root) if data_root is not None else _data_root
        if root is None:
            raise RuntimeError("Data platform not bootstrapped")
        if _platform is None:
            bootstrap(root)
        return DataRepository(root)


def reload_platform(*, strict: bool = True) -> DataPlatform:
    with _lock:
        if _data_root is None:
            raise RuntimeError("Cannot reload — platform never bootstrapped")
        root = _data_root
    platform = DataPlatform(root, strict=strict)
    with _lock:
        global _platform
        _platform = platform
        hooks = list(_on_reload)
    logger.info(
        "Data platform reloaded version=%s hash=%s files=%s",
        platform.version,
        platform.csv_hash,
        platform.file_count,
    )
    for hook in hooks:
        try:
            hook(platform)
        except Exception:  # noqa: BLE001
            logger.exception("Reload hook failed")
    return platform


def platform_meta() -> PlatformMeta:
    return get_platform().meta
