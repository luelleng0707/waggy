from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from repository.formulas.loader import FormulaWarehouseLoader
from repository.mathematics.runtime import ScientificMathematicsRuntime
from repository.models.runtime import EvidenceGraph
from repository.warehouse import WarehouseInterface


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs" / "mathematics"
EXPECTED_BENCHMARK_HASH = "b2b200753bc955b6568cbc52c83e88151db65370c58159e9d718a7e0a75b9303"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _benchmark_output_hash() -> str:
    wh = WarehouseInterface()
    rows = FormulaWarehouseLoader(wh).load()["formulas.benchmarks"]
    benchmark_paths = sorted([str(row.get("dataset_path", "")).strip() for _, row in rows.iterrows() if str(row.get("dataset_path", "")).strip()])
    runtime = ScientificMathematicsRuntime()
    outputs = []
    for path in benchmark_paths:
        payload = json.loads((ROOT / path).read_text(encoding="utf-8"))
        graph_payload = payload["evidence_graph"]
        graph = EvidenceGraph(
            dog_id=str(graph_payload.get("dog_id", "")),
            nodes=tuple(graph_payload.get("nodes", tuple())),
            edges=tuple(graph_payload.get("edges", tuple())),
            citations=tuple(graph_payload.get("citations", tuple())),
        )
        result = runtime.run(graph)
        outputs.append(
            {
                "dataset_path": path,
                "assessments": [
                    {
                        "condition_id": item.condition_id,
                        "observed_prevalence": item.observed_prevalence,
                        "estimated_prevalence": item.estimated_prevalence,
                        "agreement": item.agreement,
                        "confidence": item.confidence,
                        "priority": item.priority,
                        "novelty": item.novelty,
                        "uncertainty": item.uncertainty,
                    }
                    for item in result.assessments
                ],
            }
        )
    blob = json.dumps(outputs, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def test_all_mat_formulas_are_inventoried():
    rows = _csv_rows(DOCS / "FORMULA_REGISTRY.csv")
    expected = {"MAT-1001", "MAT-1002", "MAT-1003", "MAT-1004", "MAT-1005", "MAT-1006", "MAT-1007", "MAT-1008"}
    actual = {row["formula_id"] for row in rows}
    assert expected.issubset(actual)


def test_mat1002_parameters_are_classified_and_engineering_identified():
    rows = _csv_rows(DOCS / "MAT1002_PARAMETER_AUDIT.csv")
    allowed = {"SCIENTIFICALLY_ESTIMATED", "EMPIRICALLY_DERIVED", "ENGINEERING_PARAMETER", "MATHEMATICAL_CONSTANT", "UNKNOWN"}
    assert rows
    assert all(row["classification"] in allowed for row in rows)
    assert any(row["classification"] == "ENGINEERING_PARAMETER" for row in rows)


def test_all_formulas_have_dependencies_and_no_false_scientific_label():
    dep_rows = _csv_rows(DOCS / "FORMULA_DEPENDENCIES.csv")
    formulas = {row["formula_id"] for row in dep_rows}
    expected = {"MAT-1001", "MAT-1002", "MAT-1003", "MAT-1004", "MAT-1005", "MAT-1006", "MAT-1007", "MAT-1008"}
    assert expected.issubset(formulas)
    registry_rows = _csv_rows(DOCS / "FORMULA_REGISTRY.csv")
    for row in registry_rows:
        if row["formula_id"] in expected:
            assert row["scientific_provenance_status"] != "SCIENTIFICALLY_SUPPORTED"


def test_mixed_breed_first_path_behavior_is_detected():
    text = _read_text(DOCS / "OMEGA9_CURRENT_MODEL.md")
    assert "profile.breeds[0]" in text


def test_bayesian_methodology_flag_present_when_likelihood_not_explicit():
    text = _read_text(DOCS / "PROPOSED_FORMULA_REGISTRY.md")
    assert "METHODOLOGICAL_REDESIGN_REQUIRED" in text


def test_uncertainty_and_agreement_semantics_are_checked():
    text = _read_text(DOCS / "OMEGA9_CURRENT_MODEL.md")
    assert "not a formal statistical confidence interval" in text
    assert "agreement is not confidence" in text


def test_warehouse_blockers_are_detected():
    text = _read_text(DOCS / "WAREHOUSE_BLOCKERS.md")
    blocker_rows = [line for line in text.splitlines() if line.startswith("| mechanisms.")]
    assert len(blocker_rows) == 8


def test_production_outputs_remain_unchanged():
    assert _benchmark_output_hash() == EXPECTED_BENCHMARK_HASH
