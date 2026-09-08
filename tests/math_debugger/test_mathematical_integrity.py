from __future__ import annotations

from pathlib import Path

from repository.math_debugger import FormulaConstantValidator, MathDebuggerRuntime
from repository.math_debugger.independent_replay import IndependentFormulaReplay
from repository.math_debugger.numerical_inventory import CLASSIFICATIONS, NumericalInventoryBuilder
from repository.math_debugger.sensitivity import SensitivityAnalyzer
from repository.mathematics.agreement import AgreementMathematicsEngine
from repository.mathematics.bayesian import posterior_percent
from repository.mathematics.models import EstimatedEpidemiology, ObservedEpidemiology
from repository.models.runtime import DogProfile
from repository.pipeline.biological_runtime import (
    InMemoryEvidenceGraphBuilder,
    WarehouseBackedDogResolver,
    WarehouseBackedEnvironmentResolver,
    WarehouseBackedEvidenceCollector,
    WarehouseBackedLifeStageResolver,
    WarehouseBackedObservationResolver,
    WarehouseBackedTraitResolver,
)
from repository.warehouse import WarehouseInterface

_INVENTORY_CACHE = NumericalInventoryBuilder().build()


def _profile() -> DogProfile:
    return DogProfile(
        dog_id="DOG_AUDIT_OMEGA93",
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
        groomer_observations=({"trait_name": "coat_type", "trait_value": "Double Coat", "source": "groomer"},),
    )


def _graph():
    wh = WarehouseInterface()
    profile = _profile()
    dog = WarehouseBackedDogResolver(wh).resolve(profile)
    life_stage = WarehouseBackedLifeStageResolver(wh).resolve(dog)
    environment = WarehouseBackedEnvironmentResolver(wh).resolve(profile)
    traits = WarehouseBackedObservationResolver().merge(profile, WarehouseBackedTraitResolver(wh).resolve(dog))
    collection = WarehouseBackedEvidenceCollector(wh).collect(dog, life_stage, environment, traits)
    return InMemoryEvidenceGraphBuilder().build(collection)


def test_numerical_inventory_assigns_single_classification():
    rows = _INVENTORY_CACHE
    assert rows
    assert all(row.classification in CLASSIFICATIONS for row in rows)


def test_unknown_values_are_reported_for_review():
    rows = _INVENTORY_CACHE
    unknown = [row for row in rows if row.classification == "UNKNOWN"]
    assert all(row.review_required == "YES" for row in unknown)


def test_scientific_parameter_rows_require_numeric_support():
    rows = _INVENTORY_CACHE
    scientific = [row for row in rows if row.classification == "SCIENTIFIC_PARAMETER"]
    invalid = [row for row in scientific if not (row.paper_name and row.paper_link and row.scientific_quote)]
    assert len(invalid) == 0


def test_engineering_assumptions_are_explicitly_classified():
    rows = _INVENTORY_CACHE
    engineering = [row for row in rows if row.classification == "ENGINEERING_PARAMETER"]
    assert engineering
    assert all(row.status in {"ENGINEERING_ASSUMPTION", "VALID"} for row in engineering)


def test_independent_replay_matches_production_result():
    trace = MathDebuggerRuntime().trace(_graph())
    replay = IndependentFormulaReplay().replay_all(trace.formula_traces)
    comparable = [item for item in replay if item.status != "SKIP"]
    assert comparable
    assert all(item.status == "MATCH" for item in comparable)


def test_formula_specs_exist_for_active_runtime_formulas():
    trace = MathDebuggerRuntime().trace(_graph())
    root = Path(__file__).resolve().parents[2]
    docs_text = (root / "docs" / "WAGGY_SYSTEM.md").read_text(encoding="utf-8")
    ids = {item.formula_id for item in trace.formula_traces}
    missing = [formula_id for formula_id in ids if formula_id not in docs_text]
    assert not missing, missing


def test_formula_trace_contains_equation_and_substitution():
    trace = MathDebuggerRuntime().trace(_graph())
    for formula in trace.formula_traces:
        assert formula.equation
        assert formula.substituted_equation


def test_constant_audit_detects_or_marks_constants():
    rows = FormulaConstantValidator().audit()
    assert isinstance(rows, tuple)
    assert all(row.classification for row in rows)


def test_replay_and_sensitivity_are_deterministic():
    trace = MathDebuggerRuntime().trace(_graph())
    replay = IndependentFormulaReplay()
    first = replay.replay_all(trace.formula_traces)
    second = replay.replay_all(trace.formula_traces)
    assert first == second
    sensitivity = SensitivityAnalyzer().analyze(trace.formula_traces[0])
    sensitivity_2 = SensitivityAnalyzer().analyze(trace.formula_traces[0])
    assert sensitivity == sensitivity_2


def test_audit_does_not_mutate_warehouse_facts():
    wh = WarehouseInterface()
    before = wh.load_all()
    before_fact_counts = {
        name: len(table["fact_id"].astype(str)) for name, table in before.items() if "fact_id" in table.columns
    }
    _ = MathDebuggerRuntime().trace(_graph())
    after = WarehouseInterface().load_all()
    after_fact_counts = {
        name: len(table["fact_id"].astype(str)) for name, table in after.items() if "fact_id" in table.columns
    }
    assert before_fact_counts == after_fact_counts


def test_agreement_edge_cases():
    engine = AgreementMathematicsEngine()
    observed_zero = ObservedEpidemiology("C1", "Condition", 0.0, 0)
    estimated_high = EstimatedEpidemiology("C1", "Condition", 20.0, 0.0, 0.0, 0.0, 1)
    result1 = engine.evaluate(observed_zero, estimated_high)
    assert result1.agreement_percent == 0.0

    observed_high = ObservedEpidemiology("C1", "Condition", 20.0, 1)
    estimated_zero = EstimatedEpidemiology("C1", "Condition", 0.0, 0.0, 0.0, 0.0, 1)
    result2 = engine.evaluate(observed_high, estimated_zero)
    assert result2.agreement_percent == 0.0

    both_zero = engine.evaluate(observed_zero, estimated_zero)
    assert both_zero.agreement_percent == 100.0

    equal_values = engine.evaluate(observed_high, EstimatedEpidemiology("C1", "Condition", 20.0, 0.0, 0.0, 0.0, 1))
    assert equal_values.agreement_percent == 100.0


def test_bayesian_helper_returns_bounded_percent():
    result = posterior_percent(prior_percent=18.0, evidence_percent=5.5, strength=0.4)
    assert 0.0 <= result <= 100.0
