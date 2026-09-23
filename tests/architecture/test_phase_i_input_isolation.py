"""Phase I isolation: Core stays off Ω12 and off workbench input-state machinery."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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
]
ADAPTER = ROOT / "app" / "api" / "payload_adapter.py"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_core_does_not_import_omega12_or_workbench_breed_input():
    for path in CORE_TOUCHPOINTS:
        mods = _imports(path)
        text = path.read_text(encoding="utf-8")
        for mod in mods:
            assert not (mod == "app.normalization" or mod.startswith("app.normalization.")), (
                f"{path.name} imports Ω12 ({mod})"
            )
            assert not (mod == "app.api.payload_adapter" or mod.startswith("app.api.")), (
                f"{path.name} imports customer-input machinery ({mod})"
            )
            assert not (mod == "app.contracts.agent.input" or mod.startswith("app.contracts.agent.input")), (
                f"{path.name} imports CanonicalDogInput ({mod})"
            )
        assert "workbench_breed_field" not in text
        assert "breed_input_state" not in text


def test_workbench_adapter_does_not_call_omega12():
    mods = _imports(ADAPTER)
    text = ADAPTER.read_text(encoding="utf-8")
    for mod in mods:
        assert not (mod == "app.normalization" or mod.startswith("app.normalization."))
    assert "resolve_breed(" not in text
    assert "workbench_breed_field" in text
