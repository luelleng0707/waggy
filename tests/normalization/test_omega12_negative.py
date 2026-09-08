"""Ω12 negative / fail-closed cases. Resolution is not a goal; safety is."""

from __future__ import annotations

from app.contracts.agent.enums import DomainKind
from app.normalization.enums import FORBIDDEN_RESULT_DOMAINS, EntityKind, MappingStatus
from app.normalization.resolver import resolve_raw

LABRADOR = "BREED_B02F1BE9"
HIP_DYSPLASIA = "COND_653473C1"


def test_unknown_condition():
    result = resolve_raw("quantum paw fever", EntityKind.CONDITION)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id is None


def test_unknown_product():
    result = resolve_raw("Example Omega Supplement", EntityKind.PRODUCT)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id is None


def test_unsupported_alias_shepherd_alone():
    result = resolve_raw("shepherd", EntityKind.BREED)
    assert result.status != MappingStatus.RESOLVED
    assert result.canonical_id is None


def test_dog_token_is_ambiguous():
    result = resolve_raw("dog", EntityKind.BREED)
    assert result.status == MappingStatus.AMBIGUOUS
    assert len(result.candidates) >= 2
    assert result.canonical_id is None


def test_claim_is_not_a_condition_alias():
    result = resolve_raw("high risk of hip dysplasia", EntityKind.CONDITION)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id != HIP_DYSPLASIA
    assert result.canonical_id is None


def test_claim_is_not_a_breed():
    result = resolve_raw("high risk of hip dysplasia", EntityKind.BREED)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id is None


def test_observation_claim_does_not_become_otitis():
    observation = resolve_raw("itchy ears means otitis", EntityKind.OBSERVATION)
    condition = resolve_raw("itchy ears means otitis", EntityKind.CONDITION)
    assert observation.status == MappingStatus.UNRESOLVED
    assert condition.status == MappingStatus.UNRESOLVED
    assert observation.canonical_id is None
    assert condition.canonical_id is None
    assert observation.domain_kind == DomainKind.OBSERVATION


def test_product_efficacy_copy_is_not_a_product_or_claim():
    result = resolve_raw(
        "Omega supplement proven to prevent joint disease",
        EntityKind.PRODUCT,
    )
    assert result.status == MappingStatus.UNRESOLVED
    dumped = result.to_json_dict()
    assert "efficacy" not in dumped
    assert result.domain_kind != DomainKind.SCIENTIFIC_EVIDENCE
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT


def test_labrador_as_condition_stays_unresolved():
    result = resolve_raw("Labrador Retriever", EntityKind.CONDITION)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.entity_kind == EntityKind.CONDITION


def test_observation_does_not_become_recommendation():
    result = resolve_raw("very dense coat", EntityKind.OBSERVATION)
    assert result.domain_kind == DomainKind.OBSERVATION
    assert result.domain_kind != DomainKind.RECOMMENDATION
    assert result.domain_kind not in FORBIDDEN_RESULT_DOMAINS


def test_incomplete_observation():
    result = resolve_raw("coat is", EntityKind.OBSERVATION)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.canonical_id is None


def test_mixed_with_unknown_component_still_not_a_breed_id():
    result = resolve_raw("Labrador x fluffster", EntityKind.BREED)
    assert result.status == MappingStatus.MIXED
    assert result.canonical_id is None
    assert result.components[0].canonical_id == LABRADOR
    assert result.components[1].status == MappingStatus.UNRESOLVED


def test_retriever_must_not_pick_labrador():
    result = resolve_raw("retriever", EntityKind.BREED)
    assert result.status == MappingStatus.AMBIGUOUS
    assert result.canonical_id != LABRADOR


def test_invalid_domain_conversion_product_claim_as_condition():
    result = resolve_raw("Farmina Small Breed Adult Dog Food (Chicken Flavor)", EntityKind.CONDITION)
    assert result.status == MappingStatus.UNRESOLVED
    assert result.entity_kind == EntityKind.CONDITION
    assert result.domain_kind == DomainKind.USER_INPUT


def test_brand_approval_is_not_scientific_recommendation():
    result = resolve_raw("Farmina", EntityKind.BRAND)
    assert result.status == MappingStatus.RESOLVED
    assert result.domain_kind == DomainKind.COMMERCIAL_CONFIGURATION
    assert result.domain_kind != DomainKind.RECOMMENDATION
    assert result.domain_kind != DomainKind.SCIENTIFIC_FACT


def test_punctuation_collision_xy_vs_x_hyphen_y():
    left = resolve_raw("X-Y", EntityKind.PRODUCT)
    right = resolve_raw("XY", EntityKind.PRODUCT)
    assert left.status == MappingStatus.UNRESOLVED
    assert right.status == MappingStatus.UNRESOLVED
    assert left.normalized_value != right.normalized_value
