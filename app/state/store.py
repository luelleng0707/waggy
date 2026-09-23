"""Append-only dog-state store. Never writes warehouse scientific files."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.ai.models import ConversationMessage, ConversationRecord, EventKind, EventSource, ProfileEvent
from app.state.db import close_connection, connect, locked
from app.state.errors import DogNotFound, DogStateError
from app.contracts.agent.enums import InputState
from app.contracts.agent.observations import is_breed_derived_trait_name
from app.state.models import (
    ALLOWED_EVENT_TYPES,
    ALLOWED_PREFERENCE_CATEGORIES,
    FORBIDDEN_EVENT_TYPES,
    PUBLIC_EVENT_TYPES,
    AnalysisRecord,
    DogCreateRequest,
    DogPatchRequest,
    PersistentDog,
    PreferenceRecord,
)

_KIND_FOR_TYPE: dict[str, EventKind] = {
    "PROFILE_UPDATE": "profile_update",
    "GROOMER_OBSERVATION": "observation",
    "VETERINARIAN_OBSERVATION": "observation",
    "USER_STATEMENT": "observation",
    "USER_PREFERENCE": "preference",
    "PACKAGE_INTERACTION": "package_interaction",
    "ANALYSIS_RUN": "analysis_snapshot",
    "SYSTEM_EVENT": "system",
}

_TYPE_FOR_KIND: dict[str, str] = {
    "observation": "USER_STATEMENT",
    "preference": "USER_PREFERENCE",
    "weight_update": "PROFILE_UPDATE",
    "analysis_snapshot": "ANALYSIS_RUN",
    "profile_update": "PROFILE_UPDATE",
    "package_interaction": "PACKAGE_INTERACTION",
    "system": "SYSTEM_EVENT",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _load_json(raw: Any, default: Any) -> Any:
    if raw in (None, ""):
        return default
    if isinstance(raw, (dict, list)):
        return raw
    return json.loads(str(raw))


def reset_store() -> None:
    with locked():
        conn = connect()
        for table in ("events", "preferences", "analyses", "conversations", "dogs"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()


def reset_events() -> None:
    with locked():
        conn = connect()
        conn.execute("DELETE FROM events")
        conn.commit()


def reset_conversations() -> None:
    with locked():
        conn = connect()
        conn.execute("DELETE FROM conversations")
        conn.commit()


def reset_connection() -> None:
    close_connection()


def _row_dog(row: Any) -> PersistentDog:
    return PersistentDog(
        schema="waggy_dog_state.v1",
        dog_id=row["dog_id"],
        owner_id=row["owner_id"],
        name=row["name"],
        primary_breed=row["primary_breed"],
        secondary_breed=row["secondary_breed"],
        breed_split_pct=row["breed_split_pct"],
        birthday=row["birthday"],
        age_years=row["age_years"],
        weight_kg=row["weight_kg"],
        sex=row["sex"],
        activity_level=row["activity_level"],
        current_environment=row["current_environment"],
        height_cm=row["height_cm"],
        bcs=row["bcs"],
        observed_conditions=_load_json(row["observed_conditions"], []),
        monthly_budget=row["monthly_budget"],
        breed_input_state=_row_value(row, "breed_input_state"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_value(row: Any, key: str) -> Any:
    keys = row.keys() if hasattr(row, "keys") else []
    if key not in keys:
        return None
    value = row[key]
    if value is None or value == "":
        return None
    return value


def get_dog(dog_id: str) -> PersistentDog | None:
    with locked():
        row = connect().execute("SELECT * FROM dogs WHERE dog_id = ?", (dog_id,)).fetchone()
    return _row_dog(row) if row else None


def find_dogs_named(name: str) -> list[PersistentDog]:
    key = str(name or "").strip().lower()
    if not key:
        return []
    with locked():
        rows = connect().execute(
            "SELECT * FROM dogs WHERE lower(name) = ? ORDER BY created_at ASC, dog_id ASC",
            (key,),
        ).fetchall()
    return [_row_dog(row) for row in rows]


def require_dog(dog_id: str) -> PersistentDog:
    dog = get_dog(dog_id)
    if dog is None:
        raise DogNotFound(dog_id)
    return dog


def _weight_from(body: DogCreateRequest | DogPatchRequest) -> float | None:
    if body.weight_kg is not None and body.weight is not None and body.weight_kg != body.weight:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "weight and weight_kg must match", field="weight")
    if body.weight_kg is not None:
        return body.weight_kg
    return body.weight


def create_dog(body: DogCreateRequest) -> PersistentDog:
    now = _now()
    dog_id = body.dog_id or str(uuid4())
    if get_dog(dog_id) is not None:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "dog_id already exists", field="dog_id")
    name = (body.name or "").strip()
    if not name:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "name is required", field="name")
    breed_input_state = _normalize_breed_input_state(body.breed_input_state)
    if breed_input_state == InputState.UNKNOWN and body.primary_breed:
        raise DogStateError(
            "INVALID_EVENT_PAYLOAD",
            "UNKNOWN breed cannot carry a breed string",
            field="primary_breed",
        )
    dog = PersistentDog(
        dog_id=dog_id,
        owner_id=body.owner_id or "prototype-local",
        name=name,
        primary_breed=None if breed_input_state == InputState.UNKNOWN else body.primary_breed,
        secondary_breed=body.secondary_breed,
        breed_split_pct=body.breed_split_pct,
        birthday=body.birthday,
        age_years=body.age_years,
        weight_kg=_weight_from(body),
        sex=body.sex,
        activity_level=body.activity_level,
        current_environment=body.current_environment,
        height_cm=body.height_cm,
        bcs=body.bcs,
        observed_conditions=list(body.observed_conditions or []),
        monthly_budget=body.monthly_budget,
        breed_input_state=breed_input_state,
        created_at=now,
        updated_at=now,
    )
    with locked():
        conn = connect()
        conn.execute(
            """
            INSERT INTO dogs (
                dog_id, owner_id, name, primary_breed, secondary_breed, breed_split_pct,
                birthday, age_years, weight_kg, sex, activity_level, current_environment,
                height_cm, bcs, observed_conditions, monthly_budget, breed_input_state,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dog.dog_id,
                dog.owner_id,
                dog.name,
                dog.primary_breed,
                dog.secondary_breed,
                dog.breed_split_pct,
                dog.birthday,
                dog.age_years,
                dog.weight_kg,
                dog.sex,
                dog.activity_level,
                dog.current_environment,
                dog.height_cm,
                dog.bcs,
                _json(dog.observed_conditions),
                dog.monthly_budget,
                dog.breed_input_state,
                dog.created_at,
                dog.updated_at,
            ),
        )
        conn.commit()
    record_event(
        dog_id=dog.dog_id,
        source="SYSTEM",
        kind="system",
        value="dog created",
        event_type="SYSTEM_EVENT",
        payload={"action": "create_dog", "name": dog.name},
        status="recorded",
    )
    return dog


