from __future__ import annotations

from repository.models.runtime import DogProfile, ResolvedDog, ResolvedEnvironment, ResolvedTraits
from repository.pipeline.biological_runtime import (
    InMemoryEvidenceGraphBuilder,
    ScientificExplainabilityBuilder,
    WarehouseBackedDogResolver,
    WarehouseBackedEnvironmentResolver,
    WarehouseBackedEvidenceCollector,
    WarehouseBackedLifeStageResolver,
    WarehouseBackedObservationResolver,
    WarehouseBackedResolvedDogValidator,
    WarehouseBackedTraitResolver,
)
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


def test_dog_resolution():
    wh = WarehouseInterface()
    resolver = WarehouseBackedDogResolver(wh)
    out = resolver.resolve(_profile())
    assert out.breed == "Golden Retriever"
    assert out.breed_id.startswith("BREED_")
    assert out.age_days is not None and out.age_days > 0
    assert out.weight == 30.0


def test_life_stage_resolution():
    wh = WarehouseInterface()
    resolver = WarehouseBackedLifeStageResolver(wh)
    dog = ResolvedDog(
        dog_id="DOG001",
        breed="Golden Retriever",
        breed_id="BREED_4C2466ED",
        date_of_birth="2020-03-15",
        age_days=500,
        age_months=16.4,
        age_years=1.37,
        weight=30.0,
        environment="Temperate",
        life_stage="",
    )
    stage = resolver.resolve(dog)
    assert stage.stage in {"Puppy", "Young Adult", "Mature Adult", "Senior", "End of Life"}


def test_environment_resolution():
    wh = WarehouseInterface()
    resolver = WarehouseBackedEnvironmentResolver(wh)
    env = resolver.resolve(_profile())
    assert env.climate
    assert env.environment_name


def test_trait_resolution_and_observation_merge():
    wh = WarehouseInterface()
    trait_resolver = WarehouseBackedTraitResolver(wh)
    obs_resolver = WarehouseBackedObservationResolver()
    dog = ResolvedDog(
        dog_id="DOG001",
        breed="Golden Retriever",
        breed_id="BREED_4C2466ED",
        date_of_birth="2020-03-15",
        age_days=1000,
        age_months=32.8,
        age_years=2.74,
        weight=30.0,
        environment="Temperate",
        life_stage="",
    )
    traits = trait_resolver.resolve(dog)
    merged = obs_resolver.merge(_profile(), traits)
    names = {t["trait_name"] for t in merged.traits}
    assert "coat_type" in names
    assert "size" in names


def test_validator():
    wh = WarehouseInterface()
    validator = WarehouseBackedResolvedDogValidator(wh)
    dog = ResolvedDog(
        dog_id="DOG001",
        breed="Golden Retriever",
        breed_id="BREED_4C2466ED",
        date_of_birth="2020-03-15",
        age_days=1000,
        age_months=32.8,
        age_years=2.74,
        weight=30.0,
        environment="Temperate",
        life_stage="",
    )
    env = ResolvedEnvironment(
        environment_name="Temperate",
        city="",
        country="",
        climate="Temperate",
        urbanicity="",
        season="",
        housing="",
        walking_environment="",
    )
    traits = ResolvedTraits(
        dog_id="DOG001",
        traits=({"trait_name": "size", "trait_value": "Large", "status": "estimated"},),
    )
    out = validator.validate(dog, env, traits)
    assert out.ok is True


def test_evidence_collection_and_graph():
    wh = WarehouseInterface()
    dog_resolver = WarehouseBackedDogResolver(wh)
    life_stage_resolver = WarehouseBackedLifeStageResolver(wh)
    env_resolver = WarehouseBackedEnvironmentResolver(wh)
    trait_resolver = WarehouseBackedTraitResolver(wh)
    obs_resolver = WarehouseBackedObservationResolver()
    collector = WarehouseBackedEvidenceCollector(wh)
    graph_builder = InMemoryEvidenceGraphBuilder()
    explain_builder = ScientificExplainabilityBuilder()

    profile = _profile()
    dog = dog_resolver.resolve(profile)
    stage = life_stage_resolver.resolve(dog)
    env = env_resolver.resolve(profile)
    traits = obs_resolver.merge(profile, trait_resolver.resolve(dog))
    collection = collector.collect(dog, stage, env, traits)
    graph = graph_builder.build(collection)
    chain = explain_builder.build_chain(graph)

    assert len(collection.condition_evidence) > 0
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0
    assert chain.chain_id
