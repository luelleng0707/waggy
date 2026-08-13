from __future__ import annotations

import ast
from pathlib import Path


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_runtime_layers_do_not_import_frontend_layers():
    root = Path(__file__).resolve().parents[2]
    runtime_dirs = [
        root / "app" / "api",
        root / "app" / "agent",
        root / "repository" / "pipeline",
        root / "repository" / "mathematics",
        root / "repository" / "optimization",
    ]
    for directory in runtime_dirs:
        for py in directory.rglob("*.py"):
            for mod in _imports(py):
                assert not mod.startswith("app.ui"), f"{py} imports frontend module {mod}"


def test_warehouse_layer_does_not_import_math_or_optimization():
    root = Path(__file__).resolve().parents[2]
    warehouse_dir = root / "repository" / "warehouse"
    for py in warehouse_dir.rglob("*.py"):
        for mod in _imports(py):
            assert not mod.startswith("repository.mathematics"), f"{py} imports {mod}"
            assert not mod.startswith("repository.optimization"), f"{py} imports {mod}"
            assert not mod.startswith("repository.reasoning"), f"{py} imports {mod}"


def test_formula_configuration_modules_do_not_depend_on_app_code():
    root = Path(__file__).resolve().parents[2]
    formulas_dir = root / "repository" / "formulas"
    config_modules = {"loader.py", "models.py", "registry.py", "resolver.py", "validator.py"}
    for py in formulas_dir.glob("*.py"):
        if py.name not in config_modules:
            continue
        for mod in _imports(py):
            assert not mod.startswith("app."), f"{py} imports app module {mod}"
            assert not mod.startswith("repository.pipeline"), f"{py} imports {mod}"
            assert not mod.startswith("repository.mathematics"), f"{py} imports {mod}"
