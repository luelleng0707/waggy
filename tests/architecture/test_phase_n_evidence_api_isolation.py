"""Phase N isolation: evidence-report HTTP adapter stays off Core, Ω12, and products."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_FILE = ROOT / "app" / "api" / "evidence_report.py"
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
    ROOT / "app" / "normalization" / "resolver.py",
]
FORBIDDEN = (
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
    "app.state.store",
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


def test_evidence_report_api_adapter_does_not_import_core_or_omega12():
    mods = _imports(API_FILE)
    text = API_FILE.read_text(encoding="utf-8")
    for mod in mods:
        for forbidden in FORBIDDEN:
            assert not (mod == forbidden or mod.startswith(forbidden + ".")), f"imports {mod}"
    assert "app.state.evidence_report" in mods
    assert "app.state.evidence" not in mods
    assert set(mods) <= {"__future__", "app.state.evidence_report"}
    assert "resolve_breed(" not in text
    assert "FormulaGraph" not in text
    assert "PPIEWellnessAgent" not in text
    assert "CREATE TABLE" not in text
    assert "INSERT INTO" not in text
    assert "record_event" not in text
    assert "confidence =" not in text
    assert "evidence_score" not in text


def test_route_delegates_to_phase_m_without_rebuilding_evidence():
    main = (ROOT / "app" / "api" / "main.py").read_text(encoding="utf-8")
    assert '@app.get("/api/v1/dogs/{dog_id}/evidence-report")' in main
    assert "read_evidence_report(" in main
    handler = main.split("async def get_dog_evidence_report", 1)[1].split("@app.", 1)[0]
    assert "build_evidence_report" not in handler
    assert "select_canonical_observation" not in handler
    assert "resolve_breed(" not in handler
    assert "record_event" not in handler


def test_core_does_not_import_phase_n_api_adapter():
    for path in CORE_TOUCHPOINTS:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            assert not (mod == "app.api.evidence_report" or mod.startswith("app.api.evidence_report.")), (
                f"{path.name} imports Phase N adapter ({mod})"
            )
        assert "read_evidence_report" not in text
        assert "get_dog_evidence_report" not in text
