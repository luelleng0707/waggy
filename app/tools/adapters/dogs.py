"""Dog-profile tool adapter. Reads persistent dog state only."""

from __future__ import annotations

from app.state.store import preferences_for
from app.tools.auth import authorize_dog
from app.tools.models import GetDogProfileInput, ToolCaller

_PROFILE_FIELDS = (
    "dog_id",
    "owner_id",
    "name",
    "primary_breed",
    "secondary_breed",
    "birthday",
    "age_years",
    "weight_kg",
    "sex",
    "activity_level",
    "current_environment",
    "observed_conditions",
    "monthly_budget",
)

_REQUIRED_FOR_ANALYSIS = (
    "primary_breed",
    "weight_kg",
    "activity_level",
    "current_environment",
)


def get_dog_profile(payload: GetDogProfileInput, caller: ToolCaller) -> dict:
    dog = authorize_dog(caller, payload.dog_id)
    dumped = dog.model_dump(mode="json")
    profile = {key: dumped.get(key) for key in _PROFILE_FIELDS}
    missing = [key for key in _REQUIRED_FOR_ANALYSIS if profile.get(key) in (None, "", [])]
    if not profile.get("birthday") and profile.get("age_years") is None:
        missing.append("birthday_or_age_years")
    data: dict = {
        "dog": profile,
        "completeness": {
            "missing_fields": missing,
            "ready_for_analysis": not missing,
        },
        "engine_ran": False,
    }
    if payload.include_preferences:
        data["preferences"] = [
            {
                "preference_id": item.preference_id,
                "category": item.category,
                "value": item.value,
                "status": item.status,
                "source": item.source,
                "scientific": False,
            }
            for item in preferences_for(dog.dog_id)
        ]
    return data
