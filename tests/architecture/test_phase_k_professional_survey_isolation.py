"""Phase K isolation: professional survey contracts stay off Ω12, Core, and products."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY_FILES = [
    ROOT / "app" / "contracts" / "agent" / "survey.py",
    ROOT / "app" / "state" / "survey.py",
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
FORBIDDEN_FROM_SURVEY = (
    "app.normalization",
    "app.agent.formula_graph",
    "app.agent.nodes.breed_node",
    "app.agent.nodes.biology_node",
    "app.agent.nodes.risk_node",
    "app.agent.nodes.epidemiology_node",
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


def test_professional_survey_does_not_import_core_or_omega12():
    for path in SURVEY_FILES:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            for forbidden in FORBIDDEN_FROM_SURVEY:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{path.name} imports {mod}"
                )
        assert "resolve_breed(" not in text
        assert "PPIEWellnessAgent" not in text
        assert "CREATE TABLE" not in text
        assert "authority" not in text.lower()
        assert "recommend" not in text.lower()


def test_core_does_not_import_professional_survey_machinery():
    for path in CORE_TOUCHPOINTS:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            assert not (mod == "app.contracts.agent.survey" or mod.startswith("app.contracts.agent.survey.")), (
                f"{path.name} imports professional survey ({mod})"
            )
            assert not (mod == "app.state.survey" or mod.startswith("app.state.survey.")), (
                f"{path.name} imports professional survey persist ({mod})"
            )
        assert "ProfessionalSurveyResponse" not in text
        assert "record_professional_survey" not in text
