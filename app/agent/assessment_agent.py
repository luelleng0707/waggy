"""AssessmentAgent — owns profile → FormulaGraph → AssessmentResult."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from app.agent.assessment_result import AssessmentResult
from app.agent.execution_context import ExecutionContext
from app.agent.formula_graph import FormulaGraph
from app.agent.nodes import default_nodes
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.data.warehouse.parameters import ParameterRepository
from app.data.warehouse.units import UnitNormalizer

logger = logging.getLogger(__name__)


class AssessmentAgent:
    """
    Single owner of assessment execution.

    AssessmentAgent → ExecutionContext → FormulaGraph → AssessmentResult
    Nodes never call each other; only the graph schedules execute().
    """

    def __init__(
        self,
        repository: DataRepository,
        *,
        parameters: ParameterRepository | None = None,
        units: UnitNormalizer | None = None,
        graph: FormulaGraph | None = None,
    ):
        self.repository = repository
        self.parameters = parameters or ParameterRepository()
        self.units = units or UnitNormalizer()
        self.graph = graph or FormulaGraph(default_nodes())

    def assess(self, profile: DogProfileInput) -> AssessmentResult:
        t0 = perf_counter()
        context = ExecutionContext(
            profile=profile,
            repository=self.repository,
            parameters=self.parameters,
            units=self.units,
            inputs={"profile": profile.model_dump()},
        )
        self.graph.execute(context)
        result = AssessmentResult.from_context(context)
        # Phase 4: additive knowledge-graph explainability (does not alter clinical math)
        try:
            from app.science.attach import attach_science_to_analyze, build_reasoning_payload

            reasoning = build_reasoning_payload(
                profile=profile, result=result, repository=self.repository
            )
            result.legacy_json = attach_science_to_analyze(result.legacy_json or {}, reasoning)
            result.debug = {**(result.debug or {}), "science": reasoning}
            result.evidence = {
                **(result.evidence or {}),
                "objects": reasoning.get("evidence_objects") or [],
                "recommendations": reasoning.get("recommendation_explanations") or [],
            }
        except Exception:  # noqa: BLE001
            logger.exception("Science explainability attach failed — clinical result preserved")
        elapsed = round((perf_counter() - t0) * 1000, 3)
        result.performance = {
            **(result.performance or {}),
            "total_ms": elapsed,
            "metrics": context.metrics,
            "stage_timings_ms": context.metrics.get("stage_timings_ms"),
        }
        logger.info(
            "AssessmentAgent complete name=%s risks=%s nodes=%s total_ms=%s",
            profile.name,
            len((result.health or {}).get("risks") or []),
            len(context.execution_trace),
            elapsed,
        )
        return result

    def assess_legacy_json(self, profile: DogProfileInput) -> dict[str, Any]:
        """Public analyze-compatible dict."""
        return self.assess(profile).to_analyze_dict()

    def describe_graph(self) -> list[dict[str, Any]]:
        return self.graph.describe()
