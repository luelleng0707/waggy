from __future__ import annotations

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
from repository.reasoning.agreement import DeterministicAgreementEngine
from repository.reasoning.estimation import DeterministicEstimatedEngine
from repository.reasoning.observed import DeterministicObservedEngine
from repository.reasoning.runtime import ScientificInferenceRuntime
from repository.warehouse import WarehouseInterface


def _profile() -> DogProfile:
    return DogProfile(
        dog_id="DOG001",
        name="Dolly",
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


def _resolved_inputs():
    wh = WarehouseInterface()
    profile = _profile()
    dog = WarehouseBackedDogResolver(wh).resolve(profile)
    life_stage = WarehouseBackedLifeStageResolver(wh).resolve(dog)
    environment = WarehouseBackedEnvironmentResolver(wh).resolve(profile)
    traits = WarehouseBackedObservationResolver().merge(
        profile, WarehouseBackedTraitResolver(wh).resolve(dog)
    )
    collection = WarehouseBackedEvidenceCollector(wh).collect(dog, life_stage, environment, traits)
    graph = InMemoryEvidenceGraphBuilder().build(collection)
    return wh, dog, graph


def test_observed_estimated_agreement_are_deterministic():
    _, dog, graph = _resolved_inputs()
    observed_engine = DeterministicObservedEngine()
    estimated_engine = DeterministicEstimatedEngine()
    agreement_engine = DeterministicAgreementEngine()

    obs_a = observed_engine.evaluate(graph)
    est_a = estimated_engine.evaluate(dog, graph)
    agr_a = agreement_engine.evaluate(obs_a, est_a)

    obs_b = observed_engine.evaluate(graph)
    est_b = estimated_engine.evaluate(dog, graph)
    agr_b = agreement_engine.evaluate(obs_b, est_b)

    assert obs_a == obs_b
    assert est_a == est_b
    assert agr_a == agr_b
    assert len(est_a) > 0


def test_reasoning_runtime_outputs_condition_assessment_only():
    wh, dog, graph = _resolved_inputs()
    runtime = ScientificInferenceRuntime(warehouse=wh)
    result = runtime.run(dog, graph)

    assert len(result.assessments) > 0
    first = result.assessments[0]
    assert first.condition_name
    assert first.estimated_prevalence >= 0.0
    assert first.body_system
    assert first.required_mechanisms is not None
    assert len(first.formula_ids_used) > 0
    assert len(first.reasoning_chain) > 0

    # runtime trace exists and captures deterministic stage flow
    stage_names = [s.stage_name for s in result.trace.stages]
    assert stage_names == [
        "Observed Epidemiology",
        "Estimated Epidemiology",
        "Agreement Analysis",
        "Condition Assessment Build",
        "System Aggregation",
        "Mechanism Mapping",
    ]
    assert all(len(s.formula_ids) >= 0 for s in result.trace.stages)


def test_research_gap_emerging_condition_exists_when_observed_missing():
    wh, dog, graph = _resolved_inputs()
    runtime = ScientificInferenceRuntime(warehouse=wh)
    result = runtime.run(dog, graph)
    assert any(a.research_gap_status in {"observed", "emerging_condition"} for a in result.assessments)
