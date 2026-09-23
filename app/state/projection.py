"""Fail-closed projection: persistent dog → DogProfileInput.

Does not invent age, weight, breed, activity, or environment.
Does not copy warehouse science. Does not inject observation prose.
"""

from __future__ import annotations

from typing import Any

from app.agent.state import DogProfileInput
from app.api.payload_adapter import WorkbenchInputError, profile_from_workbench_body
from app.state.errors import DogStateError
from app.state.models import PersistentDog
from app.state.recalculation import recommendation_snapshot
from app.state.store import get_dog, preferences_for, require_dog


def dog_to_workbench_body(dog: PersistentDog) -> dict[str, Any]:
    body: dict[str, Any] = {
        "name": dog.name,
        "pet_name": dog.name,
        "observed_conditions": list(dog.observed_conditions or []),
    }
    if dog.breed_input_state:
        body["breed_input_state"] = dog.breed_input_state
    if dog.primary_breed:
        body["primary_breed"] = dog.primary_breed
        breeds = [dog.primary_breed]
        if dog.secondary_breed:
            body["secondary_breed"] = dog.secondary_breed
            breeds.append(dog.secondary_breed)
        body["breeds"] = breeds
    if dog.breed_split_pct is not None:
        body["breed_split_pct"] = dog.breed_split_pct
    if dog.birthday:
        body["birthday"] = dog.birthday
    if dog.age_years is not None:
        body["age_years"] = dog.age_years
    if dog.weight_kg is not None:
        body["weight"] = dog.weight_kg
        body["weight_kg"] = dog.weight_kg
    if dog.sex:
        body["sex"] = dog.sex
    if dog.activity_level:
        body["activity_level"] = dog.activity_level
    if dog.current_environment:
        body["current_environment"] = dog.current_environment
    if dog.height_cm is not None:
        body["height_cm"] = dog.height_cm
    if dog.bcs is not None:
        body["bcs"] = dog.bcs
    budget = dog.monthly_budget
    for pref in preferences_for(dog.dog_id):
        if pref.category == "budget" and pref.status == "EXPLICIT":
            try:
                budget = float(pref.value)
            except (TypeError, ValueError):
                continue
    if budget is not None:
        body["monthly_budget"] = budget
    return body


def project_to_dog_profile_input(dog_id: str) -> DogProfileInput:
    dog = require_dog(dog_id)
    try:
        return profile_from_workbench_body(dog_to_workbench_body(dog))
    except WorkbenchInputError as exc:
        raise DogStateError(
            "MISSING_REQUIRED_PROFILE_INPUT" if exc.error.code.value == "MISSING_REQUIRED_INPUT" else "INVALID_INPUT",
            exc.error.message,
            field=exc.field,
        ) from exc


def analysis_input_snapshot(profile: DogProfileInput) -> dict[str, Any]:
    return profile.model_dump(mode="json")


def result_digest(envelope: dict[str, Any]) -> dict[str, Any]:
    canonical = envelope.get("canonical") if isinstance(envelope.get("canonical"), dict) else envelope
    packages = ((canonical or {}).get("package_optimization") or {}).get("package_options") or {}
    digest_packages: dict[str, list[str]] = {}
    for tier, rows in packages.items():
        if not isinstance(rows, list):
            continue
        ids: list[str] = []
        for row in rows[:3]:
            if not isinstance(row, dict):
                continue
            for product in row.get("products") or []:
                if isinstance(product, dict) and product.get("product_id"):
                    ids.append(str(product["product_id"]))
        digest_packages[str(tier)] = ids
    findings = ((canonical or {}).get("scientific_analysis") or {}).get("findings") or []
    titles = [str(item.get("title")) for item in findings if isinstance(item, dict) and item.get("title")]
    return {
        "package_product_ids": digest_packages,
        "finding_titles": titles,
        "analysis_signature": envelope.get("analysis_signature") or (canonical or {}).get("analysis_id"),
        "recommendation_snapshot": recommendation_snapshot(envelope),
    }


def get_dog_or_none(dog_id: str | None) -> PersistentDog | None:
    if not dog_id or not str(dog_id).strip():
        return None
    return get_dog(str(dog_id).strip())
