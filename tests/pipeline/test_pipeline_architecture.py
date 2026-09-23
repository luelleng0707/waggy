from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import ast

from repository.models import (
    ConditionEvidence,
    DogProfile,
    EvidenceCollection,
    EvidenceChain,
    EvidenceEdge,
    EvidenceGraph,
    LifeStage,
    EvidenceNode,
    ResolvedEnvironment,
    ResolvedDog,
    ResolvedTraits,
    ScientificCitation,
    ValidationResult,
)
from repository.pipeline.orchestrator import PipelineOrchestrator
from repository.pipeline.stage_order import PIPELINE_STAGE_ORDER


def test_pipeline_order_is_canonical():
    assert PIPELINE_STAGE_ORDER == (
        "Dog Resolver",
        "Life Stage Resolver",
        "Environment Resolver",
        "Trait Resolver",
        "Observation Resolver",
        "Resolved Dog Validator",
        "Evidence Collector",
        "Evidence Graph Builder",
    )


def test_models_are_serializable_dataclasses():
    profile = DogProfile(dog_id="DOG001", name="Dolly", breeds=("Golden Retriever",))
    resolved = ResolvedDog(
        dog_id=profile.dog_id,
        breed="Golden Retriever",
        breed_id="BREED_X",
        date_of_birth="2020-01-01",
        age_days=100,
        age_months=3.2,
        age_years=0.27,
        weight=30.0,
        environment="Temperate",
        life_stage="Puppy",
    )
    stage = LifeStage(stage="Puppy")
    env = ResolvedEnvironment(
        environment_name="Temperate",
        city="Shanghai",
        country="CN",
        climate="Temperate",
        urbanicity="Urban",
        season="Summer",
        housing="Apartment",
        walking_environment="Pavement",
    )
    traits = ResolvedTraits(dog_id=profile.dog_id)
    evidence = ConditionEvidence(dog_id=profile.dog_id, condition_id="COND_X", condition_name="Example")
    collection = EvidenceCollection(dog_id=profile.dog_id, condition_evidence=(evidence,))
    graph = EvidenceGraph(dog_id=profile.dog_id)
    validation = ValidationResult(ok=True)
    citation = ScientificCitation(
        citation_id="CIT001",
        paper_name="paper",
        paper_link="https://example.org",
        scientific_quote="quote",
        fact_id="FACT_001",
    )
    node = EvidenceNode(
        node_id="NODE001",
        condition_id="COND_X",
        condition_name="Example",
        summary="summary",
    )
    edge = EvidenceEdge(
        edge_id="EDGE001",
        from_node_id="NODE_SRC",
        to_node_id="NODE001",
        evidence_type="trait",
        effect="positive",
        source_dataset="biology.trait_condition_associations",
    )
    chain = EvidenceChain(
        chain_id="CHAIN001",
        condition_id="COND_X",
        nodes=(node,),
        edges=(edge,),
    )
    # ensure plain data export
    assert asdict(profile)["dog_id"] == "DOG001"
    assert asdict(resolved)["dog_id"] == "DOG001"
    assert asdict(stage)["stage"] == "Puppy"
    assert asdict(env)["climate"] == "Temperate"
    assert asdict(traits)["dog_id"] == "DOG001"
    assert asdict(evidence)["condition_id"] == "COND_X"
    assert asdict(collection)["dog_id"] == "DOG001"
    assert asdict(graph)["dog_id"] == "DOG001"
    assert asdict(validation)["ok"] is True
    assert asdict(citation)["citation_id"] == "CIT001"
    assert asdict(chain)["chain_id"] == "CHAIN001"


