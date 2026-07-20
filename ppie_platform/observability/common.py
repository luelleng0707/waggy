"""Shared helpers for Phase Ω observatories."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "meta"
PLATFORM_OUT = ROOT / "ppie_platform" / "observability" / "reports"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for p in (
        PLATFORM_OUT,
        META / "architecture",
        META / "metrics",
        META / "inventories",
        META / "dependency_graph",
        ROOT / "operations" / "snapshots",
        ROOT / "quality" / "reports",
    ):
        p.mkdir(parents=True, exist_ok=True)


def write_md_json(stem: str, markdown: str, payload: dict[str, Any], *dirs: Path) -> list[Path]:
    ensure_dirs()
    written: list[Path] = []
    targets = dirs or (PLATFORM_OUT, META / "metrics")
    for d in targets:
        d.mkdir(parents=True, exist_ok=True)
        md = d / f"{stem}.md"
        js = d / f"{stem}.json"
        md.write_text(markdown if markdown.endswith("\n") else markdown + "\n", encoding="utf-8")
        js.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        written.extend([md, js])
    return written


def default_platform() -> Any:
    from app.data.repository import DataPlatform

    return DataPlatform("data", strict=True)
