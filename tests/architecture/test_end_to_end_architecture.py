from __future__ import annotations

import ast
import csv
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def _imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out.extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            out.append(node.module)
    return out


def test_required_omega98_architecture_artifacts_exist():
    required = [
        "docs/architecture/END_TO_END_RUNTIME_ARCHITECTURE.md",
        "docs/architecture/DATA_CONTRACT_GRAPH.csv",
        "docs/architecture/CANONICAL_LAYER_OWNERSHIP.csv",
        "docs/architecture/PRODUCTION_RUNTIME_BOUNDARY.md",
        "docs/architecture/SCIENTIFIC_DECISION_PIPELINE.md",
        "docs/architecture/EVIDENCE_PROVENANCE_ARCHITECTURE.md",
        "docs/architecture/FORMULA_EXECUTION_ARCHITECTURE.md",
        "docs/architecture/OPTIMIZATION_DECISION_ARCHITECTURE.md",
        "docs/architecture/FINANCIAL_MODEL_ARCHITECTURE.md",
        "docs/architecture/THREE_SURFACE_PRESENTATION_ARCHITECTURE.md",
        "docs/architecture/API_PRESENTATION_CONTRACT.md",
        "docs/architecture/FAILURE_AND_FALLBACK_ARCHITECTURE.md",
        "docs/architecture/MIXED_BREED_MODEL.md",
        "docs/architecture/ENVIRONMENT_MODEL.md",
        "docs/architecture/WAREHOUSE_DOMAIN_MAP.csv",
        "docs/architecture/TRACE_LINEAGE_ARCHITECTURE.md",
        "docs/architecture/PRESENTATION_SECURITY_BOUNDARY.md",
        "docs/architecture/OMEGA9.8_ARCHITECTURE_SCORECARD.csv",
        "docs/architecture/ARCHITECTURAL_DEBT_REGISTER.csv",
        "docs/architecture/OMEGA9.8_ARCHITECTURE_COMPLETION_REPORT.md",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel


def test_pipeline_stages_and_production_runtime_path_documented():
    e2e = (ROOT / "docs/architecture/END_TO_END_RUNTIME_ARCHITECTURE.md").read_text(encoding="utf-8").lower()
    for stage in (
        "profile normalization",
        "biological resolution",
        "evidence collection",
        "mathematical assessment",
        "optimization",
        "presentation projection",
    ):
        assert stage in e2e

    boundary = (ROOT / "docs/architecture/PRODUCTION_RUNTIME_BOUNDARY.md").read_text(encoding="utf-8")
    assert "POST /api/v1/analyze" in boundary
    assert "PPIEWellnessAgent" in boundary
    assert "app.api.main" in boundary


def test_presentation_routes_and_api_contract_documented():
    src = (ROOT / "app/api/main.py").read_text(encoding="utf-8")
    for route in ("/", "/business", "/developer", "/health", "/api/v1/analyze", "/api/v1/presentation/three-surfaces"):
        assert route in src

    contract = (ROOT / "docs/architecture/API_PRESENTATION_CONTRACT.md").read_text(encoding="utf-8")
    for endpoint in ("GET /", "GET /business", "GET /developer", "GET /health", "POST /api/v1/analyze", "POST /api/v1/presentation/three-surfaces"):
        assert endpoint in contract


def test_formula_and_trace_contracts_exist():
    assert (ROOT / "docs/architecture/FORMULA_EXECUTION_ARCHITECTURE.md").is_file()
    assert (ROOT / "docs/architecture/TRACE_LINEAGE_ARCHITECTURE.md").is_file()
    assert (ROOT / "docs/architecture/TRACE_CANONICAL_CONTRACT.md").is_file()
    assert (ROOT / "docs/architecture/FORMULA_REGISTRY_CANONICAL_CONTRACT.md").is_file()


def test_known_blockers_remain_explicitly_documented():
    text = (ROOT / "docs/mathematics/WAREHOUSE_BLOCKERS.md").read_text(encoding="utf-8")
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
        "warehouse/",
    )
    for line in git.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().replace("\\", "/")
        assert not path.startswith(protected), f"protected path modified: {path}"
