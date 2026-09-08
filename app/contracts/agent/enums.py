"""Shared enumerations. Reuse warehouse/engine tokens where they already exist."""

from __future__ import annotations

from enum import StrEnum


class InputState(StrEnum):
    PROVIDED = "PROVIDED"
    UNKNOWN = "UNKNOWN"
    NOT_PROVIDED = "NOT_PROVIDED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID = "INVALID"


class EvidenceStatus(StrEnum):
    """Scientific-use status.

    APPROVED is a contract state for validated-for-use facts. The current
    warehouse does not label rows APPROVED. Do not map migrated → APPROVED.
    """

    APPROVED = "APPROVED"
    NEEDS_VALIDATION = "NEEDS_VALIDATION"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    WAREHOUSE_EVIDENCE = "WAREHOUSE_EVIDENCE"
    MIGRATED = "migrated"
    NOT_MODELED = "NOT_MODELED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class AvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class DomainKind(StrEnum):
    USER_INPUT = "USER_INPUT"
    OBSERVATION = "OBSERVATION"
    SCIENTIFIC_EVIDENCE = "SCIENTIFIC_EVIDENCE"
    SCIENTIFIC_FACT = "SCIENTIFIC_FACT"
    SCIENTIFIC_INFERENCE = "SCIENTIFIC_INFERENCE"
    PRODUCT_FACT = "PRODUCT_FACT"
    COMMERCIAL_CONFIGURATION = "COMMERCIAL_CONFIGURATION"
    DERIVED_ANALYSIS = "DERIVED_ANALYSIS"
    RECOMMENDATION = "RECOMMENDATION"
    PROJECTION = "PROJECTION"
    ANALYTICS = "ANALYTICS"


class ObserverRole(StrEnum):
    CUSTOMER = "customer"
    GROOMER = "groomer"
    SYSTEM = "system"


class ActorRole(StrEnum):
    CUSTOMER = "customer"
    GROOMER = "groomer"
    BUSINESS = "business"
    SCIENCE = "science"
    DEVELOPER = "developer"
    AI_AGENT = "ai_agent"


class OperationType(StrEnum):
    READ = "read"
    CALCULATE = "calculate"
    READ_CALCULATE = "read_calculate"
    PROJECTION = "projection"
    WRITE = "write"


class ToolErrorCode(StrEnum):
    MISSING_REQUIRED_INPUT = "MISSING_REQUIRED_INPUT"
    INVALID_INPUT = "INVALID_INPUT"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    NEEDS_VALIDATION = "NEEDS_VALIDATION"
    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    NO_VALID_PRODUCTS = "NO_VALID_PRODUCTS"
    NO_VALID_BUNDLES = "NO_VALID_BUNDLES"
    WAREHOUSE_ERROR = "WAREHOUSE_ERROR"


class BundleTier(StrEnum):
    ESSENTIAL = "essential"
    BALANCED = "balanced"
    OPTIMAL = "optimal"