def patch_dog(dog_id: str, body: DogPatchRequest) -> PersistentDog:
    dog = require_dog(dog_id)
    updates: dict[str, Any] = {}
    mapping = {
        "name": body.name,
        "primary_breed": body.primary_breed,
        "secondary_breed": body.secondary_breed,
        "breed_split_pct": body.breed_split_pct,
        "birthday": body.birthday,
        "age_years": body.age_years,
        "sex": body.sex,
        "activity_level": body.activity_level,
        "current_environment": body.current_environment,
        "height_cm": body.height_cm,
        "bcs": body.bcs,
        "monthly_budget": body.monthly_budget,
    }
    for key, value in mapping.items():
        if value is not None and getattr(dog, key) != value:
            updates[key] = value
    weight = _weight_from(body)
    if weight is not None and dog.weight_kg != weight:
        updates["weight_kg"] = weight
    if body.observed_conditions is not None and body.observed_conditions != dog.observed_conditions:
        updates["observed_conditions"] = list(body.observed_conditions)
    if updates:
        data = dog.model_dump(by_alias=True)
        data.update(updates)
        data["updated_at"] = _now()
        updated = PersistentDog.model_validate(data)
        _write_dog(updated)
        for field, value in updates.items():
            record_event(
                dog_id=dog_id,
                source="USER" if field != "observed_conditions" else "SYSTEM",
                kind="weight_update" if field == "weight_kg" else "profile_update",
                value=f"{field}={value}",
                event_type="PROFILE_UPDATE",
                payload={"field": field, "value": value},
                confirmed=body.confirmed,
                status="explicit" if body.confirmed else "recorded",
            )
        return updated
    return dog


