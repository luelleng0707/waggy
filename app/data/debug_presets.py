"""Developer-only DogProfile presets for Validation Console (no clinical math)."""

from __future__ import annotations

from typing import Any

# Request bodies compatible with profile_from_analyze_body / analyze API.
PRESETS: dict[str, dict[str, Any]] = {
    "golden_retriever": {
        "id": "golden_retriever",
        "label": "Golden Retriever",
        "description": "Adult Golden, 28 kg, moderate activity",
        "body": {
            "name": "Sunny",
            "pet_name": "Sunny",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 28,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "german_shepherd": {
        "id": "german_shepherd",
        "label": "German Shepherd",
        "description": "Working-line adult, high activity",
        "body": {
            "name": "Rex",
            "pet_name": "Rex",
            "breeds": ["German Shepherd Dog"],
            "birthday": "2019-04-12",
            "weight": 34,
            "sex": "Male",
            "activity_level": "High",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "border_collie": {
        "id": "border_collie",
        "label": "Border Collie",
        "description": "High-drive herding breed",
        "body": {
            "name": "Pip",
            "pet_name": "Pip",
            "breeds": ["Border Collie"],
            "birthday": "2021-01-20",
            "weight": 18,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Rural Cool",
            "observed_conditions": [],
        },
    },
    "french_bulldog": {
        "id": "french_bulldog",
        "label": "French Bulldog",
        "description": "Brachycephalic companion breed",
        "body": {
            "name": "Biscuit",
            "pet_name": "Biscuit",
            "breeds": ["French Bulldog"],
            "birthday": "2022-08-08",
            "weight": 12,
            "sex": "Male",
            "activity_level": "Low",
            "current_environment": "Urban Indoor",
            "observed_conditions": [],
        },
    },
    "mixed_breed": {
        "id": "mixed_breed",
        "label": "Mixed Breed",
        "description": "Dolly — Golden × Labrador (default demo)",
        "body": {
            "name": "Dolly",
            "pet_name": "Dolly",
            "breeds": ["Golden Retriever", "Labrador Retriever"],
            "birthday": "2021-03-15",
            "weight": 30,
            "sex": "Female",
            "activity_level": "High",
            "current_environment": "Shanghai Summer",
            "observed_conditions": [],
        },
    },
    "senior_labrador": {
        "id": "senior_labrador",
        "label": "Senior Labrador",
        "description": "Aging Labrador, lower activity",
        "body": {
            "name": "Maple",
            "pet_name": "Maple",
            "breeds": ["Labrador Retriever"],
            "birthday": "2013-05-01",
            "weight": 32,
            "sex": "Female",
            "activity_level": "Low",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "large_breed_puppy": {
        "id": "large_breed_puppy",
        "label": "Large Breed Puppy",
        "description": "Growing Golden puppy",
        "body": {
            "name": "Scout",
            "pet_name": "Scout",
            "breeds": ["Golden Retriever"],
            "birthday": "2025-09-01",
            "weight": 14,
            "sex": "Male",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "golden_20kg": {
        "id": "golden_20kg",
        "label": "Golden @ 20 kg",
        "description": "Compare preset A — lighter Golden",
        "body": {
            "name": "CompareA",
            "pet_name": "CompareA",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 20,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
    "golden_25kg": {
        "id": "golden_25kg",
        "label": "Golden @ 25 kg",
        "description": "Compare preset B — heavier Golden",
        "body": {
            "name": "CompareB",
            "pet_name": "CompareB",
            "breeds": ["Golden Retriever"],
            "birthday": "2020-06-01",
            "weight": 25,
            "sex": "Female",
            "activity_level": "Moderate",
            "current_environment": "Temperate Suburban",
            "observed_conditions": [],
        },
    },
}

DEFAULT_PRESET_ID = "mixed_breed"


def list_presets() -> list[dict[str, Any]]:
    return [
        {
            "id": p["id"],
            "label": p["label"],
            "description": p["description"],
        }
        for p in PRESETS.values()
    ]


def get_preset_body(preset_id: str) -> dict[str, Any]:
    key = (preset_id or DEFAULT_PRESET_ID).strip().lower()
    if key not in PRESETS:
        raise KeyError(f"Unknown preset: {preset_id}")
    return dict(PRESETS[key]["body"])
