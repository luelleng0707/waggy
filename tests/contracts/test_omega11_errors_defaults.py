"""Ω11 typed errors and no silent defaults."""

from __future__ import annotations

import pytest

from app.contracts.agent.adapters import engine_profile_from_canonical
from app.contracts.agent.bundles import BundleSearchResult
from app.contracts.agent.enums import InputState, ToolErrorCode
from app.contracts.agent.errors import (
    ENGINE_NOT_AVAILABLE,
    ToolError,
    invalid_input,
    missing_required_input,
)
from app.contracts.agent.input import CanonicalDogInput, invalid, provided
from app.contracts.agent.versions import VersionStamp


def test_missing_required_input_codes():
    err = missing_required_input(["age_years", "weight_kg"])
    assert err.code == ToolErrorCode.MISSING_REQUIRED_INPUT
    assert "age_years" in err.fields


def test_invalid_input_code():
    err = invalid_input(["age_years"], message="age must be positive")
    assert err.code == ToolErrorCode.INVALID_INPUT


def test_not_available_and_evidence_codes():
    assert ToolError(code=ToolErrorCode.NOT_AVAILABLE, message="no prevalence").code.value == "NOT_AVAILABLE"
    assert ENGINE_NOT_AVAILABLE == "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE"
    assert ToolError(code=ToolErrorCode.MISSING_EVIDENCE, message="no paper").code == ToolErrorCode.MISSING_EVIDENCE
    assert ToolError(code=ToolErrorCode.NEEDS_VALIDATION, message="flagged").code == ToolErrorCode.NEEDS_VALIDATION
    assert ToolError(code=ToolErrorCode.MISSING_PROVENANCE, message="no cite").code == ToolErrorCode.MISSING_PROVENANCE


def test_product_and_bundle_and_warehouse_error_codes():
    assert ToolError(code=ToolErrorCode.NO_VALID_PRODUCTS, message="none").code == ToolErrorCode.NO_VALID_PRODUCTS
    assert ToolError(code=ToolErrorCode.NO_VALID_BUNDLES, message="none").code == ToolErrorCode.NO_VALID_BUNDLES
    assert ToolError(code=ToolErrorCode.WAREHOUSE_ERROR, message="io").code == ToolErrorCode.WAREHOUSE_ERROR
    empty = BundleSearchResult(versions=VersionStamp())
    assert empty.essential == []
    assert empty.balanced == []
    assert empty.optimal == []


def test_incomplete_dog_does_not_default_age_or_weight():
    dog = CanonicalDogInput()
    assert dog.age_years.state == InputState.NOT_PROVIDED
    assert dog.age_years.value is None
    assert dog.weight_kg.value is None
    assert dog.primary_breed.value is None
    assert dog.activity_level.value is None
    error = dog.validate_for_tools()
    assert error is not None
    assert error.code == ToolErrorCode.MISSING_REQUIRED_INPUT
    assert "age_years" in error.fields
    assert "weight_kg" in error.fields
    assert "primary_breed" in error.fields
    dumped = dog.model_dump(mode="json")
    assert dumped["age_years"]["value"] is None
    assert dumped["weight_kg"]["value"] is None
    assert dumped["age_years"]["value"] != 5
    assert dumped["weight_kg"]["value"] != 20


def test_unknown_age_is_missing_required_not_five():
    from app.contracts.agent.input import unknown

    dog = CanonicalDogInput(
        primary_breed=provided("Golden Retriever"),
        age_years=unknown(),
        weight_kg=provided(20.0),
    )
    error = dog.validate_for_tools()
    assert error is not None
    assert error.code == ToolErrorCode.MISSING_REQUIRED_INPUT
    assert dog.age_years.value is None


def test_invalid_field_is_invalid_input():
    dog = CanonicalDogInput(
        primary_breed=provided("Golden Retriever"),
        age_years=invalid(-1.0),
        weight_kg=provided(20.0),
    )
    error = dog.validate_for_tools()
    assert error is not None
    assert error.code == ToolErrorCode.INVALID_INPUT
    assert "age_years" in error.fields


def test_engine_adapter_refuses_silent_defaults():
    incomplete = CanonicalDogInput(primary_breed=provided("Golden Retriever"))
    with pytest.raises(ValueError, match="Missing required input"):
        engine_profile_from_canonical(incomplete)
    almost = CanonicalDogInput(
        name=provided("Dolly"),
        primary_breed=provided("Golden Retriever"),
        age_years=provided(5.0),
        weight_kg=provided(24.0),
        environment=provided("Temperate Indoor"),
        # activity omitted on purpose
    )
    with pytest.raises(ValueError, match="activity_level"):
        engine_profile_from_canonical(almost)


def test_engine_adapter_succeeds_only_with_explicit_fields():
    dog = CanonicalDogInput(
        name=provided("Dolly"),
        primary_breed=provided("Golden Retriever"),
        age_years=provided(5.2),
        weight_kg=provided(24.0),
        environment=provided("Temperate Indoor"),
        activity_level=provided("Moderate"),
    )
    profile = engine_profile_from_canonical(dog)
    assert profile.age_years == 5.2
    assert profile.weight_kg == 24.0
    assert profile.activity_level == "Moderate"
