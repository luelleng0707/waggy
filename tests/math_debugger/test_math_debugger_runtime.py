from __future__ import annotations

from pathlib import Path

from repository.math_debugger import FormulaConstantValidator, MathDebuggerRuntime
from repository.mathematics.runtime import ScientificMathematicsRuntime
from repository.models.runtime import DogProfile
from repository.objectives.models import IngredientSourcePlan
from repository.pipeline.biological_runtime import (
    InMemoryEvidenceGraphBuilder,
    WarehouseBackedDogResolver,
    WarehouseBackedEnvironmentResolver,
    WarehouseBackedEvidenceCollector,
    WarehouseBackedLifeStageResolver,
    WarehouseBackedObservationResolver,
    WarehouseBackedTraitResolver,
)
from repository.optimization.runtime import OptimizationRuntime
from repository.warehouse import WarehouseInterface


def _profile() -> DogProfile:
    return DogProfile(
        dog_id="DOG_AUDIT_001",
        name="AuditDog",
        breeds=("Golden Retriever",),
        date_of_birth="2020-03-15",
        weight_kg=30.0,
        environment="Temperate suburban",
        climate="Temperate",
        city="Shanghai",
        country="CN",
        urbanicity="Urban",
        season="Summer",
        housing="Apartment",
        walking_environment="Mixed",
        groomer_observations=(
            {"trait_name": "coat_type", "trait_value": "Double Coat", "source": "groomer"},
        ),
    )


def _graph():
    wh = WarehouseInterface()
    profile = _profile()
    dog = WarehouseBackedDogResolver(wh).resolve(profile)
    life_stage = WarehouseBackedLifeStageResolver(wh).resolve(dog)
    environment = WarehouseBackedEnvironmentResolver(wh).resolve(profile)
    traits = WarehouseBackedObservationResolver().merge(profile, WarehouseBackedTraitResolver(wh).resolve(dog))
    collection = WarehouseBackedEvidenceCollector(wh).collect(dog, life_stage, environment, traits)
    graph = InMemoryEvidenceGraphBuilder().build(collection)
    return graph


def _fact_ids_in_warehouse() -> set[str]:
    wh = WarehouseInterface()
    ids: set[str] = set()
    for _, table in wh.load_all().items():
        if "fact_id" not in table.columns:
            continue
        ids.update(set(table["fact_id"].astype(str).str.strip()) - {""})
    return ids


def test_formula_trace_contains_required_fields_and_replay_matches_runtime():
    graph = _graph()
    trace = MathDebuggerRuntime().trace(graph)
    runtime_result = ScientificMathematicsRuntime().run(graph)

    assert trace.formula_traces
    assert trace.final_outputs
    runtime_outputs = {item.condition_id: item.estimated_prevalence for item in runtime_result.assessments}
    assert trace.final_outputs == runtime_outputs

    first = trace.formula_traces[0]
    assert first.formula_id
    assert first.formula_version
    assert first.equation
    assert first.substituted_equation
    assert first.input_variables is not None
    assert first.output_variable


def test_code_references_exist_and_line_ranges_valid():
    graph = _graph()
    trace = MathDebuggerRuntime().trace(graph)
    root = Path(__file__).resolve().parents[2]
    for code_ref in trace.code_references:
        target = root / code_ref.python_file
        assert target.exists()
        total_lines = len(target.read_text(encoding="utf-8").splitlines())
        if code_ref.source_line_start > 0:
            assert code_ref.source_line_start <= total_lines
            assert code_ref.source_line_end <= total_lines


def test_warehouse_trace_fact_ids_exist_when_provided():
    graph = _graph()
    trace = MathDebuggerRuntime().trace(graph)
    known_fact_ids = _fact_ids_in_warehouse()
    for row in trace.warehouse_trace:
        if row.evidence_id:
            assert row.evidence_id in known_fact_ids


def test_deterministic_trace_same_input_same_output():
    graph = _graph()
    first = MathDebuggerRuntime().trace(graph)
    second = MathDebuggerRuntime().trace(graph)
    assert first.formula_traces == second.formula_traces
    assert first.final_outputs == second.final_outputs


def test_missing_observed_evidence_reports_no_evidence_status():
    graph = _graph()
    edges = tuple([edge for edge in graph.edges if str(edge.get("evidence_type", "")).strip().lower() != "observed"])
    stripped = type(graph)(dog_id=graph.dog_id, nodes=graph.nodes, edges=edges, citations=graph.citations)
    trace = MathDebuggerRuntime().trace(stripped)
    statuses = {item.status for item in trace.formula_traces if item.formula_id == "MAT-1001"}
    assert "NO_EVIDENCE" in statuses


def test_formula_version_override_deterministic():
    graph = _graph()
    default_trace = MathDebuggerRuntime().trace(graph)
    explicit_trace = MathDebuggerRuntime().trace(graph, formula_version_overrides={"MAT-1005": "v1.0"})
    assert default_trace.final_outputs == explicit_trace.final_outputs


def test_formula_constant_audit_runs():
    validator = FormulaConstantValidator()
    rows = validator.audit()
    assert isinstance(rows, tuple)
    layer_issues = validator.cross_validate_layers()
    assert isinstance(layer_issues, tuple)
    assert not any(issue.startswith("MISSING_SPEC:MAT-") for issue in layer_issues)
    assert not any(issue.startswith("MISSING_PARAMETER_CONFIGURATION:MAT-") for issue in layer_issues)


def test_optimization_harmony_trace_components():
    source_plan = (
        IngredientSourcePlan(
            source_id="SRC_001",
            ingredient_id="ING_F9E1B8CF",
            ingredient_name="Omega-3",
            natural_amount=820.0,
            unit="mg_per_100g",
            bioavailability=0.82,
            coverage_score=1.0,
            formula_ids_used=("SRC-601",),
            supporting_papers=("Nutrients",),
            supporting_quotes=("Omega-3 source quote",),
            warehouse_rows_used=("sources.ingredient_sources:SRC_001:ING_F9E1B8CF",),
        ),
    )
    optimized = OptimizationRuntime(WarehouseInterface()).run(source_plan, {"life_stage": "adult", "weight_kg": 22.0}).optimized_bundle
    trace = MathDebuggerRuntime().trace_optimization(optimized)
    harmony_traces = [item for item in trace.formula_traces if item.formula_id == "HRM-711"]
    assert harmony_traces
    assert any("coverage_contribution" in row for row in harmony_traces[0].intermediate_calculations)
