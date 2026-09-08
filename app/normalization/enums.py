"""Ω12 lookup kinds and mapping statuses. Reuses Ω11 DomainKind on results."""

from __future__ import annotations

from enum import StrEnum

from app.contracts.agent.enums import DomainKind


class MappingStatus(StrEnum):
    RESOLVED = "RESOLVED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"
    MIXED = "MIXED"


class EntityKind(StrEnum):
    BREED = "breed"
    CONDITION = "condition"
    PRODUCT = "product"
    BRAND = "brand"
    OBSERVATION = "observation"
    SEX = "sex"
    AGE_YEARS = "age_years"
    WEIGHT_KG = "weight_kg"


ENTITY_TO_DOMAIN: dict[EntityKind, DomainKind] = {
    EntityKind.BREED: DomainKind.USER_INPUT,
    EntityKind.CONDITION: DomainKind.USER_INPUT,
    EntityKind.PRODUCT: DomainKind.PRODUCT_FACT,
    EntityKind.BRAND: DomainKind.COMMERCIAL_CONFIGURATION,
    EntityKind.OBSERVATION: DomainKind.OBSERVATION,
    EntityKind.SEX: DomainKind.USER_INPUT,
    EntityKind.AGE_YEARS: DomainKind.USER_INPUT,
    EntityKind.WEIGHT_KG: DomainKind.USER_INPUT,
}

FORBIDDEN_RESULT_DOMAINS = frozenset(
    {
        DomainKind.SCIENTIFIC_EVIDENCE,
        DomainKind.SCIENTIFIC_FACT,
        DomainKind.SCIENTIFIC_INFERENCE,
        DomainKind.DERIVED_ANALYSIS,
        DomainKind.RECOMMENDATION,
        DomainKind.PROJECTION,
        DomainKind.ANALYTICS,
    }
)
