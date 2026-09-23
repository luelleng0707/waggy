"""Canonical groomer observation adapter.

Legacy HTTP routes remain. Longitudinal truth is persistent dog state when a
dog can be uniquely identified. Process memory is only a transient cache for
unnamed/unpersisted pets on the legacy analyze path.

Groomer observations remain observations, not diagnoses or warehouse facts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.state.errors import DogNotFound

SESSIONS: dict[str, dict[str, Any]] = {}


def reset_groomer_sessions() -> None:
    SESSIONS.clear()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tokens(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(item).strip() for item in raw if str(item).strip()]


def resolve_groomer_dog(*, dog_id: str | None, pet_id: str) -> Any:
    from app.state.store import find_dogs_named, get_dog

    if dog_id and str(dog_id).strip():
        dog = get_dog(str(dog_id).strip())
        if dog is None:
            raise DogNotFound(str(dog_id).strip())
        return dog
    matches = find_dogs_named(pet_id)
    if len(matches) == 1:
        return matches[0]
    return None


def observations_for_legacy_analyze(pet_key: str) -> list[str]:
    """Legacy analyze merge. Workbench does not call this."""
    from app.state.store import find_dogs_named

    if not pet_key:
        return []
    matches = find_dogs_named(pet_key)
    if len(matches) == 1:
        return list(matches[0].observed_conditions or [])
    session = SESSIONS.get(pet_key.lower())
    return list((session or {}).get("observed_conditions") or [])


def get_groomer_session(pet_id: str) -> dict[str, Any]:
    dog = resolve_groomer_dog(dog_id=None, pet_id=pet_id)
    if dog is not None:
        return {
            "observed_conditions": list(dog.observed_conditions or []),
            "notes": None,
            "weight": dog.weight_kg,
            "height": dog.height_cm,
            "updated_at": dog.updated_at,
            "dog_id": dog.dog_id,
            "canonical": True,
        }
    return dict(SESSIONS.get(pet_id.lower()) or {"observed_conditions": []})


def apply_groomer_update(
    *,
    pet_id: str,
    observed_conditions: list[str] | None = None,
    notes: str | None = None,
    weight: Any = None,
    height: Any = None,
    dog_id: str | None = None,
) -> dict[str, Any]:
    key = str(pet_id).lower()
    tokens = _tokens(observed_conditions)
    note_text = str(notes).strip() if notes not in (None, "") else ""
    dog = resolve_groomer_dog(dog_id=dog_id, pet_id=pet_id)
    stamp = _now()
    if dog is not None:
        from app.state.store import get_dog, record_event
        for token in tokens:
            record_event(
                dog_id=dog.dog_id,
                source="GROOMER",
                kind="observation",
                value=token,
                event_type="GROOMER_OBSERVATION",
                payload={"observed_condition": token, "observation": token},
                status="recorded",
            )
        if note_text:
            record_event(
                dog_id=dog.dog_id,
                source="GROOMER",
                kind="observation",
                value=note_text,
                event_type="GROOMER_OBSERVATION",
                payload={"observation": note_text, "category": "unspecified"},
                status="recorded",
            )
        if weight not in (None, ""):
            try:
                weight_kg = float(weight)
            except (TypeError, ValueError):
                weight_kg = None
            if weight_kg is not None and weight_kg > 0:
                record_event(
                    dog_id=dog.dog_id,
                    source="GROOMER",
                    kind="weight_update",
                    value=str(weight_kg),
                    event_type="PROFILE_UPDATE",
                    payload={"field": "weight_kg", "value": weight_kg},
                    confirmed=True,
                    status="recorded",
                )
        dog = get_dog(dog.dog_id)
        session = {
            "observed_conditions": list((dog.observed_conditions if dog else tokens) or []),
            "notes": note_text or None,
            "weight": (dog.weight_kg if dog else weight),
            "height": height,
            "updated_at": stamp,
            "dog_id": dog.dog_id if dog else None,
            "canonical": True,
        }
        SESSIONS[key] = session
        return session

    session = SESSIONS.get(key) or {"observed_conditions": []}
    session["observed_conditions"] = list(
        dict.fromkeys([*(session.get("observed_conditions") or []), *tokens])
    )
    session["notes"] = note_text or None
    session["weight"] = weight
    session["height"] = height
    session["updated_at"] = stamp
    session["canonical"] = False
    SESSIONS[key] = session
    return session
