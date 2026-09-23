"""Phase J isolation: individual observations stay off Ω12, Core, and product logic."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBSERVATION_FILES = [
    ROOT / "app" / "contracts" / "agent" / "observations.py",
    ROOT / "app" / "state" / "observations.py",
]
CORE_TOUCHPOINTS = [
    ROOT / "app" / "agent" / "formula_graph.py",
    ROOT / "app" / "agent" / "nodes" / "breed_node.py",
    ROOT / "app" / "agent" / "nodes" / "biology_node.py",
    ROOT / "app" / "agent" / "nodes" / "risk_node.py",
    ROOT / "app" / "agent" / "nodes" / "epidemiology_node.py",
    ROOT / "app" / "formulas" / "stages" / "health_risk.py",
    ROOT / "app" / "formulas" / "stages" / "biological.py",
    ROOT / "app" / "formulas" / "stages" / "epidemiology.py",
    ROOT / "app" / "data" / "scientific_care.py",
    ROOT / "app" / "agent" / "package_search.py",
    ROOT / "app" / "agent" / "package_optimizer.py",
]
FORBIDDEN_FROM_OBSERVATIONS = (
    "app.normalization",
    "app.agent.formula_graph",
    "app.agent.nodes.breed_node",
    "app.data.scientific_care",
    "app.agent.package_search",
    "app.agent.package_optimizer",
    "app.formulas",
)


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_physical_observation_layer_does_not_import_core_or_omega12():
    for path in OBSERVATION_FILES:
        mods = _imports(path)
        for mod in mods:
            for forbidden in FORBIDDEN_FROM_OBSERVATIONS:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{path.name} imports {mod}"
                )
        text = path.read_text(encoding="utf-8")
        assert "resolve_breed(" not in text
        assert "FormulaGraph" not in text
        assert "PPIEWellnessAgent" not in text


def test_core_does_not_import_owner_observation_machinery():
    for path in CORE_TOUCHPOINTS:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            assert not (mod == "app.state.observations" or mod.startswith("app.state.observations.")), (
                f"{path.name} imports owner-observation machinery ({mod})"
            )
        assert "record_physical_observation" not in text
        assert "PHYSICAL_OBSERVATION_TYPES" not in text
        assert "physical_observations_for" not in text
