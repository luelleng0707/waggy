"""Ω11 semantic separation — statuses and domains must not collapse."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.contracts.agent.analysis import CanonicalAnalysis
from app.contracts.agent.bundles import BundleSearchResult
from app.contracts.agent.enums import (
    AvailabilityStatus,
    DomainKind,
    EvidenceStatus,
    InputState,
    ObserverRole,
)
from app.contracts.agent.evidence import ScientificEvidence, ScientificFact
from app.contracts.agent.health import HealthAnalysisResult
from app.contracts.agent.inference import PrevalenceValue, ScientificInference
from app.contracts.agent.input import CanonicalDogInput, provided, unknown
from app.contracts.agent.nutrition import NutritionAnalysisResult
from app.contracts.agent.observations import Observation
from app.contracts.agent.products import BusinessConfiguration, ProductIdentity, ProductRecord
from app.contracts.agent.report import ReportProjection
from app.contracts.agent.versions import VersionStamp


def test_unknown_is_not_zero():
    field = unknown()
    assert field.state == InputState.UNKNOWN
    assert field.value is None
    assert field.value != 0
    with pytest.raises(ValidationError):
        type(field)(state=InputState.UNKNOWN, value=0)


def test_not_available_prevalence_is_not_zero():
    missing = PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE)
    assert missing.percent is None
    assert missing.ratio is None
    assert missing.is_numeric is False
    present = PrevalenceValue(status=AvailabilityStatus.AVAILABLE, percent=12.7)
    assert present.percent != 0
    assert present.is_numeric is True


def test_needs_validation_is_not_approved():
    evidence = ScientificEvidence(status=EvidenceStatus.NEEDS_VALIDATION, paper_name="Example")
    assert evidence.status != EvidenceStatus.APPROVED
    fact = ScientificFact(
        subject="Example",
        relationship="prevalence",
        object="Example",
        status=EvidenceStatus.NEEDS_VALIDATION,
    )
    assert fact.is_scientifically_usable is False
    approved = fact.model_copy(update={"status": EvidenceStatus.APPROVED})
    assert approved.is_scientifically_usable is True
    assert fact.status != approved.status


def test_missing_provenance_is_not_approved():
    fact = ScientificFact(
        subject="Example",
        relationship="trait",
        object="Example",
        status=EvidenceStatus.MISSING_PROVENANCE,
    )
    assert fact.status != EvidenceStatus.APPROVED
    assert fact.is_scientifically_usable is False


def test_migrated_is_not_approved():
    fact = ScientificFact(
        subject="Example",
        relationship="prevalence",
        object="Example",
        status=EvidenceStatus.MIGRATED,
    )
    assert fact.status != EvidenceStatus.APPROVED
    assert fact.is_scientifically_usable is False


def test_observation_is_not_scientific_fact():
    obs = Observation(observer_role=ObserverRole.GROOMER, observation_type="coat_density", value="dense coat")
    fact = ScientificFact(
        subject="dog",
        relationship="has_trait",
        object="dense coat",
        status=EvidenceStatus.NOT_AVAILABLE,
    )
    assert obs.domain == DomainKind.OBSERVATION
    assert fact.domain == DomainKind.SCIENTIFIC_FACT
    assert obs.domain != fact.domain
    assert not hasattr(obs, "diagnosis")
    assert "diagnosis" not in obs.model_fields


def test_scientific_fact_is_not_inference():
    fact = ScientificFact(
        subject="Breed",
        relationship="prevalence",
        object="Condition",
        status=EvidenceStatus.WAREHOUSE_EVIDENCE,
    )
    inference = ScientificInference(
        inference_type="condition_priority",
        subject="Condition",
        result_status=EvidenceStatus.WAREHOUSE_EVIDENCE,
    )
    assert fact.domain != inference.domain


def test_product_fact_is_not_scientific_evidence():
    product = ProductRecord(identity=ProductIdentity(product_id="X", product_name="Y"))
    evidence = ScientificEvidence(status=EvidenceStatus.NEEDS_VALIDATION)
    assert product.domain == DomainKind.PRODUCT_FACT
    assert evidence.domain == DomainKind.SCIENTIFIC_EVIDENCE


def test_commercial_configuration_is_not_scientific_evidence():
    config = BusinessConfiguration(allowed_brands=["Brand A"])
    assert config.domain == DomainKind.COMMERCIAL_CONFIGURATION
    assert config.domain != DomainKind.SCIENTIFIC_EVIDENCE
    assert config.domain != DomainKind.SCIENTIFIC_FACT


def test_recommendation_and_report_projection_domains():
    versions = VersionStamp()
    health = HealthAnalysisResult(evidence_status=EvidenceStatus.NOT_AVAILABLE, versions=versions)
    nutrition = NutritionAnalysisResult(versions=versions)
    bundles = BundleSearchResult(versions=versions)
    dog = CanonicalDogInput(
        primary_breed=provided("Example"),
        age_years=provided(4.0),
        weight_kg=provided(18.0),
    )
    analysis = CanonicalAnalysis(dog=dog, health=health, nutrition=nutrition, bundles=bundles, versions=versions)
    assert health.domain == DomainKind.DERIVED_ANALYSIS
    assert nutrition.domain == DomainKind.DERIVED_ANALYSIS
    assert bundles.domain == DomainKind.DERIVED_ANALYSIS
    assert analysis.domain == DomainKind.DERIVED_ANALYSIS
    assert bundles.capability == "optimize_bundles"
    assert health.diagnosis_claim is False
    report = ReportProjection(versions=versions, analysis_id=None)
    assert report.domain == DomainKind.PROJECTION
    assert report.capability == "generate_report"


def test_canonical_input_rejects_demo_mode_and_hidden_session():
    assert "demo_mode" not in CanonicalDogInput.model_fields
    assert "groomer_session" not in CanonicalDogInput.model_fields
    with pytest.raises(ValidationError):
        CanonicalDogInput.model_validate({"demo_mode": True})


def test_budget_not_provided_is_not_zero():
    dog = CanonicalDogInput()
    assert dog.monthly_budget.state == InputState.NOT_PROVIDED
    assert dog.monthly_budget.value is None
    zero = CanonicalDogInput(monthly_budget=provided(0.0))
    assert zero.monthly_budget.state == InputState.PROVIDED
    assert zero.monthly_budget.value == 0.0
