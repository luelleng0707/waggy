"""Aggregated platform status payloads for ΩR self-inspection APIs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ppie_platform import CLINICAL_PATH, CORE_ARCHITECTURE_FROZEN, __version__ as OMEGA_VERSION
from app.agent.formula_registry import FORMULA_REGISTRY, list_formulas
from app.agent.nodes import default_nodes
from app.agent.version import ALGORITHM_VERSION

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any] | None:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def platform_status() -> dict[str, Any]:
    current = _read_json(ROOT / "warehouse" / "current" / "release.json") or {}
    return {
        "schema": "platform_status.v1",
        "omega_version": OMEGA_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "core_architecture_frozen": CORE_ARCHITECTURE_FROZEN,
        "clinical_path": CLINICAL_PATH,
        "active_release": current.get("active_version"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "healthy": True,
    }


def platform_runtime() -> dict[str, Any]:
    data = _read_json(ROOT / "ppie_platform" / "observability" / "reports" / "SYSTEM_RUNTIME.json")
    return {"schema": "platform_runtime.v1", "data": data, "hint": "Run: py -3 -m ppie_platform.omega --observatory"}


def platform_dependencies() -> dict[str, Any]:
    data = _read_json(ROOT / "meta" / "dependency_graph" / "DEPENDENCY_OBSERVATORY.json")
    return {"schema": "platform_dependencies.v1", "data": data}


def platform_formulas() -> dict[str, Any]:
    nodes = [{"id": n.id, "formula_id": n.formula_id, "version": n.version, "deps": list(n.dependencies)} for n in default_nodes()]
    return {
        "schema": "platform_formulas.v1",
        "formulas": list_formulas(),
        "registry": {k: {"version": v.get("version"), "tables": v.get("tables"), "consumers": v.get("consumers")} for k, v in FORMULA_REGISTRY.items()},
        "nodes": nodes,
    }


def platform_science() -> dict[str, Any]:
    data = _read_json(ROOT / "ppie_platform" / "observability" / "reports" / "SCIENCE_OBSERVATORY.json")
    return {"schema": "platform_science.v1", "data": data}


def platform_performance() -> dict[str, Any]:
    data = _read_json(ROOT / "ppie_platform" / "observability" / "reports" / "PERFORMANCE_OBSERVATORY.json")
    bench = _read_json(ROOT / "governance" / "reports" / "BENCHMARK_REPORT.json")
    return {"schema": "platform_performance.v1", "observatory": data, "benchmark": bench}


def platform_coverage() -> dict[str, Any]:
    health = _read_json(ROOT / "governance" / "reports" / "data_health.json")
    sci = _read_json(ROOT / "ppie_platform" / "observability" / "reports" / "SCIENCE_OBSERVATORY.json")
    return {"schema": "platform_coverage.v1", "data_health": health, "science": sci}


def platform_release() -> dict[str, Any]:
    current = _read_json(ROOT / "warehouse" / "current" / "release.json")
    summary = _read_json(ROOT / "governance" / "reports" / "RELEASE_SUMMARY.json")
    return {"schema": "platform_release.v1", "current": current, "last_summary": summary}


def platform_audit() -> dict[str, Any]:
    sec = _read_json(ROOT / "ppie_platform" / "security" / "SECURITY_AUDIT.json")
    val = _read_json(ROOT / "governance" / "validation" / "SCIENCE_VALIDATION_REPORT.json")
    return {"schema": "platform_audit.v1", "security": sec, "science_validation": val}