def test_orchestrator_executes_all_stages_in_order():
    calls: list[str] = []

    class _DogResolver:
        def resolve(self, profile: DogProfile) -> ResolvedDog:
            calls.append("Dog Resolver")
            return ResolvedDog(
                dog_id=profile.dog_id,
                breed="Golden Retriever",
                breed_id="BREED_X",
                date_of_birth="2020-01-01",
                age_days=100,
                age_months=3.2,
                age_years=0.27,
                weight=30.0,
                environment="Temperate",
                life_stage="",
            )

    class _LifeStageResolver:
        def resolve(self, resolved_dog: ResolvedDog) -> LifeStage:
            calls.append("Life Stage Resolver")
            return LifeStage(stage="Puppy")

    class _EnvironmentResolver:
        def resolve(self, profile: DogProfile) -> ResolvedEnvironment:
            calls.append("Environment Resolver")
            return ResolvedEnvironment(
                environment_name="Temperate",
                city="",
                country="",
                climate="Temperate",
                urbanicity="",
                season="",
                housing="",
                walking_environment="",
            )

    class _TraitResolver:
        def resolve(self, resolved_dog: ResolvedDog) -> ResolvedTraits:
            calls.append("Trait Resolver")
            return ResolvedTraits(dog_id=resolved_dog.dog_id, traits=({"trait_name": "size", "trait_value": "Large"},))

    class _ObservationResolver:
        def merge(self, profile: DogProfile, resolved_traits: ResolvedTraits) -> ResolvedTraits:
            calls.append("Observation Resolver")
            return resolved_traits

    class _Validator:
        def validate(
            self,
            resolved_dog: ResolvedDog,
            environment: ResolvedEnvironment,
            traits: ResolvedTraits,
        ) -> ValidationResult:
            calls.append("Resolved Dog Validator")
            return ValidationResult(ok=True)

    class _EvidenceCollector:
        def collect(
            self,
            resolved_dog: ResolvedDog,
            life_stage: LifeStage,
            environment: ResolvedEnvironment,
            resolved_traits: ResolvedTraits,
        ) -> EvidenceCollection:
            calls.append("Evidence Collector")
            ce = ConditionEvidence(
                dog_id=resolved_traits.dog_id,
                condition_id="COND_X",
                condition_name="Example",
            )
            return EvidenceCollection(
                dog_id=resolved_traits.dog_id,
                condition_evidence=(ce,),
                collection_metadata={"evidence_row_count": "1"},
            )

    class _EvidenceGraphBuilder:
        def build(self, evidence_collection: EvidenceCollection) -> EvidenceGraph:
            calls.append("Evidence Graph Builder")
            return EvidenceGraph(dog_id=evidence_collection.dog_id)

    orchestrator = PipelineOrchestrator(
        dog_resolver=_DogResolver(),
        life_stage_resolver=_LifeStageResolver(),
        environment_resolver=_EnvironmentResolver(),
        trait_resolver=_TraitResolver(),
        observation_resolver=_ObservationResolver(),
        resolved_dog_validator=_Validator(),
        evidence_collector=_EvidenceCollector(),
        evidence_graph_builder=_EvidenceGraphBuilder(),
    )
    result = orchestrator.run(DogProfile(dog_id="DOG001", name="Dolly", breeds=("Golden Retriever",)))
    assert result.evidence_graph.dog_id == "DOG001"
    assert calls == list(PIPELINE_STAGE_ORDER)
    assert [s.stage_name for s in result.trace.stages] == list(PIPELINE_STAGE_ORDER)
    assert result.trace.stages[-2].evidence_collected_count == "1"


def test_warehouse_isolation_no_read_csv_outside_interface():
    root = Path(__file__).resolve().parents[2]
    allowed = (root / "repository" / "warehouse" / "warehouse_interface.py").resolve()
    known_noncanonical = {
        (root / "repository" / "validation" / "runtime.py").resolve(),
    }
    for path in (root / "repository").rglob("*.py"):
        if path.resolve() == allowed or path.resolve() in known_noncanonical:
            continue
        text = path.read_text(encoding="utf-8")
        assert "read_csv(" not in text, f"read_csv usage outside WarehouseInterface: {path}"


def test_dependency_direction_no_reverse_imports():
    root = Path(__file__).resolve().parents[2]
    warehouse_dir = root / "repository" / "warehouse"
    engine_dir = root / "repository" / "engine"
    api_dir = root / "repository" / "api"
    frontend_dir = root / "repository" / "frontend"

    def _imports(path: Path) -> list[str]:
        if path.suffix != ".py":
            return []
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
        return names

    for py in warehouse_dir.rglob("*.py"):
        for mod in _imports(py):
            assert not mod.startswith("repository.engine")
            assert not mod.startswith("repository.api")
            assert not mod.startswith("repository.frontend")

    for py in engine_dir.rglob("*.py"):
        for mod in _imports(py):
            assert not mod.startswith("repository.api")
            assert not mod.startswith("repository.frontend")

    # Historical repository/api and repository/frontend were archived to legacy/.
    # They are not part of the production path (app.api.main + waggy-frontend).
    assert not api_dir.exists()
    assert not frontend_dir.exists()
