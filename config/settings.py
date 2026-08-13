"""Repository-wide settings with no hardcoded data paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    warehouse_root: Path
    docs_root: Path
    validation_report_path: Path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    repo_root = Path(__file__).resolve().parents[1]
    raw_warehouse = os.getenv("WAGGY_WAREHOUSE_ROOT", "warehouse")
    warehouse_root = Path(raw_warehouse)
    if not warehouse_root.is_absolute():
        warehouse_root = repo_root / warehouse_root
    docs_root = repo_root / "docs"
    return Settings(
        repo_root=repo_root,
        warehouse_root=warehouse_root.resolve(),
        docs_root=docs_root.resolve(),
        validation_report_path=(docs_root / "validation_report.md").resolve(),
    )
