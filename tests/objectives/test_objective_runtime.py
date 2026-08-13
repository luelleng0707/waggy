from __future__ import annotations

from repository.models.explainability import ScientificCitation
from repository.objectives import ObjectiveNetworkRuntime
from repository.reasoning.models import ConditionAssessment
from repository.warehouse import WarehouseInterface


def _assessment(condition_id: str, condition_name: str, estimated_prevalence: float) -> ConditionAssessment:
    citation = ScientificCitation(
        citation_id=f"CIT-{condition_id}",
        paper_name="Deterministic Study",
        paper_link="https://example.org/study",
        scientific_quote="Deterministic reference quote.",
        fact_id=f"FACT-{condition_id}",
    )
    return ConditionAssessment(
        condition_id=condition_id,
        condition_name=condition_name,
        observed_prevalence=None,
        estimated_prevalence=estimated_prevalence,
        agreement_percentage=None,
        research_gap_status="observed",
        body_system="General",
        required_mechanisms=tuple(),
        supporting_papers=(citation.paper_name,),
        supporting_quotes=(citation.scientific_quote,),
        formula_ids_used=("EST-004",),
        citations=(citation,),
        reasoning_chain=tuple(),
        formula_traces=tuple(),
        runtime_trace_stage_ids=tuple(),
    )


def test_objective_runtime_is_deterministic():
    runtime = ObjectiveNetworkRuntime(warehouse=WarehouseInterface())
    assessments = (
        _assessment("COND_653473C1", "Hip Dysplasia", 63.0),
        _assessment("COND_2D00FDEA", "Atopic Dermatitis", 39.0),
        _assessment("COND_4F31B412", "Obesity", 44.0),
    )

    first = runtime.run(assessments)
    second = runtime.run(assessments)

    assert first.objective_plan == second.objective_plan
    assert first.mechanism_plan == second.mechanism_plan
    assert first.ingredient_plan == second.ingredient_plan
    assert first.ingredient_source_plan == second.ingredient_source_plan
    assert first.network_summary == second.network_summary


def test_objective_runtime_outputs_traceable_pipeline():
    runtime = ObjectiveNetworkRuntime(warehouse=WarehouseInterface())
    result = runtime.run(
        (
            _assessment("COND_653473C1", "Hip Dysplasia", 58.0),
            _assessment("COND_E1F6DDA1", "Osteoarthritis", 49.0),
        )
    )

    assert result.objective_plan
    assert result.mechanism_plan
    assert result.ingredient_plan
    assert result.ingredient_source_plan
    assert result.trace.stages

    formula_ids = {formula for stage in result.trace.stages for formula in stage.formula_ids}
    assert {
        "OBJ-501",
        "OBJ-502",
        "OBJ-503",
        "OBJ-504",
        "MEC-505",
        "ING-506",
        "SRC-601",
        "SRC-602",
    }.issubset(formula_ids)

    for row in result.objective_plan:
        assert row.supporting_papers
        assert row.supporting_quotes
        assert row.warehouse_rows_used

    for row in result.ingredient_source_plan:
        assert row.supporting_papers
        assert row.supporting_quotes
        assert row.warehouse_rows_used
