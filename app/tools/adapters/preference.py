"""Preference candidate only. Does not persist and does not recompute."""

from __future__ import annotations

from app.state.errors import DogStateError
from app.state.package_constraints import validate_preference_value
from app.tools.auth import authorize_dog
from app.tools.errors import INVALID_PREFERENCE, ToolFailure
from app.tools.models import ProposePreferenceInput, ToolCaller

_MUTATION_NOTE = "Preference mutation remains an explicit application-authorized operation."


def propose_preference(payload: ProposePreferenceInput, caller: ToolCaller) -> dict:
    if payload.dog_id:
        authorize_dog(caller, payload.dog_id)
    if payload.type == "ingredient_exclusion":
        category = "ingredient_exclusion"
        raw = str(payload.value)
    else:
        category = "budget"
        raw = str(payload.value)
    try:
        cleaned = validate_preference_value(category, raw)
    except DogStateError as exc:
        raise ToolFailure(INVALID_PREFERENCE, str(exc), field=exc.field or "value") from exc
    value: str | float = cleaned
    if payload.type == "monthly_budget":
        value = float(cleaned)
    return {
        "candidate": {
            "type": payload.type,
            "value": value,
            "category": category,
            "scientific": False,
        },
        "validation_status": "valid",
        "requires_confirmation": True,
        "requires_authorized_mutation": True,
        "persisted": False,
        "recomputed": False,
        "engine_ran": False,
        "note": _MUTATION_NOTE,
        "user_text": payload.user_text,
        "dog_id": payload.dog_id,
    }
