"""Ω9 mathematics runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.models.runtime import EvidenceGraph
from repository.reasoning.models import ConditionAssessment

from .agreement import AgreementMathematicsEngine
from .aggregation import TraitAggregationEngine
from .confidence import ConfidenceMathematicsEngine
from .epidemiology import ObservedEpidemiologyEngine
from .models import (
    MathematicalAssessment,
    MathematicsRuntimeResult,
    MathematicsStageTrace,
    MathematicsTrace,
)
from .novelty import NoveltyMathematicsEngine
from .priority import PriorityMathematicsEngine
from .uncertainty import UncertaintyMathematicsEngine


class MathematicalAssessmentAssembler:
    def assemble(self, observed, estimated, agreement, confidence, novelty, uncertainty, priority) -> MathematicalAssessment:
        formula_ids = []
        for payload in (observed, estimated, agreement, confidence, novelty, uncertainty, priority):
            for trace in payload.formula_traces:
                formula_ids.append(trace.formula_id)
        all_traces = tuple(
            list(observed.formula_traces)
            + list(estimated.formula_traces)
            + list(agreement.formula_traces)
            + list(confidence.formula_traces)
            + list(novelty.formula_traces)
            + list(uncertainty.formula_traces)
            + list(priority.formula_traces)
        )
        return MathematicalAssessment(
            condition_id=observed.condition_id,
            condition_name=observed.condition_name,
            observed_prevalence=observed.observed_prevalence,
            estimated_prevalence=estimated.estimated_prevalence,
            confidence=confidence.confidence_score,
            agreement=agreement.agreement_percent,
            priority=priority.priority_score,
            novelty=novelty.novelty_score,
            uncertainty=uncertainty.uncertainty,
            lower_bound=uncertainty.lower_bound,
            upper_bound=uncertainty.upper_bound,
            supporting_formulas=tuple(sorted(set(formula_ids))),
            supporting_quotes=observed.supporting_quotes,
            supporting_papers=observed.supporting_papers,
            supporting_links=observed.supporting_links,
            supporting_evidence_ids=tuple(sorted(set([str(trace.output) for trace in observed.formula_traces]))),
            formula_traces=all_traces,
        )


@dataclass(frozen=True)
class ScientificMathematicsRuntime:
    formula_version_overrides: dict[str, str] | None = None
    observed_engine: ObservedEpidemiologyEngine | None = None
    aggregation_engine: TraitAggregationEngine | None = None
    agreement_engine: AgreementMathematicsEngine | None = None
    confidence_engine: ConfidenceMathematicsEngine | None = None
    novelty_engine: NoveltyMathematicsEngine | None = None
    uncertainty_engine: UncertaintyMathematicsEngine | None = None
    priority_engine: PriorityMathematicsEngine | None = None
    assembler: MathematicalAssessmentAssembler | None = None

    def __post_init__(self) -> None:
        overrides = self.formula_version_overrides or {}
        if self.observed_engine is None:
            object.__setattr__(self, "observed_engine", ObservedEpidemiologyEngine())
        if self.aggregation_engine is None:
            object.__setattr__(self, "aggregation_engine", TraitAggregationEngine(overrides))
        if self.agreement_engine is None:
            object.__setattr__(self, "agreement_engine", AgreementMathematicsEngine())
        if self.confidence_engine is None:
            object.__setattr__(self, "confidence_engine", ConfidenceMathematicsEngine(overrides))
        if self.novelty_engine is None:
            object.__setattr__(self, "novelty_engine", NoveltyMathematicsEngine(overrides))
        if self.uncertainty_engine is None:
            object.__setattr__(self, "uncertainty_engine", UncertaintyMathematicsEngine(overrides))
        if self.priority_engine is None:
            object.__setattr__(self, "priority_engine", PriorityMathematicsEngine(overrides))
        if self.assembler is None:
            object.__setattr__(self, "assembler", MathematicalAssessmentAssembler())

    def run(
        self,
        evidence_graph: EvidenceGraph,
        condition_assessments: tuple[ConditionAssessment, ...] = (),
    ) -> MathematicsRuntimeResult:
        run_id = uuid.uuid4().hex
        traces: list[MathematicsStageTrace] = []
        citations = {str(c.get("citation_id", "")): c for c in evidence_graph.citations}
        condition_nodes = [node for node in evidence_graph.nodes if str(node.get("node_type", "")).strip().lower() == "condition"]
        condition_name_override = {row.condition_id: row.condition_name for row in condition_assessments}

        pre_rank: list[dict[str, object]] = []
        for condition_node in sorted(condition_nodes, key=lambda row: str(row.get("condition_id", ""))):
            condition_id = str(condition_node.get("condition_id", "")).strip()
            if not condition_id:
                continue
            condition_name = condition_name_override.get(condition_id, str(condition_node.get("condition_name", "")).strip() or condition_id)
            node_id = str(condition_node.get("node_id", "")).strip()
            edges = tuple(
                sorted(
                    [edge for edge in evidence_graph.edges if str(edge.get("to_node_id", "")).strip() == node_id],
                    key=lambda row: str(row.get("edge_id", "")),
                )
            )

            observed, elapsed = _timed(lambda: self.observed_engine.evaluate(condition_id, condition_name, edges, citations))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Observed Epidemiology:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in observed.formula_traces]))),
                    input_summary="condition_edges",
                    output_summary="ObservedEpidemiology",
                    elapsed_ms=elapsed,
                )
            )
            estimated, elapsed = _timed(lambda: self.aggregation_engine.estimate(condition_id, condition_name, observed, edges))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Trait Aggregation:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in estimated.formula_traces]))),
                    input_summary="observed+condition_edges",
                    output_summary="EstimatedEpidemiology",
                    elapsed_ms=elapsed,
                )
            )
            agreement, elapsed = _timed(lambda: self.agreement_engine.evaluate(observed, estimated))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Agreement Mathematics:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in agreement.formula_traces]))),
                    input_summary="observed+estimated",
                    output_summary="AgreementMetrics",
                    elapsed_ms=elapsed,
                )
            )
            confidence, elapsed = _timed(lambda: self.confidence_engine.evaluate(observed, estimated, agreement, edges))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Confidence Mathematics:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in confidence.formula_traces]))),
                    input_summary="observed+estimated+agreement+condition_edges",
                    output_summary="ConfidenceMetrics",
                    elapsed_ms=elapsed,
                )
            )
            novelty, elapsed = _timed(lambda: self.novelty_engine.evaluate(observed, estimated, confidence))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Novelty Mathematics:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in novelty.formula_traces]))),
                    input_summary="observed+estimated+confidence",
                    output_summary="NoveltyMetrics",
                    elapsed_ms=elapsed,
                )
            )
            uncertainty, elapsed = _timed(lambda: self.uncertainty_engine.evaluate(estimated, confidence, edges))
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Uncertainty Mathematics:{condition_id}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in uncertainty.formula_traces]))),
                    input_summary="estimated+confidence+condition_edges",
                    output_summary="UncertaintyMetrics",
                    elapsed_ms=elapsed,
                )
            )
            pre_rank.append(
                {
                    "condition_id": condition_id,
                    "condition_name": condition_name,
                    "observed": observed,
                    "estimated": estimated,
                    "agreement": agreement,
                    "confidence": confidence,
                    "novelty": novelty,
                    "uncertainty": uncertainty,
                }
            )

        pre_rank_sorted = sorted(
            pre_rank,
            key=lambda row: (
                -row["estimated"].estimated_prevalence,
                -row["confidence"].confidence_score,
                row["condition_id"],
            ),
        )
        assessments: list[MathematicalAssessment] = []
        for idx, item in enumerate(pre_rank_sorted, start=1):
            priority, elapsed = _timed(
                lambda item=item, idx=idx: self.priority_engine.rank(
                    condition_id=item["condition_id"],
                    condition_name=item["condition_name"],
                    estimated_prevalence=item["estimated"].estimated_prevalence,
                    confidence=item["confidence"],
                    agreement=item["agreement"],
                    novelty=item["novelty"],
                    rank=idx,
                )
            )
            traces.append(
                MathematicsStageTrace(
                    stage_name=f"Priority Mathematics:{item['condition_id']}",
                    formula_ids=tuple(sorted(set([trace.formula_id for trace in priority.formula_traces]))),
                    input_summary="estimated+confidence+agreement+novelty",
                    output_summary="PriorityMetrics",
                    elapsed_ms=elapsed,
                )
            )
            assessments.append(
                self.assembler.assemble(
                    observed=item["observed"],
                    estimated=item["estimated"],
                    agreement=item["agreement"],
                    confidence=item["confidence"],
                    novelty=item["novelty"],
                    uncertainty=item["uncertainty"],
                    priority=priority,
                )
            )
        assessments = sorted(assessments, key=lambda row: (row.priority * -1.0, row.condition_id))
        return MathematicsRuntimeResult(
            assessments=tuple(assessments),
            trace=MathematicsTrace(run_id=run_id, stages=tuple(traces)),
        )


def _timed(fn):
    started = time.perf_counter()
    value = fn()
    elapsed = (time.perf_counter() - started) * 1000.0
    return value, elapsed
