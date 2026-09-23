"""Validated preference change → new analysis. Does not mutate completed analyses."""

from __future__ import annotations

from typing import Any

from app.agent.catalog_eligibility import PackageConstraints
from app.agent.state import DogProfileInput
from app.state.errors import DogStateError
from app.state.models import PreferenceChange, PreferenceRecord
from app.state.package_constraints import (
    canonical_budget_text,
    constraints_from_dog,
    overlay_budget,
    validate_preference_value,
)
from app.state.preferences import persist_explicit_preference
from app.state.projection import analysis_input_snapshot, project_to_dog_profile_input
from app.state.store import analyses_for, preferences_for, require_dog


def latest_analysis(dog_id: str):
    rows = analyses_for(dog_id)
    return rows[-1] if rows else None


def apply_preference_change(
    dog_id: str,
    change: PreferenceChange | None,
    *,
    source: str = "USER",
) -> tuple[list[PreferenceRecord], PackageConstraints, PackageConstraints, list[dict[str, Any]]]:
    require_dog(dog_id)
    before = constraints_from_dog(dog_id)
    saved: list[PreferenceRecord] = []
    changed: list[dict[str, Any]] = []
    if change is None:
        after = constraints_from_dog(dog_id)
        return saved, before, after, changed
    if change.excluded_ingredients is not None:
        if not isinstance(change.excluded_ingredients, list):
            raise DogStateError(
                "INVALID_PREFERENCE",
                "excluded_ingredients must be a list",
                field="excluded_ingredients",
            )
        if not change.excluded_ingredients:
            raise DogStateError(
                "INVALID_PREFERENCE",
                "excluded_ingredients must not be empty",
                field="excluded_ingredients",
            )
        current = {item.value for item in preferences_for(dog_id) if item.category == "ingredient_exclusion" and not item.superseded}
        for raw in change.excluded_ingredients:
            if not isinstance(raw, str):
                raise DogStateError(
                    "INVALID_PREFERENCE",
                    "excluded_ingredients must be a list of strings",
                    field="excluded_ingredients",
                )
            token = validate_preference_value("ingredient_exclusion", raw)
            if token in current:
                changed.append({"category": "ingredient_exclusion", "value": token, "action": "unchanged"})
                continue
            record = persist_explicit_preference(
                dog_id,
                category="ingredient_exclusion",
                value=token,
                source=source,
            )
            saved.append(record)
            current.add(token)
            changed.append({"category": "ingredient_exclusion", "value": record.value, "action": "added"})
    if change.monthly_budget is not None:
        token = validate_preference_value("budget", canonical_budget_text(float(change.monthly_budget)))
        record = persist_explicit_preference(
            dog_id,
            category="budget",
            value=token,
            source=source,
        )
        saved.append(record)
        changed.append({"category": "budget", "value": record.value, "action": "replaced"})
    after = constraints_from_dog(dog_id)
    return saved, before, after, changed


def effective_profile(dog_id: str, constraints: PackageConstraints) -> DogProfileInput:
    profile = project_to_dog_profile_input(dog_id)
    return overlay_budget(profile, constraints)


def effective_input_snapshot(profile: DogProfileInput, constraints: PackageConstraints) -> dict[str, Any]:
    payload = analysis_input_snapshot(profile)
    payload["package_constraints"] = constraints.as_dict()
    return payload


def require_expected_signature(dog_id: str, expected: str | None) -> None:
    if not expected:
        return
    current = latest_analysis(dog_id)
    actual = current.analysis_signature if current else None
    if actual != expected:
        raise DogStateError(
            "ANALYSIS_STALE",
            "expected_analysis_signature does not match the latest stored analysis",
            field="expected_analysis_signature",
            status=409,
        )
