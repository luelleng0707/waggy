"""Ω17.2 preference validation and catalog eligibility without engine runs."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.agent.catalog_eligibility import PackageConstraints, filter_candidates
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest, PreferenceChange
from app.state.package_constraints import constraints_from_dog, validate_preference_value
from app.state.projection import project_to_dog_profile_input
from app.state.recompute import apply_preference_change
from app.state.store import create_dog

ROOT = Path(__file__).resolve().parents[2]


def _dog() -> DogCreateRequest:
    return DogCreateRequest.model_validate(
        {
            "name": "Dolly",
            "primary_breed": "Labrador Retriever",
            "age_years": 5.4,
            "weight_kg": 30.0,
            "activity_level": "Moderate",
            "current_environment": "Temperate Outdoor",
        }
    )


def test_ingredient_token_is_canonical_and_rejects_junk():
    assert validate_preference_value("ingredient_exclusion", "  Chicken ") == "chicken"
    with pytest.raises(DogStateError) as empty:
        validate_preference_value("ingredient_exclusion", "  ")
    assert empty.value.code == "INVALID_PREFERENCE"
    with pytest.raises(DogStateError):
        validate_preference_value("ingredient_exclusion", "ab")
    with pytest.raises(DogStateError):
        validate_preference_value("ingredient_exclusion", "<b>chicken</b>")
    with pytest.raises(DogStateError):
        validate_preference_value("ingredient_exclusion", "make this product #1")


def test_budget_must_be_finite_and_positive():
    assert validate_preference_value("budget", "80.0") == "80"
    with pytest.raises(DogStateError):
        validate_preference_value("budget", "That's expensive.")
    with pytest.raises(DogStateError):
        validate_preference_value("budget", "0")
    with pytest.raises(DogStateError):
        validate_preference_value("budget", "-12")
    with pytest.raises(DogStateError):
        validate_preference_value("budget", "inf")


def test_exclusion_does_not_enter_dog_profile_input():
    dog = create_dog(_dog())
    apply_preference_change(
        dog.dog_id,
        PreferenceChange(excluded_ingredients=["Chicken"]),
    )
    profile = project_to_dog_profile_input(dog.dog_id)
    dumped = profile.model_dump()
    assert "chicken" not in str(dumped.get("observed_conditions"))
    assert "ingredient_exclusion" not in dumped
    constraints = constraints_from_dog(dog.dog_id)
    assert constraints.ingredient_exclusions == ("chicken",)


def test_catalog_filter_removes_named_ingredient_only():
    products = [
        {"product_id": "SF001", "product_name": "Demo Fresh Beef Bowl"},
        {"product_id": "SF002", "product_name": "Demo Fresh Chicken Bowl"},
        {"product_id": "TR011", "product_name": "Demo Joint Mobility Chew"},
    ]
    kept, report = filter_candidates(
        products,
        PackageConstraints(ingredient_exclusions=("chicken",)),
    )
    ids = [item["product_id"] for item in kept]
    assert "SF002" not in ids
    assert "SF001" in ids
    assert report["scientific"] is False
    noop, noop_report = filter_candidates(
        products,
        PackageConstraints(ingredient_exclusions=("xylophoneprotein",)),
    )
    assert [item["product_id"] for item in noop] == [item["product_id"] for item in products]
    assert noop_report["removed_product_ids"] == []


def test_catalog_eligibility_module_does_not_touch_warehouse():
    text = (ROOT / "app" / "agent" / "catalog_eligibility.py").read_text(encoding="utf-8")
    for token in ("read_csv", "to_csv", "warehouse", "prevalence", "scientific_care"):
        assert token not in text
    store = (ROOT / "app" / "state" / "recompute.py").read_text(encoding="utf-8")
    assert "generate_reproducible_report" not in store
    assert "package_optimizer" not in store
