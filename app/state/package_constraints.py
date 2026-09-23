"""Commercial package constraints from persisted dog preferences.

Not scientific facts. Not DogProfileInput fields. Not warehouse writes.
Ingredient/product exclusions constrain catalog eligibility only.
Budget remains the existing DogProfileInput.monthly_budget commercial field.
"""

from __future__ import annotations

import math
import re
from typing import Any

from app.agent.catalog_eligibility import (
    PackageConstraints,
    apply_active_constraints,
    candidate_excluded,
    filter_candidates,
    using_package_constraints,
)
from app.agent.state import DogProfileInput
from app.ai.feedback import is_ambiguous_preference
from app.state.errors import DogStateError
from app.state.models import PreferenceRecord
from app.state.store import preferences_for

CANONICAL_PACKAGE_CATEGORIES = ("essential", "balanced", "optimal")
CANONICAL_CATEGORY_DISPLAY = {
    "essential": "Essential Care",
    "balanced": "Balanced Care",
    "optimal": "Optimal Care",
}

_ELIGIBILITY_CATEGORIES = frozenset(
    {"ingredient_exclusion", "product_exclusion", "product_dislike"}
)
_RANKING_LANGUAGE = re.compile(
    r"make this product|#\s*1|rank this|optimizer instruction|become number one",
    re.IGNORECASE,
)
_HTML_MARK = re.compile(r"<|>|javascript:", re.IGNORECASE)


def canonical_exclusion_token(value: str) -> str:
    return " ".join(str(value or "").split()).casefold()


def canonical_budget_text(amount: float) -> str:
    if amount == int(amount):
        return str(int(amount))
    return format(amount, ".10g")


def validate_preference_value(category: str, value: str) -> str:
    cleaned = " ".join(str(value or "").split())
    if not cleaned:
        raise DogStateError("INVALID_PREFERENCE", "preference value is required", field="value")
    if _HTML_MARK.search(cleaned):
        raise DogStateError("INVALID_PREFERENCE", "HTML is not a preference", field="value")
    if _RANKING_LANGUAGE.search(cleaned):
        raise DogStateError(
            "INVALID_PREFERENCE",
            "package ranking instructions are not preferences",
            field="value",
        )
    if category == "budget":
        if is_ambiguous_preference(cleaned) and not any(ch.isdigit() for ch in cleaned):
            raise DogStateError(
                "AMBIGUOUS_PREFERENCE",
                "ambiguous budget language is not durable",
                field="value",
            )
        try:
            amount = float(cleaned)
        except (TypeError, ValueError) as exc:
            raise DogStateError(
                "INVALID_PREFERENCE",
                "explicit budget must be a number",
                field="value",
            ) from exc
        if not math.isfinite(amount) or amount <= 0:
            raise DogStateError("INVALID_PREFERENCE", "budget must be a finite number > 0", field="value")
        return canonical_budget_text(amount)
    if category in _ELIGIBILITY_CATEGORIES:
        token = canonical_exclusion_token(cleaned)
        if len(token) < 3:
            raise DogStateError("INVALID_PREFERENCE", "exclusion token is too short", field="value")
        return token
    return cleaned


def constraints_from_preferences(prefs: list[PreferenceRecord]) -> PackageConstraints:
    ingredients: list[str] = []
    products: list[str] = []
    budget: float | None = None
    for pref in prefs:
        if pref.status != "EXPLICIT" or pref.superseded:
            continue
        if pref.category == "ingredient_exclusion":
            token = canonical_exclusion_token(pref.value)
            if token and token not in ingredients:
                ingredients.append(token)
        elif pref.category in {"product_exclusion", "product_dislike"}:
            token = canonical_exclusion_token(pref.value)
            if token and token not in products:
                products.append(token)
        elif pref.category == "budget":
            try:
                amount = float(pref.value)
            except (TypeError, ValueError):
                continue
            if math.isfinite(amount) and amount > 0:
                budget = amount
    return PackageConstraints(
        ingredient_exclusions=tuple(ingredients),
        product_exclusions=tuple(products),
        monthly_budget=budget,
    )


def constraints_from_dog(dog_id: str) -> PackageConstraints:
    return constraints_from_preferences(preferences_for(dog_id))


def overlay_budget(profile: DogProfileInput, constraints: PackageConstraints) -> DogProfileInput:
    if constraints.monthly_budget is None:
        return profile
    return profile.model_copy(update={"monthly_budget": constraints.monthly_budget})


def should_apply_stored_preferences(dog_id: str | None, flag: bool | None) -> bool:
    if not dog_id:
        return False
    if flag is None:
        return True
    return bool(flag)


__all__ = [
    "CANONICAL_CATEGORY_DISPLAY",
    "CANONICAL_PACKAGE_CATEGORIES",
    "PackageConstraints",
    "apply_active_constraints",
    "candidate_excluded",
    "canonical_budget_text",
    "canonical_exclusion_token",
    "constraints_from_dog",
    "constraints_from_preferences",
    "filter_candidates",
    "overlay_budget",
    "should_apply_stored_preferences",
    "using_package_constraints",
    "validate_preference_value",
]
