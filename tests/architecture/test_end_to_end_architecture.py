from __future__ import annotations

import ast
import csv
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "docs" / "WAGGY_SYSTEM.md"


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_authoritative_spec_and_readme_exist():
    assert SPEC.is_file()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/WAGGY_SYSTEM.md" in readme
    spec = SPEC.read_text(encoding="utf-8")
    assert "PACKAGE_OPTIMIZER_V2_1" in spec
    assert "PPIEWellnessAgent" in spec
    assert "app.api.main" in spec


def test_pipeline_stages_and_production_runtime_path_documented():
    e2e = SPEC.read_text(encoding="utf-8").lower()
    for stage in (
        "profile normalization",
        "biological resolution",
        "evidence collection",
        "mathematical assessment",
        "optimization",
        "presentation projection",
    ):
        assert stage in e2e

    boundary = SPEC.read_text(encoding="utf-8")
    assert "POST /api/v1/analyze" in boundary
    assert "PPIEWellnessAgent" in boundary
    assert "app.api.main" in boundary


def test_presentation_routes_and_api_contract_documented():
    src = (ROOT / "app/api/main.py").read_text(encoding="utf-8")
    for route in ("/", "/business", "/developer", "/health", "/api/v1/analyze", "/api/v1/presentation/three-surfaces"):
        assert route in src

    contract = SPEC.read_text(encoding="utf-8")
    for endpoint in (
        "GET /",
        "GET /business",
        "GET /developer",
        "GET /health",
        "POST /api/v1/analyze",
        "POST /api/v1/presentation/workbench",
        "POST /api/v1/presentation/three-surfaces",
        "POST /api/v1/ai/explain",
        "POST /api/v1/dogs",
    ):
        assert endpoint in contract


def test_formula_and_trace_contracts_documented_in_spec():
    text = SPEC.read_text(encoding="utf-8")
    assert "FormulaGraph" in text
    assert "PACKAGE_OPTIMIZER_V2_1" in text
    assert "canonical" in text.lower()


def test_known_blockers_remain_explicitly_documented():
    text = SPEC.read_text(encoding="utf-8")
    assert "ERROR_COUNT: 8" in text
    for token in ("COND_HIP_DYSPLASIA", "COND_ATOPIC_DERMATITIS", "COND_OBESITY", "ING_ZINC"):
        assert token in text


def test_canonical_ownership_and_data_contract_files_have_rows():
    with (ROOT / "docs/architecture/CANONICAL_LAYER_OWNERSHIP.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) >= 15
    assert {"concept", "canonical_owner", "production_status"}.issubset(rows[0].keys())

    with (ROOT / "docs/architecture/DATA_CONTRACT_GRAPH.csv").open("r", encoding="utf-8", newline="") as handle:
        edges = list(csv.DictReader(handle))
    assert len(edges) >= 12
    assert {"source_type", "destination_type", "producer", "consumer", "status"}.issubset(edges[0].keys())


def test_dependency_direction_presentation_boundary():
    for py in (ROOT / "app" / "presentation").rglob("*.py"):
        for mod in _imports(py):
            assert not mod.startswith("repository.warehouse"), f"{py} imports {mod}"
            assert not mod.startswith("repository.mathematics"), f"{py} imports {mod}"
            assert not mod.startswith("repository.optimization"), f"{py} imports {mod}"


def test_protected_scientific_paths_not_modified_in_this_phase():
    git = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if git.returncode != 0:
        return
    protected = (
        "repository/mathematics/",
        "repository/formulas/",
        "repository/optimization/",
    )
    # warehouse/ intern recovery is allowed (biology, prevention, commercial,
    # reference, recovery_original). Do not treat fact-library recovery as a
    # formula-layer edit.
    for line in git.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().replace("\\", "/")
        assert not path.startswith(protected), f"protected path modified: {path}"
