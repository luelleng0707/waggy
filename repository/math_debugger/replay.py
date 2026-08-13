"""Deterministic replay engine for mathematics runtime."""

from __future__ import annotations

from repository.mathematics.runtime import ScientificMathematicsRuntime
from repository.models.runtime import EvidenceGraph
from repository.reasoning.models import ConditionAssessment

from .pipeline_trace import build_pipeline_trace


class DeterministicMathReplay:
    def replay(
        self,
        evidence_graph: EvidenceGraph,
        condition_assessments: tuple[ConditionAssessment, ...] = (),
        formula_version_overrides: dict[str, str] | None = None,
    ):
        runtime = ScientificMathematicsRuntime(formula_version_overrides=formula_version_overrides or {})
        result = runtime.run(evidence_graph, condition_assessments)
        return build_pipeline_trace(result)
