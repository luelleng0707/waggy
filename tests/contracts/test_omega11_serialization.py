"""Ω11 contract serialization / deserialization."""

from __future__ import annotations

import json

from app.agent.version import ALGORITHM_VERSION
from app.contracts.agent.bundles import BundleOption, BundleSearchResult, OptimizerProvenance
from app.contracts.agent.context import AgentActor, AgentContext
from app.contracts.agent.enums import (
    ActorRole,
    AvailabilityStatus,
    BundleTier,
    EvidenceStatus,
    InputState,
    ObserverRole,
    ToolErrorCode,
)
from app.contracts.agent.errors import ToolError, missing_required_input
from app.contracts.agent.evidence import ScientificEvidence, ScientificFact
from app.contracts.agent.health import ConditionFinding, HealthAnalysisResult
from app.contracts.agent.inference import PrevalenceValue, ScientificInference
from app.contracts.agent.input import CanonicalDogInput, provided
from app.contracts.agent.nutrition import NutrientRequirement, NutritionAnalysisResult
from app.contracts.agent.observations import Observation
from app.contracts.agent.products import BusinessConfiguration, ProductIdentity, ProductRecord
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.report import ReportProjection
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION, VersionStamp


def _roundtrip(model):
    payload = model.model_dump(mode="json")
    text = json.dumps(payload)
    restored = type(model).model_validate_json(text)
    assert restored.model_dump(mode="json") == payload
    return restored


def test_canonical_dog_input_roundtrip():
    dog = CanonicalDogInput(
        name=provided("Dolly"),
        primary_breed=provided("Golden Retriever"),
        age_years=provided(5.2),
        weight_kg=provided(24.0),
        activity_level=provided("Moderate"),
        environment=provided("Temperate Indoor"),
    )
    restored = _roundtrip(dog)
    assert restored.primary_breed.value == "Golden Retriever"
    assert restored.monthly_budget.state == InputState.NOT_PROVIDED


def test_observation_roundtrip():
    obs = Observation(
        observer_role=ObserverRole.GROOMER,
        observation_type="coat_density",
        value="dense coat",
        dog_id="DOG::dolly",
    )
    assert _roundtrip(obs).domain.value == "OBSERVATION"


def test_scientific_evidence_and_fact_roundtrip():
    evidence = ScientificEvidence(
        paper_id="EXAMPLE_PAPER",
        paper_name="Example paper",
        paper_link="https://example.invalid/paper",
        publication_year="2021",
        scientific_quote="Example quote",
        status=EvidenceStatus.NEEDS_VALIDATION,
        warehouse_version="example",
    )
    fact = ScientificFact(
        fact_id="EXAMPLE_FACT",
        subject="Example Breed",
        relationship="prevalence",
        object="Example Condition",
        value=0.12,
        unit="ratio",
        status=EvidenceStatus.NEEDS_VALIDATION,
        evidence=[evidence],
    )
    assert _roundtrip(fact).status == EvidenceStatus.NEEDS_VALIDATION


def test_inference_product_business_roundtrip():
    inference = ScientificInference(
        inference_type="condition_priority",
        subject="Example Condition",
        result_status=EvidenceStatus.NOT_AVAILABLE,
        estimated_prevalence=PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE),
    )
    product = ProductRecord(
        identity=ProductIdentity(product_id="EXAMPLE_SKU", product_name="Example Food"),
    )
    config = BusinessConfiguration(allowed_brands=["Example Brand"])
    _roundtrip(inference)
    _roundtrip(product)
    _roundtrip(config)


def test_health_nutrition_bundle_provenance_version_error_roundtrip():
    versions = VersionStamp(
        engine_version=ALGORITHM_VERSION,
        warehouse_version="example",
        csv_hash="abc123",
        schema_version=AGENT_CONTRACT_SCHEMA_VERSION,
        tool_version="1.0.0",
    )
    health = HealthAnalysisResult(
        evidence_status=EvidenceStatus.NOT_AVAILABLE,
        versions=versions,
        findings=[
            ConditionFinding(
                condition="Example Condition",
                status=EvidenceStatus.NOT_AVAILABLE,
                observed_prevalence=PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE),
                estimated_prevalence=PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE),
            )
        ],
    )
    nutrition = NutritionAnalysisResult(
        versions=versions,
        nutrients=[
            NutrientRequirement(
                nutrient_id="protein_pct_dm",
                display="Protein",
                minimum=18.0,
                maximum=None,
                unit="% DM",
                basis="percent_dry_matter",
            )
        ],
    )
    bundles = BundleSearchResult(
        versions=versions,
        optimizer=OptimizerProvenance(llm_used=False),
        essential=[
            BundleOption(
                bundle_id="EXAMPLE_BUNDLE",
                tier=BundleTier.ESSENTIAL,
                product_ids=["EXAMPLE_SKU"],
                products=[ProductIdentity(product_id="EXAMPLE_SKU", product_name="Example Food")],
            )
        ],
    )
    provenance = ProvenanceRecord(
        source_type="paper",
        paper_id="EXAMPLE_PAPER",
        source_name="Example paper",
        source_link="https://example.invalid/paper",
        publication_year="2021",
        quote="Example quote",
        status=EvidenceStatus.NEEDS_VALIDATION,
        warehouse_version="example",
        engine_version=ALGORITHM_VERSION,
    )
    error = missing_required_input(["age_years"])
    actor = AgentContext(actor=AgentActor(actor_id="user-1", role=ActorRole.CUSTOMER))
    _roundtrip(health)
    _roundtrip(nutrition)
    _roundtrip(bundles)
    _roundtrip(provenance)
    _roundtrip(error)
    _roundtrip(versions)
    _roundtrip(actor)
    _roundtrip(ReportProjection(versions=versions))
    assert error.code == ToolErrorCode.MISSING_REQUIRED_INPUT
    parsed = ToolError.model_validate(error.model_dump(mode="json"))
    assert parsed.fields == ["age_years"]
