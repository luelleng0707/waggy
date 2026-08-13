"""Snapshot and publish helpers for versioned warehouse releases."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE = ROOT / "warehouse"


def release_id(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.strftime("%Y.%m.%d")


def default_release_metadata(
    *,
    version: str,
    author: str = "phase5-pipeline",
    reviewers: list[str] | None = None,
    notes: str = "",
    validation_status: str = "pending",
) -> dict[str, Any]:
    return {
        "version": version,
        "release_date": datetime.now(timezone.utc).date().isoformat(),
        "author": author,
        "reviewers": reviewers or [],
        "papers_added": [],
        "papers_removed": [],
        "conditions_changed": [],
        "ingredients_changed": [],
        "products_changed": [],
        "validation_status": validation_status,
        "notes": notes,
        "workflow": ["draft", "validation", "scientific_review", "approved", "published", "production"],
        "clinical_formulas_changed": False,
        "recommendation_logic_changed": False,
    }


def snapshot_warehouse(version: str | None = None, stage: str = "releases") -> Path:
    """Copy key warehouse artifacts into warehouse/{stage}/{version}/."""
    version = version or release_id()
    dest = WAREHOUSE / stage / version
    dest.mkdir(parents=True, exist_ok=True)

    for name in ("science", "reference", "runtime", "graph", "generated"):
        src = WAREHOUSE / name
        if src.exists():
            target = dest / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    meta = default_release_metadata(version=version, notes=f"Snapshot into {stage}/{version}")
    (dest / "release.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dest


def publish_to_current(version: str) -> Path:
    """Update warehouse/current release pointer (live tables stay in reference/science/runtime)."""
    current = WAREHOUSE / "current"
    current.mkdir(parents=True, exist_ok=True)
    pointer = {
        "active_version": version,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "note": "Live engine reads warehouse/{reference,science,runtime} via Repository.",
    }
    release_dir = WAREHOUSE / "releases" / version
    if release_dir.exists():
        pointer["release_path"] = str(release_dir.relative_to(ROOT)).replace("\\", "/")
    (current / "release.json").write_text(json.dumps(pointer, indent=2), encoding="utf-8")
    return current


def promote(src_stage: str, dest_stage: str, version: str) -> Path:
    src = WAREHOUSE / src_stage / version
    if not src.exists():
        # allow promoting from releases/
        src = WAREHOUSE / "releases" / version if src_stage == "releases" else src
    if not src.exists():
        raise FileNotFoundError(src)
    dest = WAREHOUSE / dest_stage / version
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest
