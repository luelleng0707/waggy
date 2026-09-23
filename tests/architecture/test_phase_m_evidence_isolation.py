"""Phase M isolation: longitudinal report stays off Ω12, Core, and products."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_FILES = [
    ROOT / "app" / "contracts" / "agent" / "evidence_report.py",
    ROOT / "app" / "state" / "evidence_report.py",
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
FORBIDDEN_FROM_REPORT = (
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
    "app.api.main",
    "fastapi",
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


def test_phase_m_does_not_import_core_or_omega12():
    for path in REPORT_FILES:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            for forbidden in FORBIDDEN_FROM_REPORT:
                assert not (mod == forbidden or mod.startswith(forbidden + ".")), (
                    f"{path.name} imports {mod}"
                )
        assert "resolve_breed(" not in text
        assert "FormulaGraph" not in text
        assert "PPIEWellnessAgent" not in text
        assert "CREATE TABLE" not in text
        assert "confidence =" not in text
        assert "evidence_score" not in text
        assert "INSERT INTO" not in text


def test_core_does_not_import_phase_m_report_machinery():
    for path in CORE_TOUCHPOINTS:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            assert not (mod == "app.state.evidence_report" or mod.startswith("app.state.evidence_report.")), (
                f"{path.name} imports Phase M persist/read ({mod})"
            )
            assert not (
                mod == "app.contracts.agent.evidence_report"
                or mod.startswith("app.contracts.agent.evidence_report.")
            ), f"{path.name} imports Phase M contract ({mod})"
        assert "build_evidence_report" not in text
        assert "EvidenceReport" not in text
        assert "EvidenceTimelinePoint" not in text


def test_phase_m_modules_do_not_register_http_routes():
    """HTTP exposure belongs to Phase N. Phase M stays a read function."""
    for path in REPORT_FILES:
        text = path.read_text(encoding="utf-8")
        assert "/evidence-report" not in text
        assert "APIRouter" not in text
        assert "@app.get" not in text
