"""Benchmark runner for mathematics formula versions."""

from __future__ import annotations

import json
from pathlib import Path

from repository.formulas.loader import FormulaWarehouseLoader
from repository.mathematics.runtime import ScientificMathematicsRuntime
from repository.models.runtime import EvidenceGraph
from repository.warehouse import WarehouseInterface

from .comparator import BenchmarkComparison, compare_versions
from .reports import render_comparison_report


class BenchmarkRunner:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse
        self.tables = FormulaWarehouseLoader(warehouse).load()

    def run(self, formula_id: str, baseline_version: str, candidate_versions: tuple[str, ...]) -> tuple[BenchmarkComparison, ...]:
        benchmark_rows = self.tables["formulas.benchmarks"]
        benchmark_paths = tuple(
            sorted(
                [str(row.get("dataset_path", "")).strip() for _, row in benchmark_rows.iterrows() if str(row.get("dataset_path", "")).strip()]
            )
        )
        baseline_results = self._run_version(formula_id, baseline_version, benchmark_paths)
        baseline_actual = tuple(result["actual"] for result in baseline_results)
        baseline_predicted = tuple(result["predicted"] for result in baseline_results)
        baseline_ranking = tuple(result["top_condition"] for result in baseline_results)

        comparisons: list[BenchmarkComparison] = []
        for version in candidate_versions:
            candidate_results = self._run_version(formula_id, version, benchmark_paths)
            candidate_predicted = tuple(result["predicted"] for result in candidate_results)
            candidate_ranking = tuple(result["top_condition"] for result in candidate_results)
            comparisons.append(
                compare_versions(
                    reference_actual=baseline_actual,
                    baseline_predicted=baseline_predicted,
                    candidate_predicted=candidate_predicted,
                    baseline_ranking=baseline_ranking,
                    candidate_ranking=candidate_ranking,
                    candidate_version=version,
                )
            )
        return tuple(comparisons)

    def report(self, formula_id: str, baseline_version: str, candidate_versions: tuple[str, ...]) -> str:
        comparisons = self.run(formula_id, baseline_version, candidate_versions)
        return render_comparison_report(comparisons)

    def _run_version(self, formula_id: str, version: str, benchmark_paths: tuple[str, ...]) -> list[dict[str, object]]:
        runtime = ScientificMathematicsRuntime(formula_version_overrides={formula_id: version})
        outputs: list[dict[str, object]] = []
        for path in benchmark_paths:
            payload = _load_benchmark_payload(path)
            graph = _build_graph(payload["evidence_graph"])
            result = runtime.run(graph)
            top = result.assessments[0]
            actual = top.observed_prevalence
            predicted = top.estimated_prevalence
            outputs.append({"actual": actual, "predicted": predicted, "top_condition": top.condition_id})
        return outputs


def _load_benchmark_payload(relative_path: str) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    target = root / relative_path
    with target.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_graph(payload: dict[str, object]) -> EvidenceGraph:
    return EvidenceGraph(
        dog_id=str(payload.get("dog_id", "")),
        nodes=tuple(payload.get("nodes", tuple())),
        edges=tuple(payload.get("edges", tuple())),
        citations=tuple(payload.get("citations", tuple())),
    )
