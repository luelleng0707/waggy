from __future__ import annotations

from repository.mechanisms import BiologicalMechanismRuntime
from repository.models.explainability import ScientificCitation
from repository.reasoning.models import ConditionAssessment
from repository.warehouse import WarehouseInterface


def _assessment(
    condition_id: str,
    condition_name: str,
    estimated_prevalence: float,
) -> ConditionAssessment:
    citation = ScientificCitation(
        citation_id=f"CIT-{condition_id}",
        paper_name="Reference Paper",
        paper_link="https://example.org/paper",
        scientific_quote="Reference scientific quote.",
        fact_id=f"FACT-{condition_id}",
    )
    return ConditionAssessment(
        condition_id=condition_id,
        condition_name=condition_name,
        observed_prevalence=None,
        estimated_prevalence=estimated_prevalence,
        agreement_percentage=None,
        research_gap_status="observed",
        body_system="Musculoskeletal",
        required_mechanisms=tuple(),
        supporting_papers=(citation.paper_name,),
        supporting_quotes=(citation.scientific_quote,),
        formula_ids_used=("EST-004",),
        citations=(citation,),
        reasoning_chain=tuple(),
        formula_traces=tuple(),
        runtime_trace_stage_ids=tuple(),
    )


def test_omega5_runtime_is_deterministic():
    runtime = BiologicalMechanismRuntime(warehouse=WarehouseInterface())
    assessments = (
        _assessment("COND_HIP_DYSPLASIA", "Hip Dysplasia", 62.0),
        _assessment("COND_ATOPIC_DERMATITIS", "Atopic Dermatitis", 38.0),
    )
    context = {
        "weight_kg": 24.0,
        "life_stage": "adult",
        "activity": "medium",
        "climate": "hot",
    }

    first = runtime.run(assessments, context)
    second = runtime.run(assessments, context)

    assert first.mechanism_plan == second.mechanism_plan
    assert first.dose_targets == second.dose_targets
    assert first.interaction_report == second.interaction_report


def test_omega5_outputs_traceable_structures():
    runtime = BiologicalMechanismRuntime(warehouse=WarehouseInterface())
    assessments = (
        _assessment("COND_HIP_DYSPLASIA", "Hip Dysplasia", 55.0),
        _assessment("COND_OBESITY", "Obesity", 41.0),
    )
    result = runtime.run(assessments, {"weight_kg": 30.0, "life_stage": "senior"})

    assert result.mechanism_plan
    assert result.dose_targets
    assert result.trace.stages

    for plan in result.mechanism_plan:
        assert plan.formula_ids_used
        assert plan.dose_formula_ids
        assert plan.supporting_papers
        assert plan.supporting_quotes

    for target in result.dose_targets:
        assert target.formula_id
        assert target.reasoning
        assert target.papers
        assert target.quotes

    formula_ids_in_trace = {formula for stage in result.trace.stages for formula in stage.formula_ids}
    assert {"OBJ-001", "MEC-201", "MEC-202", "DOS-302", "INT-401", "INT-402"}.issubset(
        formula_ids_in_trace
    )