def _write_dog(dog: PersistentDog) -> None:
    with locked():
        conn = connect()
        conn.execute(
            """
            UPDATE dogs SET
                owner_id=?, name=?, primary_breed=?, secondary_breed=?, breed_split_pct=?,
                birthday=?, age_years=?, weight_kg=?, sex=?, activity_level=?, current_environment=?,
                height_cm=?, bcs=?, observed_conditions=?, monthly_budget=?,
                breed_input_state=?, updated_at=?
            WHERE dog_id=?
            """,
            (
                dog.owner_id,
                dog.name,
                dog.primary_breed,
                dog.secondary_breed,
                dog.breed_split_pct,
                dog.birthday,
                dog.age_years,
                dog.weight_kg,
                dog.sex,
                dog.activity_level,
                dog.current_environment,
                dog.height_cm,
                dog.bcs,
                _json(dog.observed_conditions),
                dog.monthly_budget,
                dog.breed_input_state,
                dog.updated_at,
                dog.dog_id,
            ),
        )
        conn.commit()


def _normalize_breed_input_state(raw: str | None) -> str | None:
    if raw is None or str(raw).strip() == "":
        return None
    text = str(raw).strip()
    if text == InputState.UNKNOWN:
        return InputState.UNKNOWN
    raise DogStateError(
        "INVALID_EVENT_PAYLOAD",
        "breed_input_state may be omitted or UNKNOWN; it is not an Ω12 mapping status",
        field="breed_input_state",
    )


def _event_type_from(*, source: EventSource, kind: EventKind, event_type: str | None) -> str:
    if event_type:
        return event_type
    if source == "VETERINARIAN" and kind == "observation":
        return "VETERINARIAN_OBSERVATION"
    if source == "GROOMER" and kind in {"observation", "weight_update"}:
        return "GROOMER_OBSERVATION" if kind == "observation" else "PROFILE_UPDATE"
    if source == "USER" and kind == "observation":
        return "USER_STATEMENT"
    if source == "USER" and kind == "preference":
        return "USER_PREFERENCE"
    return _TYPE_FOR_KIND.get(kind, "SYSTEM_EVENT")


def _validate_event(*, source: str, event_type: str, public: bool) -> None:
    if source == "SCIENTIFIC" or event_type in FORBIDDEN_EVENT_TYPES:
        raise DogStateError(
            "SCIENTIFIC_EVENT_FORBIDDEN",
            "AI/profile events cannot write scientific warehouse facts.",
            field="event_type",
        )
    if event_type not in ALLOWED_EVENT_TYPES:
        raise DogStateError("INVALID_EVENT_TYPE", f"unsupported event_type {event_type}", field="event_type")
    if public and event_type not in PUBLIC_EVENT_TYPES:
        raise DogStateError(
            "INVALID_EVENT_TYPE",
            "ANALYSIS_RUN is created by an analysis endpoint, not by arbitrary event POST",
            field="event_type",
        )
    if source == "GROOMER" and event_type not in {"GROOMER_OBSERVATION", "PROFILE_UPDATE", "SYSTEM_EVENT"}:
        raise DogStateError(
            "INVALID_EVENT_TYPE",
            "groomer events must remain observations, not diagnoses",
            field="event_type",
        )
    if source == "VETERINARIAN" and event_type not in {"VETERINARIAN_OBSERVATION", "SYSTEM_EVENT"}:
        raise DogStateError(
            "INVALID_EVENT_TYPE",
            "veterinarian events must remain observations, not diagnoses",
            field="event_type",
        )


