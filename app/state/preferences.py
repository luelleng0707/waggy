"""Explicit preference persistence. Ambiguous language is not durable."""

from __future__ import annotations

from app.ai.feedback import is_ambiguous_preference
from app.ai.models import FeedbackCandidate, ProposedConstraints
from app.state.errors import DogStateError
from app.state.models import PreferenceRecord
from app.state.package_constraints import validate_preference_value
from app.state.store import get_dog, save_preference

_CATEGORY_FOR_FEEDBACK = {
    "budget": "budget",
    "monthly_budget": "budget",
    "ingredient_exclusion": "ingredient_exclusion",
    "ingredient": "ingredient_exclusion",
    "product_exclusion": "product_exclusion",
    "product_dislike": "product_dislike",
    "package_rejection": "package_rejection",
    "package_acceptance": "package_acceptance",
}


def persist_explicit_preference(
    dog_id: str,
    *,
    category: str,
    value: str,
    status: str = "EXPLICIT",
    source: str = "USER",
) -> PreferenceRecord:
    cleaned = validate_preference_value(category, value)
    if is_ambiguous_preference(cleaned) and category == "budget" and not any(ch.isdigit() for ch in cleaned):
        raise DogStateError("AMBIGUOUS_PREFERENCE", "ambiguous budget language is not durable", field="value")
    return save_preference(dog_id=dog_id, category=category, value=cleaned, status=status, source=source)


def persist_durable_feedback(
    dog_id: str | None,
    feedback: list[FeedbackCandidate],
    constraints: ProposedConstraints | None,
) -> list[PreferenceRecord]:
    if not dog_id or get_dog(dog_id) is None:
        return []
    saved: list[PreferenceRecord] = []
    if constraints and constraints.monthly_budget is not None:
        saved.append(
            persist_explicit_preference(
                dog_id,
                category="budget",
                value=str(constraints.monthly_budget),
            )
        )
    if constraints and constraints.ingredient_exclusion:
        for item in constraints.ingredient_exclusion:
            saved.append(
                persist_explicit_preference(
                    dog_id,
                    category="ingredient_exclusion",
                    value=str(item),
                )
            )
    for candidate in feedback:
        if not candidate.durable:
            continue
        category = _CATEGORY_FOR_FEEDBACK.get(candidate.category)
        if category is None:
            continue
        if any(item.category == category and item.value == candidate.value for item in saved):
            continue
        saved.append(
            persist_explicit_preference(
                dog_id,
                category=category,
                value=candidate.value,
            )
        )
    return saved


def preference_error_if_ambiguous(message: str, *, category: str | None = None) -> None:
    if category == "budget" and is_ambiguous_preference(message):
        raise DogStateError("AMBIGUOUS_PREFERENCE", "ambiguous preference is not durable", field="value")
