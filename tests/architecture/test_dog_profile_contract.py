from __future__ import annotations

from dataclasses import asdict

import pytest
from pydantic import ValidationError

from app.agent.state import DogProfileInput
from app.api.payload_adapter import profile_from_analyze_body
from repository.models.runtime import DogProfile


def _to_repository_profile(profile: DogProfileInput) -> DogProfile:
    breeds = [profile.primary_breed]
    if profile.secondary_breed:
        breeds.append(profile.secondary_breed)
    return DogProfile(
        dog_id=f"DOG::{profile.name.lower()}",
        name=profile.name,
        breeds=tuple(breeds),
        age_years=profile.age_years,
        date_of_birth=profile.birthday or "",
        weight_kg=profile.weight_kg,
        sex=profile.sex or profile.gender or "",
        activity_level=profile.activity_level,
        environment=profile.current_environment,
        observed_conditions=tuple(profile.observed_conditions),
    )


def test_app_profile_contract_enforces_positive_age_and_weight():
    with pytest.raises(ValidationError):
        DogProfileInput(
            name="x",
            primary_breed="Breed",
            age_years=0,
            weight_kg=10.0,
            current_environment="Temperate",
        )
    with pytest.raises(ValidationError):
        DogProfileInput(
            name="x",
            primary_breed="Breed",
            age_years=2.0,
            weight_kg=0,
            current_environment="Temperate",
        )


def test_app_to_repository_contract_mapping_preserves_core_identity():
    app_profile = profile_from_analyze_body(
        {
            "pet_name": "Dolly",
            "breeds": ["Golden Retriever", "Labrador Retriever"],
            "breed_split_pct": 50.0,
            "birthday": "2021-03-15",
            "weight": 24.5,
            "environment": "Shanghai Summer",
            "observed_conditions": ["itching", "joint_stiffness"],
        }
    )
    repo_profile = _to_repository_profile(app_profile)
    payload = asdict(repo_profile)
    assert payload["name"] == "Dolly"
    assert payload["breeds"] == ("Golden Retriever", "Labrador Retriever")
    assert payload["date_of_birth"] == "2021-03-15"
    assert payload["weight_kg"] == 24.5
    assert payload["environment"] == "Shanghai Summer"
    assert payload["observed_conditions"] == ("itching", "joint_stiffness")


def test_repository_profile_is_immutable_domain_shape():
    profile = DogProfile(dog_id="DOG001", name="Dolly")
    with pytest.raises(Exception):
        profile.name = "New Name"  # type: ignore[misc]


def test_lossy_fields_are_explicitly_identified_for_adapter_gate():
    app_profile = DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=35.0,
        age_years=5.2,
        weight_kg=21.0,
        current_environment="Urban",
        sex="female",
        gender="female",
        height_cm=53.0,
        bcs=5.0,
        observed_conditions=["dry_skin"],
    )
    repo_profile = _to_repository_profile(app_profile)
    repo_fields = set(asdict(repo_profile).keys())
    assert "breed_split_pct" not in repo_fields
    assert "height_cm" not in repo_fields
    assert "bcs" not in repo_fields