def record_event(
    *,
    dog_id: str,
    source: EventSource,
    kind: EventKind,
    value: str,
    session_id: str | None = None,
    confirmed: bool = False,
    notes: str | None = None,
    event_type: str | None = None,
    payload: dict[str, Any] | None = None,
    status: str = "recorded",
    correlation_id: str | None = None,
    public: bool = False,
    observed_at: str | None = None,
) -> ProfileEvent:
    resolved_type = _event_type_from(source=source, kind=kind, event_type=event_type)
    _validate_event(source=source, event_type=resolved_type, public=public)
    if source == "GROOMER" and kind not in {"observation", "weight_update", "profile_update", "system"}:
        raise DogStateError(
            "INVALID_EVENT_TYPE",
            "Groomer events must remain observations, not diagnoses.",
            field="kind",
        )
    if source == "VETERINARIAN" and kind not in {"observation", "system"}:
        raise DogStateError(
            "INVALID_EVENT_TYPE",
            "Veterinarian events must remain observations, not diagnoses.",
            field="kind",
        )
    if source == "USER" and kind == "observation":
        notes = (notes or "") + "|user_reported_observation"
    payload = dict(payload or {})
    observation_type = payload.get("observation_type")
    if isinstance(observation_type, str) and is_breed_derived_trait_name(observation_type):
        raise DogStateError(
            "INVALID_EVENT_PAYLOAD",
            "breed-derived trait names cannot be recorded as individual observations",
            field="observation_type",
        )
    kind_name: EventKind = kind
    if kind_name not in {
        "observation",
        "preference",
        "weight_update",
        "analysis_snapshot",
        "profile_update",
        "package_interaction",
        "system",
    }:
        kind_name = _KIND_FOR_TYPE.get(resolved_type, "system")  # type: ignore[assignment]
    elif resolved_type in _KIND_FOR_TYPE and kind in {"observation", "preference"}:
        kind_name = _KIND_FOR_TYPE[resolved_type]
    now = _now()
    observed = str(observed_at).strip() if observed_at and str(observed_at).strip() else None
    event = ProfileEvent(
        event_id=str(uuid4()),
        dog_id=dog_id,
        source=source,
        kind=kind_name,
        value=value,
        timestamp=now,
        session_id=session_id,
        confirmed=confirmed,
        notes=notes,
        event_type=resolved_type,  # type: ignore[arg-type]
        payload=payload,
        status=status,
        created_at=now,
        correlation_id=correlation_id,
        observed_at=observed,
        recorded_at=now,
    )
    with locked():
        conn = connect()
        conn.execute(
            """
            INSERT INTO events (
                event_id, dog_id, event_type, source, kind, value, payload, status,
                timestamp, created_at, session_id, correlation_id, confirmed, notes,
                observed_at, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.dog_id,
                event.event_type,
                event.source,
                event.kind,
                event.value,
                _json(event.payload),
                event.status,
                event.timestamp,
                event.created_at,
                event.session_id,
                event.correlation_id,
                1 if event.confirmed else 0,
                event.notes,
                event.observed_at,
                event.recorded_at,
            ),
        )
        conn.commit()
    _apply_event_to_current(event)
    return event


def _apply_event_to_current(event: ProfileEvent) -> None:
    dog = get_dog(event.dog_id)
    if dog is None:
        return
    payload = event.payload or {}
    changed = False
    if event.event_type == "GROOMER_OBSERVATION":
        token = payload.get("observed_condition")
        if isinstance(token, str) and token.strip():
            token = token.strip()
            if token not in dog.observed_conditions:
                dog.observed_conditions.append(token)
                changed = True
    elif event.event_type == "PROFILE_UPDATE":
        field = payload.get("field")
        value = payload.get("value")
        apply_value = event.source in {"GROOMER", "SYSTEM"} or event.confirmed
        if apply_value and field in {
            "name",
            "primary_breed",
            "secondary_breed",
            "birthday",
            "age_years",
            "weight_kg",
            "sex",
            "activity_level",
            "current_environment",
            "monthly_budget",
        }:
            if getattr(dog, field) != value:
                setattr(dog, field, value)
                changed = True
    elif event.event_type == "USER_PREFERENCE" and event.status == "explicit":
        if payload.get("category") == "budget":
            try:
                budget = float(event.value)
            except (TypeError, ValueError):
                budget = None
            if budget is not None and dog.monthly_budget != budget:
                dog.monthly_budget = budget
                changed = True
    if changed:
        dog.updated_at = _now()
        _write_dog(dog)


def events_for(dog_id: str) -> list[ProfileEvent]:
    with locked():
        rows = connect().execute(
            "SELECT * FROM events WHERE dog_id = ? ORDER BY timestamp ASC, event_id ASC",
            (dog_id,),
        ).fetchall()
    return [_row_event(row) for row in rows]


def _row_event(row: Any) -> ProfileEvent:
    return ProfileEvent(
        event_id=row["event_id"],
        dog_id=row["dog_id"],
        source=row["source"],
        kind=row["kind"],
        value=row["value"] or "",
        timestamp=row["timestamp"],
        session_id=row["session_id"],
        confirmed=bool(row["confirmed"]),
        notes=row["notes"],
        event_type=row["event_type"],
        payload=_load_json(row["payload"], {}),
        status=row["status"],
        created_at=row["created_at"],
        correlation_id=row["correlation_id"],
        observed_at=_row_value(row, "observed_at"),
        recorded_at=_row_value(row, "recorded_at"),
    )


def current_projection(dog_id: str) -> dict[str, Any]:
    history = events_for(dog_id)
    latest: dict[str, ProfileEvent] = {}
    for event in history:
        latest[event.kind] = event
        latest[event.event_type] = event
    return {
        "history": [item.model_dump(by_alias=True) for item in history],
        "current": {key: value.model_dump(by_alias=True) for key, value in latest.items()},
        "dog": get_dog(dog_id).model_dump(by_alias=True) if get_dog(dog_id) else None,
    }


def save_preference(
    *,
    dog_id: str,
    category: str,
    value: str,
    source: str = "USER",
    status: str = "EXPLICIT",
) -> PreferenceRecord:
    if source == "SCIENTIFIC":
        raise DogStateError("SCIENTIFIC_EVENT_FORBIDDEN", "preferences cannot write scientific facts", field="source")
    if status.upper() != "EXPLICIT":
        raise DogStateError(
            "AMBIGUOUS_PREFERENCE",
            "only EXPLICIT preferences are durable",
            field="status",
        )
    if category not in ALLOWED_PREFERENCE_CATEGORIES:
        raise DogStateError("INVALID_EVENT_PAYLOAD", f"unsupported preference category {category}", field="category")
    cleaned = str(value).strip()
    if not cleaned:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "preference value is required", field="value")
    require_dog(dog_id)
    event = record_event(
        dog_id=dog_id,
        source="USER" if source == "USER" else source,  # type: ignore[arg-type]
        kind="preference",
        value=cleaned,
        event_type="USER_PREFERENCE",
        payload={"category": category, "value": cleaned},
        status="explicit",
        confirmed=True,
    )
    if category in {"budget", "package_acceptance", "package_rejection"}:
        with locked():
            conn = connect()
            conn.execute(
                "UPDATE preferences SET superseded = 1 WHERE dog_id = ? AND category = ? AND superseded = 0",
                (dog_id, category),
            )
            conn.commit()
    now = _now()
    record = PreferenceRecord(
        preference_id=str(uuid4()),
        dog_id=dog_id,
        category=category,
        value=cleaned,
        source=source,
        status="EXPLICIT",
        event_id=event.event_id,
        created_at=now,
        superseded=False,
    )
    with locked():
        conn = connect()
        conn.execute(
            """
            INSERT INTO preferences (
                preference_id, dog_id, category, value, source, status, event_id, created_at, superseded
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                record.preference_id,
                record.dog_id,
                record.category,
                record.value,
                record.source,
                record.status,
                record.event_id,
                record.created_at,
            ),
        )
        conn.commit()
    return record


