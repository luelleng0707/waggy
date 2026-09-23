"""Phase D review must stay outside production Core execution."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OFFLINE_ROOT = ROOT / "app" / "offline"

PRODUCTION_CONSUMERS = [
    ROOT / "app" / "agent" / "formula_graph.py",
    ROOT / "app" / "agent" / "engine.py",
    ROOT / "app" / "agent" / "nodes" / "breed_node.py",
    ROOT / "app" / "agent" / "nodes" / "biology_node.py",
    ROOT / "app" / "agent" / "nodes" / "risk_node.py",
    ROOT / "app" / "agent" / "nodes" / "epidemiology_node.py",
    ROOT / "app" / "formulas" / "stages" / "health_risk.py",
    ROOT / "app" / "formulas" / "stages" / "biological.py",
    ROOT / "app" / "formulas" / "stages" / "epidemiology.py",
    ROOT / "app" / "data" / "scientific_care.py",
    ROOT / "app" / "api" / "main.py",
]

FORBIDDEN_HARNESS_IMPORTS = {
    "app.agent.formula_graph",
    "app.agent.engine",
    "app.formulas.stages.health_risk",
    "app.formulas.stages.biological",
    "app.formulas.stages.epidemiology",
    "app.data.scientific_care",
    "app.api.main",
    "fastapi",
}


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_production_does_not_import_phase_d_review():
    for path in PRODUCTION_CONSUMERS:
        text = path.read_text(encoding="utf-8")
        assert "breed_identity_review" not in text
        assert "PHASE_D" not in text
        for mod in _imports(path):
            assert mod != "app.offline"
            assert not mod.startswith("app.offline.")


def test_phase_d_review_does_not_import_formula_graph_or_api():
    review_path = OFFLINE_ROOT / "breed_identity_review.py"
    mods = _imports(review_path)
    for mod in mods:
        for forbidden in FORBIDDEN_HARNESS_IMPORTS:
            assert not (mod == forbidden or mod.startswith(forbidden + "."))
    text = review_path.read_text(encoding="utf-8")
    assert "from app.agent.formula_graph" not in text
    assert "FormulaGraph" not in text
    assert "PPIEWellnessAgent" not in text
    for py in OFFLINE_ROOT.glob("*.py"):
        source = py.read_text(encoding="utf-8")
        assert "pymongo" not in source
        assert "openai" not in source.lower()
        assert "wikipedia" not in source.lower()
