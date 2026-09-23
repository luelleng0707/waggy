"""Phase C comparison must stay outside production Core execution."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPARE_PATH = ROOT / "app" / "offline" / "breed_identity_compare.py"

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
    ROOT / "app" / "data" / "warehouse_biology.py",
    ROOT / "app" / "api" / "main.py",
    ROOT / "app" / "api" / "payload_adapter.py",
    ROOT / "app" / "api" / "http_models.py",
    ROOT / "app" / "api" / "evidence.py",
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


def test_production_consumers_do_not_import_phase_c_harness():
    for path in PRODUCTION_CONSUMERS:
        assert path.is_file(), path
        for mod in _imports(path):
            assert mod != "app.offline"
            assert not mod.startswith("app.offline.")
            assert "breed_identity_compare" not in mod
        text = path.read_text(encoding="utf-8")
        assert "breed_identity_compare" not in text
        assert "app.offline" not in text


def test_phase_c_harness_does_not_import_formula_graph_or_science_consumers():
    mods = _imports(COMPARE_PATH)
    for mod in mods:
        for forbidden in FORBIDDEN_HARNESS_IMPORTS:
            assert not (mod == forbidden or mod.startswith(forbidden + ".")), (mod, forbidden)
    text = COMPARE_PATH.read_text(encoding="utf-8")
    assert "from app.agent.formula_graph" not in text
    assert "import FormulaGraph" not in text
    assert "PPIEWellnessAgent" not in text
    assert "/api/v1/analyze" not in text
    assert "/api/v1/presentation/workbench" not in text
    assert "/api/v2/wellness/evaluate" not in text
