"""Ω12 must not import or alter the scientific engine / optimizer."""

from __future__ import annotations

import ast
from pathlib import Path

from app.agent.version import ALGORITHM_VERSION
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION
from app.normalization.version import MAPPING_CONFIG_VERSION

ROOT = Path(__file__).resolve().parents[2]
NORMALIZATION_ROOT = ROOT / "app" / "normalization"
ENGINE_TOUCHPOINTS = [
    ROOT / "app" / "agent" / "package_search.py",
    ROOT / "app" / "agent" / "package_optimizer.py",
    ROOT / "app" / "agent" / "response_assembler.py",
    ROOT / "app" / "agent" / "formula_graph.py",
    ROOT / "app" / "agent" / "nodes" / "breed_node.py",
    ROOT / "app" / "agent" / "nodes" / "biology_node.py",
    ROOT / "app" / "agent" / "nodes" / "risk_node.py",
    ROOT / "app" / "agent" / "nodes" / "epidemiology_node.py",
    ROOT / "app" / "formulas" / "stages" / "health_risk.py",
    ROOT / "app" / "formulas" / "stages" / "biological.py",
    ROOT / "app" / "formulas" / "stages" / "epidemiology.py",
    ROOT / "app" / "data" / "scientific_care.py",
    ROOT / "app" / "data" / "warehouse_biology.py",
]

FORBIDDEN_IMPORTS = {
    "app.agent.engine",
    "app.agent.package_optimizer",
    "app.agent.package_search",
    "app.data.scientific_care",
    "app.data.scientific_requirements",
    "app.formulas",
    "app.presentation.adapter",
    "google",
    "openai",
    "anthropic",
}


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_normalization_does_not_import_reasoning_or_llm():
    for py in NORMALIZATION_ROOT.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "PPIEWellnessAgent" not in text
        assert "Gemini" not in text
        assert "openai" not in text.lower()
        for mod in _imports(py):
            for forbidden in FORBIDDEN_IMPORTS:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{py} imports {mod}"
                )


def test_engine_and_optimizer_do_not_import_omega12():
    for path in ENGINE_TOUCHPOINTS:
        mods = _imports(path)
        for mod in mods:
            assert not (mod == "app.normalization" or mod.startswith("app.normalization.")), (
                f"{path.name} imports Ω12 ({mod})"
            )


def test_algorithm_and_schema_versions_unchanged():
    assert ALGORITHM_VERSION == "2.1.0"
    assert AGENT_CONTRACT_SCHEMA_VERSION == "1.0.0"
    assert MAPPING_CONFIG_VERSION == "1.0.0"
    assert MAPPING_CONFIG_VERSION != ALGORITHM_VERSION
