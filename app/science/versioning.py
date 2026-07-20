"""Versioned science stack — algorithm + warehouse + evidence + papers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from app.agent.version import ALGORITHM_VERSION


@dataclass
class VersionedScience:
    algorithm: str
    warehouse: str
    evidence: str
    papers: str
    formula_graph: str = "3.0.0"
    knowledge_graph: str = "4.0.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def current_science_versions(warehouse_root: str | Path | None = None) -> VersionedScience:
    today = date.today()
    wh_ver = "1.0.0"
    root = Path(warehouse_root) if warehouse_root else Path("warehouse")
    manifest = root / "manifest.yaml"
    if manifest.exists():
        text = manifest.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if line.strip().startswith("version:"):
                wh_ver = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
    return VersionedScience(
        algorithm=ALGORITHM_VERSION,
        warehouse=wh_ver,
        evidence=f"{today.year}.{today.month:02d}",
        papers=today.isoformat(),
    )
