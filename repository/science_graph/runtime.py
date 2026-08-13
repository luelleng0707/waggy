"""Ω7 scientific knowledge graph runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.warehouse import WarehouseInterface

from .builder import WarehouseScientificGraphBuilder
from .explainability import DeterministicScientificExplainability
from .models import GraphTrace, GraphTraceStage, GraphTraversal, GraphValidation, KnowledgeGraph
from .traversal import DeterministicScientificTraversalEngine
from .validator import WarehouseScientificGraphValidator


@dataclass(frozen=True)
class ScientificGraphRuntimeResult:
    graph: KnowledgeGraph
    validation: GraphValidation
    trace: GraphTrace


class ScientificGraphRuntime:
    def __init__(self, warehouse: WarehouseInterface):
        self.builder = WarehouseScientificGraphBuilder(warehouse)
        self.validator = WarehouseScientificGraphValidator()
        self.traversal = DeterministicScientificTraversalEngine()
        self.explainability = DeterministicScientificExplainability()

    def run(self) -> ScientificGraphRuntimeResult:
        run_id = uuid.uuid4().hex
        stages: list[GraphTraceStage] = []

        started = time.perf_counter()
        graph = self.builder.build()
        stages.append(
            GraphTraceStage(
                stage_name="Graph Build",
                formula_ids=("GRF-803",),
                input_summary="WarehouseInterface",
                output_summary="KnowledgeGraph",
                warehouse_row_ids=tuple(sorted({edge.warehouse_row_id for edge in graph.edges})),
                elapsed_ms=(time.perf_counter() - started) * 1000.0,
            )
        )

        started = time.perf_counter()
        validation = self.validator.validate(graph)
        stages.append(
            GraphTraceStage(
                stage_name="Graph Validation",
                formula_ids=validation.formula_ids,
                input_summary="KnowledgeGraph",
                output_summary="GraphValidation",
                warehouse_row_ids=tuple(sorted({issue.warehouse_row_id for issue in validation.issues})),
                elapsed_ms=(time.perf_counter() - started) * 1000.0,
            )
        )

        return ScientificGraphRuntimeResult(
            graph=graph,
            validation=validation,
            trace=GraphTrace(run_id=run_id, stages=tuple(stages)),
        )

    def traverse(self, graph: KnowledgeGraph, query: str, target_node_type: str) -> GraphTraversal:
        raw = self.traversal.traverse(graph, query, target_node_type)
        return self.explainability.explain(graph, raw)
