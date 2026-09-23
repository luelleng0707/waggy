"""Ω17.4 tools must not import the engine, warehouse, or SQL/python execution."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = ROOT / "app" / "tools"

FORBIDDEN_IMPORTS = {
    "app.agent.engine",
    "app.agent.package_search",
    "app.agent.package_optimizer",
    "app.data.scientific_care",
    "app.data.repository",
    "app.api",
    "app.api.main",
    "sqlite3",
    "pandas",
}

FORBIDDEN_SOURCE = (
    "generate_reproducible_report",
    "PPIEWellnessAgent",
    "DataRepository",
    "eval(",
    "exec(",
    "__import__",
)


def _py_files() -> list[Path]:
    return [path for path in TOOLS_ROOT.rglob("*.py") if "__pycache__" not in path.parts]


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_tools_package_does_not_import_engine_or_warehouse():
    for path in _py_files():
        for mod in _imports(path):
            for forbidden in FORBIDDEN_IMPORTS:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{path} imports {mod}"
                )


def test_tools_package_does_not_embed_engine_or_eval():
    for path in _py_files():
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_SOURCE:
            assert token not in text, f"{path} contains {token}"


def test_omega11_future_registry_is_untouched():
    from app.contracts.agent.registry import FUTURE_TOOL_NAMES, FUTURE_TOOL_REGISTRY

    assert FUTURE_TOOL_NAMES == (
        "analyze_health",
        "calculate_nutrition",
        "optimize_bundles",
        "generate_report",
    )
    assert all(not hasattr(entry, "execute") for entry in FUTURE_TOOL_REGISTRY)
