"""Ω4 scientific inference runtime: EvidenceGraph -> ConditionAssessment[]"""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.models.explainability import ScientificCitation
from repository.models.runtime import EvidenceGraph, ResolvedDog
from repository.reasoning.agreement import DeterministicAgreementEngine
from repository.reasoning.estimation import DeterministicEstimatedEngine
from repository.reasoning.explainability import build_reasoning_chain
from repository.reasoning.interfaces import (
    AgreementEngine,
    ConditionAssessmentBuilder,
    EstimatedEngine,
    MechanismMapper,
    ObservedEngine,
    SystemAggregator,
)
from repository.reasoning.models import (
    AgreementResult,
    ConditionAssessment,
    EstimatedCondition,
    FormulaTrace,
    ObservedCondition,
    ReasoningRuntimeTrace,
    StageRuntimeTrace,
)
from repository.reasoning.observed import DeterministicObservedEngine
from repository.reasoning.mechanisms import WarehouseMechanismMapper
from repository.reasoning.systems import WarehouseSystemAggregator
from repository.warehouse import WarehouseInterface


@dataclass(frozen=True)
class ScientificInferenceResult:
    assessments: tuple[ConditionAssessment, ...]
    trace: ReasoningRuntimeTrace


class DeterministicConditionAssessmentBuilder:
    def build(
        self,
        observed: tuple[ObservedCondition, ...],
        estimated: tuple[EstimatedCondition, ...],
        agreement: tuple[AgreementResult, ...],
    ) -> tuple[ConditionAssessment, ...]:
        observed_by_id = {o.condition_id: o for o in observed}
        agreement_by_id = {a.condition_id: a for a in agreement}

        assessments: list[ConditionAssessment] = []
        for est in estimated:
            obs = observed_by_id.get(est.condition_id)
            agr = agreement_by_id.get(est.condition_id)

            research_gap_status = "observed" if obs is not None else "emerging_condition"
            agreement_pct = agr.agreement_percentage if agr is not None else None
            observed_pct = obs.observed_prevalence if obs is not None else None

            citations = tuple(est.citations) + (tuple(obs.citations) if obs else tuple())
            papers = tuple(sorted(set([c.paper_name for c in citations if c.paper_name])))
            quotes = tuple([c.scientific_quote for c in citations if c.scientific_quote])
            formula_ids: list[str] = [f.formula_id for f in est.formula_traces]
            if obs:
                formula_ids.extend([f.formula_id for f in obs.formula_traces])
            if agr:
                formula_ids.extend([f.formula_id for f in agr.formula_traces])

            chain = build_reasoning_chain(obs, est, agr)
            formula_traces: list[FormulaTrace] = list(est.formula_traces)
            if obs:
                formula_traces.extend(list(obs.formula_traces))
            if agr:
                formula_traces.extend(list(agr.formula_traces))

            assessments.append(
                ConditionAssessment(
                    condition_id=est.condition_id,
                    condition_name=est.condition_name,
                    observed_prevalence=observed_pct,
                    estimated_prevalence=est.estimated_prevalence,
                    agreement_percentage=agreement_pct,
                    research_gap_status=research_gap_status,
                    body_system="Unknown",
                    required_mechanisms=tuple(),
                    supporting_papers=papers,
                    supporting_quotes=quotes,
                    formula_ids_used=tuple(sorted(set(formula_ids))),
                    citations=citations,
                    reasoning_chain=chain,
                    formula_traces=tuple(formula_traces),
                    runtime_trace_stage_ids=tuple([s.stage for s in chain]),
                )
            )
        return tuple(assessments)


class ScientificInferenceRuntime:
    def __init__(
        self,
        warehouse: WarehouseInterface,
        observed_engine: ObservedEngine | None = None,
        estimated_engine: EstimatedEngine | None = None,
        agreement_engine: AgreementEngine | None = None,
        assessment_builder: ConditionAssessmentBuilder | None = None,
        system_aggregator: SystemAggregator | None = None,
        mechanism_mapper: MechanismMapper | None = None,
    ):
        self.observed_engine = observed_engine or DeterministicObservedEngine()
        self.estimated_engine = estimated_engine or DeterministicEstimatedEngine()
        self.agreement_engine = agreement_engine or DeterministicAgreementEngine()
        self.assessment_builder = assessment_builder or DeterministicConditionAssessmentBuilder()
        self.system_aggregator = system_aggregator or WarehouseSystemAggregator(warehouse)
        self.mechanism_mapper = mechanism_mapper or WarehouseMechanismMapper(warehouse)

    def run(self, resolved_dog: ResolvedDog, evidence_graph: EvidenceGraph) -> ScientificInferenceResult:
        trace_items: list[StageRuntimeTrace] = []
        run_id = uuid.uuid4().hex

        def _run(name: str, fn, *args):
            started = time.perf_counter()
            out = fn(*args)
            elapsed = (time.perf_counter() - started) * 1000.0
            formula_ids: list[str] = []
            condition_ids: list[str] = []
            evidence_ids: list[str] = []
            warehouse_rows: list[str] = []

            if isinstance(out, tuple):
                for item in out:
                    if hasattr(item, "formula_traces"):
                        formula_ids.extend([f.formula_id for f in getattr(item, "formula_traces", tuple())])
                    if hasattr(item, "condition_id"):
                        condition_ids.append(getattr(item, "condition_id"))
                    if hasattr(item, "source_fact_id"):
                        evidence_ids.append(getattr(item, "source_fact_id"))
                    if hasattr(item, "citations"):
                        evidence_ids.extend([c.fact_id for c in getattr(item, "citations", tuple()) if c.fact_id])
            elif hasattr(out, "edges"):
                warehouse_rows.extend([e.get("source_fact_id", "") for e in getattr(out, "edges", tuple()) if e.get("source_fact_id", "")])

            trace_items.append(
                StageRuntimeTrace(
                    stage_name=name,
                    execution_time_ms=elapsed,
                    formula_ids=tuple(sorted(set([f for f in formula_ids if f]))),
                    warehouse_rows_used=tuple(sorted(set([w for w in warehouse_rows if w]))),
                    evidence_ids=tuple(sorted(set([e for e in evidence_ids if e]))),
                    condition_ids=tuple(sorted(set([c for c in condition_ids if c]))),
                    input_summary=",".join([type(a).__name__ for a in args]),
                    output_summary=type(out).__name__,
                )
            )
            return out

        observed = _run("Observed Epidemiology", self.observed_engine.evaluate, evidence_graph)
        estimated = _run("Estimated Epidemiology", self.estimated_engine.evaluate, resolved_dog, evidence_graph)
        agreement = _run("Agreement Analysis", self.agreement_engine.evaluate, observed, estimated)
        assessments = _run("Condition Assessment Build", self.assessment_builder.build, observed, estimated, agreement)
        assessments = _run("System Aggregation", self.system_aggregator.aggregate, assessments)
        assessments = _run("Mechanism Mapping", self.mechanism_mapper.map, assessments)

        return ScientificInferenceResult(
            assessments=assessments,
            trace=ReasoningRuntimeTrace(run_id=run_id, stages=tuple(trace_items)),
        )
