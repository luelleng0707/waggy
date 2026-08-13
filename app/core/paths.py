"""Resolve the canonical warehouse root for transitional runtime code."""

from __future__ import annotations

import os
from pathlib import Path

from config import get_settings

REPO_ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE = REPO_ROOT / "warehouse"
WAREHOUSE_CURRENT = WAREHOUSE / "current"  # historical pointer; not used for loading
_ENV_KEY = "PPIE_DATA_DIR"


def resolve_clinical_root() -> Path:
    """
    Single source of truth for clinical data loading.

    Order:
    1. PPIE_DATA_DIR if set
    2. warehouse/ when science/ is present
    """
    settings = get_settings()
    raw = os.getenv(_ENV_KEY)
    if raw:
        p = Path(raw)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p.resolve()

    if settings.warehouse_root.exists():
        return settings.warehouse_root

    raise FileNotFoundError(
        f"Clinical warehouse not found at {settings.warehouse_root}."
    )


def clinical_root_str() -> str:
    return str(resolve_clinical_root())
