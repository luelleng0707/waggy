"""Deterministic synthetic demo profiles for interview flow."""

from __future__ import annotations

from .models import AnalyzeDogRequest


SYNTHETIC_DEMO_PROFILES: dict[str, AnalyzeDogRequest] = {
    "golden_retriever": AnalyzeDogRequest(
        name="Demo Golden",
        primary_breed="Golden Retriever",
        age_years=4.0,
        birthday="2022-01-10",
        weight_kg=28.0,
        height_cm=58.0,
        sex="female",
        activity_level="Moderate",
        current_environment="Temperate Indoor",
        bcs=5.0,
        observed_conditions=("itching",),
    ),
    "husky": AnalyzeDogRequest(
        name="Demo Husky",
        primary_breed="Siberian Husky",
        age_years=3.5,
        birthday="2022-06-01",
        weight_kg=24.0,
        height_cm=57.0,
        sex="male",
        activity_level="High",
        current_environment="Cold Climate",
        bcs=4.5,
        observed_conditions=("shedding",),
    ),
    "mixed_lab_golden": AnalyzeDogRequest(
        name="Dolly",
        primary_breed="Labrador Retriever",
        secondary_breed="Golden Retriever",
        breed_split_pct=50.0,
        age_years=5.0,
        birthday="2021-04-15",
        weight_kg=30.0,
        height_cm=60.0,
        sex="female",
        activity_level="Moderate",
        current_environment="Temperate Outdoor",
        bcs=5.5,
        observed_conditions=("joint_stiffness", "itching"),
    ),
}