def preferences_for(dog_id: str, *, include_superseded: bool = False) -> list[PreferenceRecord]:
    sql = "SELECT * FROM preferences WHERE dog_id = ?"
    params: list[Any] = [dog_id]
    if not include_superseded:
        sql += " AND superseded = 0"
    sql += " ORDER BY created_at ASC, preference_id ASC"
    with locked():
        rows = connect().execute(sql, params).fetchall()
    return [
        PreferenceRecord(
            preference_id=row["preference_id"],
            dog_id=row["dog_id"],
            category=row["category"],
            value=row["value"],
            source=row["source"],
            status=row["status"],
            event_id=row["event_id"],
            created_at=row["created_at"],
            superseded=bool(row["superseded"]),
        )
        for row in rows
    ]


def save_analysis(
    *,
    dog_id: str,
    analysis_signature: str,
    engine_version: str | None,
    warehouse_version: str | None,
    input_snapshot: dict[str, Any],
    result_digest: dict[str, Any],
    correlation_id: str | None = None,
    result_status: str = "ok",
) -> AnalysisRecord:
    require_dog(dog_id)
    now = _now()
    record = AnalysisRecord(
        analysis_id=str(uuid4()),
        dog_id=dog_id,
        analysis_signature=analysis_signature,
        engine_version=engine_version,
        warehouse_version=warehouse_version,
        input_snapshot=input_snapshot,
        result_digest=result_digest,
        result_status=result_status,
        created_at=now,
        correlation_id=correlation_id,
    )
    with locked():
        conn = connect()
        conn.execute(
            """
            INSERT INTO analyses (
                analysis_id, dog_id, analysis_signature, engine_version, warehouse_version,
                input_snapshot, result_digest, result_status, created_at, correlation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.analysis_id,
                record.dog_id,
                record.analysis_signature,
                record.engine_version,
                record.warehouse_version,
                _json(record.input_snapshot),
                _json(record.result_digest),
                record.result_status,
                record.created_at,
                record.correlation_id,
            ),
        )
        conn.commit()
    record_event(
        dog_id=dog_id,
        source="SYSTEM",
        kind="analysis_snapshot",
        value=analysis_signature,
        event_type="ANALYSIS_RUN",
        payload={
            "analysis_id": record.analysis_id,
            "analysis_signature": analysis_signature,
            "result_digest": result_digest,
        },
        status="recorded",
        correlation_id=correlation_id,
    )
    return record


def analyses_for(dog_id: str) -> list[AnalysisRecord]:
    with locked():
        rows = connect().execute(
            "SELECT * FROM analyses WHERE dog_id = ? ORDER BY created_at ASC, analysis_id ASC",
            (dog_id,),
        ).fetchall()
    return [
        AnalysisRecord(
            analysis_id=row["analysis_id"],
            dog_id=row["dog_id"],
            analysis_signature=row["analysis_signature"],
            engine_version=row["engine_version"],
            warehouse_version=row["warehouse_version"],
            input_snapshot=_load_json(row["input_snapshot"], {}),
            result_digest=_load_json(row["result_digest"], {}),
            result_status=row["result_status"],
            created_at=row["created_at"],
            correlation_id=row["correlation_id"],
        )
        for row in rows
    ]


def get_conversation(conversation_id: str) -> ConversationRecord | None:
    with locked():
        row = connect().execute(
            "SELECT * FROM conversations WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()
    if row is None:
        return None
    return ConversationRecord(
        conversation_id=row["conversation_id"],
        dog_id=row["dog_id"],
        analysis_signature=row["analysis_signature"],
        selected_bundle_id=row["selected_bundle_id"],
        messages=[ConversationMessage.model_validate(item) for item in _load_json(row["messages"], [])],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        policy_version=row["policy_version"],
        provider=row["provider"],
        model=row["model"],
    )


def create_conversation(
    *,
    analysis_signature: str,
    dog_id: str | None,
    selected_bundle_id: str | None,
    conversation_id: str | None = None,
    policy_version: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> ConversationRecord:
    now = _now()
    record = ConversationRecord(
        conversation_id=conversation_id or str(uuid4()),
        dog_id=dog_id,
        analysis_signature=analysis_signature,
        selected_bundle_id=selected_bundle_id,
        messages=[],
        created_at=now,
        updated_at=now,
        policy_version=policy_version,
        provider=provider,
        model=model,
    )
    with locked():
        conn = connect()
        conn.execute(
            """
            INSERT INTO conversations (
                conversation_id, dog_id, analysis_signature, selected_bundle_id,
                messages, policy_version, provider, model, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.conversation_id,
                record.dog_id,
                record.analysis_signature,
                record.selected_bundle_id,
                _json([]),
                record.policy_version,
                record.provider,
                record.model,
                record.created_at,
                record.updated_at,
            ),
        )
        conn.commit()
    return record


def append_messages(conversation_id: str, items: list[ConversationMessage]) -> ConversationRecord:
    record = get_conversation(conversation_id)
    if record is None:
        raise DogStateError("INVALID_EVENT_PAYLOAD", "conversation was not found", field="conversation_id")
    record.messages.extend(items)
    record.updated_at = _now()
    with locked():
        conn = connect()
        conn.execute(
            "UPDATE conversations SET messages = ?, updated_at = ? WHERE conversation_id = ?",
            (_json([item.model_dump() for item in record.messages]), record.updated_at, conversation_id),
        )
        conn.commit()
    return record


def conversations_for_dog(dog_id: str) -> list[ConversationRecord]:
    with locked():
        rows = connect().execute(
            "SELECT conversation_id FROM conversations WHERE dog_id = ? ORDER BY updated_at ASC",
            (dog_id,),
        ).fetchall()
    out: list[ConversationRecord] = []
    for row in rows:
        item = get_conversation(row["conversation_id"])
        if item is not None:
            out.append(item)
    return out
