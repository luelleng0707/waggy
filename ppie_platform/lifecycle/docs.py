"""ΩN API stability inventory + ΩQ living architecture generators."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "meta" / "architecture"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def generate_api_stability() -> Path:
    from app.api.main import app
    from app.agent.version import ALGORITHM_VERSION

    routes = []
    for r in app.routes:
        methods = sorted(getattr(r, "methods", []) or [])
        path = getattr(r, "path", None)
        if not path or not methods:
            continue
        version = "v1" if "/api/v1/" in path else ("legacy" if path.startswith("/api/") else "static")
        deprecated = "/api/recommendations" in path or path.endswith("_legacy")
        consumers = []
        if "clinical-report" in path:
            consumers = ["app.js", "StandardReportRenderer"]
        elif "ppie/assess" in path:
            consumers = ["integrations", "Validation Console"]
        elif "platform/" in path:
            consumers = ["ops", "developers"]
        elif "analyze" in path:
            consumers = ["legacy clients"]
        routes.append(
            {
                "path": path,
                "methods": methods,
                "version": version,
                "deprecated": deprecated,
                "compatibility": "stable" if version == "v1" and not deprecated else "transitional",
                "consumers": consumers,
                "algorithm_version": ALGORITHM_VERSION,
            }
        )

    ARCH.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": _now(), "routes": routes}
    lines = [
        "# API Stability",
        "",
        f"Generated: `{payload['generated_at']}`",
        f"Algorithm: `{ALGORITHM_VERSION}`",
        "",
        "| Method | Path | Version | Deprecated | Compatibility | Consumers |",
        "|---|---|---|---|---|---|",
    ]
    for r in sorted(routes, key=lambda x: x["path"]):
        lines.append(
            f"| {','.join(r['methods'])} | `{r['path']}` | {r['version']} | {r['deprecated']} | "
            f"{r['compatibility']} | {', '.join(r['consumers']) or '—'} |"
        )
    path = ARCH / "API_STABILITY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ARCH / "API_STABILITY.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    # Mirror API_REFERENCE into meta
    api_ref = ROOT / "docs" / "API_REFERENCE.md"
    if api_ref.exists():
        (ARCH / "API_REFERENCE.md").write_text(api_ref.read_text(encoding="utf-8"), encoding="utf-8")
    return path


def generate_living_architecture() -> dict[str, Path]:
    from ppie_platform import CORE_ARCHITECTURE_FROZEN, CLINICAL_PATH, __version__ as omega_ver
    from app.agent.version import ALGORITHM_VERSION
    from app.agent.formula_registry import FORMULA_REGISTRY
    from app.agent.nodes import default_nodes

    ARCH.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    arch = ARCH / "ARCHITECTURE.md"
    arch.write_text(
        "\n".join(
            [
                "# Architecture (generated)",
                "",
                f"Generated: `{_now()}`",
                f"Omega platform: `{omega_ver}`",
                f"Algorithm: `{ALGORITHM_VERSION}`",
                f"Core frozen: **{CORE_ARCHITECTURE_FROZEN}**",
                "",
                "## Clinical execution path",
                "",
                f"`{CLINICAL_PATH}`",
                "",
                "New work should extend via datasets, formula nodes, plugins, dashboards, and reports — not redesign the engine.",
                "",
                "## Layers",
                "",
                "- `data/` + `warehouse/` — science & products",
                "- `app/agent` — FormulaGraph (frozen math wrappers)",
                "- `app/science` — knowledge graph / explainability",
                "- `governance/` + `science_pipeline/` — Phase 5 release OS",
                "- `platform/` + `quality/` + `operations/` + `meta/` — Phase Ω",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["ARCHITECTURE"] = arch

    # DATA_DICTIONARY / WAREHOUSE mirrors
    dd = ROOT / "docs" / "DATA_DICTIONARY.md"
    if dd.exists():
        paths["DATA_DICTIONARY"] = ARCH / "DATA_DICTIONARY.md"
        paths["DATA_DICTIONARY"].write_text(dd.read_text(encoding="utf-8"), encoding="utf-8")

    wh = ARCH / "WAREHOUSE.md"
    wh.write_text(
        "\n".join(
            [
                "# Warehouse (generated)",
                "",
                f"Generated: `{_now()}`",
                "",
                "Live engine reads `data/`. Governance versions live under `warehouse/releases/`.",
                "See `docs/WAREHOUSE_REFERENCE.md` and `warehouse/current/release.json`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    paths["WAREHOUSE"] = wh

    # QUALITY summary placeholder filled by pipeline
    q = ARCH / "QUALITY.md"
    q.write_text(
        f"# Quality (generated)\n\nGenerated: `{_now()}`\n\nSee `quality/reports/` for failure, fuzz, synthetic, mutation artifacts.\n",
        encoding="utf-8",
    )
    paths["QUALITY"] = q

    # RELEASE_HISTORY
    rel_dir = ROOT / "governance" / "releases"
    lines = [f"# Release History\n\nGenerated: `{_now()}`\n"]
    if rel_dir.exists():
        for p in sorted(rel_dir.glob("*.json")):
            if p.name.startswith("ROLLBACK") or p.name.startswith("TAG_"):
                continue
            try:
                meta = json.loads(p.read_text(encoding="utf-8"))
                lines.append(f"- `{meta.get('version', p.stem)}` — {meta.get('validation_status')} — {meta.get('notes', '')[:80]}")
            except Exception:
                lines.append(f"- `{p.name}`")
    paths["RELEASE_HISTORY"] = ARCH / "RELEASE_HISTORY.md"
    paths["RELEASE_HISTORY"].write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Inventory
    inv = {
        "generated_at": _now(),
        "formula_count": len(FORMULA_REGISTRY),
        "node_count": len(default_nodes()),
        "formulas": list(FORMULA_REGISTRY.keys()),
        "nodes": [n.id for n in default_nodes()],
    }
    (ROOT / "meta" / "inventories").mkdir(parents=True, exist_ok=True)
    (ROOT / "meta" / "inventories" / "formulas.json").write_text(json.dumps(inv, indent=2), encoding="utf-8")

    return paths
