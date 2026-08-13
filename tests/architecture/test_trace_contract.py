from __future__ import annotations

from dataclasses import asdict

from repository.math_debugger.formula_trace import build_formula_trace
from repository.math_debugger.pipeline_trace import build_pipeline_trace
from repository.mathematics.models import (
    MathematicalAssessment,
    MathematicalFormulaTrace,
    MathematicsRuntimeResult,
    MathematicsStageTrace,
    MathematicsTrace,
)
from repository.models.trace import RuntimeTrace, StageTrace


def _formula_trace() -> MathematicalFormulaTrace:
    return MathematicalFormulaTrace(
        formula_id="MAT-1001",
        formula_version="v1.0.0",
        formula_name="Observed prevalence",
        status="ACTIVE",
        equation="x / n",
        substituted_equation="10 / 100",
        python_file="repository/mathematics/epidemiology.py",
        python_function="compute_observed_prevalence",
        source_line_start=10,
        source_line_end=20,
        input_variables=("observed_values_sum", "observed_count"),
        inputs={"observed_values_sum": 10.0, "observed_count": 100.0},
        parameter_values={"min_count": 1.0},
        intermediate_values={"ratio": 0.1},
        output_variable="observed_prevalence",
        unit="percent",
        warehouse_row_ids=("FACT001",),
        evidence_ids=("EVID001",),
        paper_names=("Study A",),
        paper_links=("https://example.org/study-a",),
        scientific_quotes=("Observed prevalence quote",),
        output=10.0,
    )


def test_formula_trace_preserves_provenance_through_debugger_conversion():
    raw = _formula_trace()
    trace = build_formula_trace("COND001", 0, raw, tuple())
    payload = asdict(trace)
    assert payload["formula_id"] == "MAT-1001"
    assert payload["formula_version"] == "v1.0.0"
    assert payload["equation"] == "x / n"
    assert payload["substituted_equation"] == "10 / 100"
    assert payload["warehouse_trace_rows"][0]["warehouse_row_id"] == "FACT001"
    assert payload["warehouse_trace_rows"][0]["evidence_id"] == "EVID001"
    assert payload["warehouse_trace_rows"][0]["paper_link"] == "https://example.org/study-a"


def test_execution_trace_keeps_formula_and_citation_path():
    assessment = MathematicalAssessment(
        condition_id="COND001",
        condition_name="Condition 1",
        observed_prevalence=10.0,
        estimated_prevalence=12.0,
        confidence=75.0,
        agreement=90.0,
        priority=7.0,
        novelty=5.0,
        uncertainty=2.0,
        lower_bound=8.0,
        upper_bound=14.0,
        supporting_formulas=("MAT-1001",),
        supporting_quotes=("Observed prevalence quote",),
        supporting_papers=("Study A",),
        supporting_links=("https://example.org/study-a",),
        supporting_evidence_ids=("EVID001",),
        formula_traces=(_formula_trace(),),
    )
    runtime_result = MathematicsRuntimeResult(
        assessments=(assessment,),
        trace=MathematicsTrace(
            run_id="RUN001",
            stages=(
                MathematicsStageTrace(
                    stage_name="Observed",
                    formula_ids=("MAT-1001",),
                    input_summary="inputs",
                    output_summary="outputs",
                    elapsed_ms=1.2,
                ),
            ),
        ),
    )
    execution = build_pipeline_trace(runtime_result)
    assert execution.run_id == "RUN001"
    assert execution.formula_traces[0].formula_id == "MAT-1001"
    assert execution.formula_traces[0].warehouse_trace_rows[0].paper_name == "Study A"
    assert execution.final_outputs["COND001"] == 12.0


def test_runtime_stage_trace_contract_keeps_timing_and_errors():
    rt = RuntimeTrace(
        run_id="RUN001",
        stages=(
            StageTrace(
                stage_name="Dog Resolver",
                input_summary="DogProfile",
                output_summary="ResolvedDog",
                runtime_ms=12.5,
                warnings=("w1",),
                errors=("e1",),
            ),
        ),
    )
    payload = asdict(rt)
    assert payload["stages"][0]["stage_name"] == "Dog Resolver"
    assert payload["stages"][0]["runtime_ms"] == 12.5
    assert payload["stages"][0]["warnings"] == ("w1",)
    assert payload["stages"][0]["errors"] == ("e1",)
