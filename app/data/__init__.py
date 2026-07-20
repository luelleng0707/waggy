"""PPIE data platform — filesystem is the canonical database."""

from __future__ import annotations

from app.data.repository import DataPlatform, DataRepository
from app.data.runtime import (
    bootstrap,
    get_platform,
    get_repository,
    reload_platform,
    platform_meta,
)

__all__ = [
    "DataPlatform",
    "DataRepository",
    "bootstrap",
    "get_platform",
    "get_repository",
    "reload_platform",
    "platform_meta",
]

# Phase 2 warehouse adapters are importable via app.data.warehouse
