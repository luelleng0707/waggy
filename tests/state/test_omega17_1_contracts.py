"""Ω17.1 dog-state contracts: persistence, provenance, fail-closed projection."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.ai.agent import AnalysisMismatchError, WaggyExplanationAgent
from app.ai.conversation import get_conversation
from app.ai.models import ExplainRequest
from app.ai.providers.fake import FakeProvider
from app.state.errors import DogStateError
from app.state.models import DogCreateRequest, DogPatchRequest
from app.state.preferences import persist_explicit_preference
from app.state.projection import project_to_dog_profile_input
from app.state.store import (
    analyses_for,
    create_dog,
    events_for,
    get_dog,
    patch_dog,
    preferences_for,
    record_event,
    reset_connection,
    save_analysis,
)

ROOT = Path(__file__).resolve().parents[2]


def _dog(**overrides) -> DogCreateRequest:
    body = {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "birthday": "2021-04-15",
        "age_years": 5.4,
        "weight_kg": 30.0,
        "sex": "Female",
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": ["joint_stiffness"],
        "monthly_budget": 100.0,
    }
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def test_dog_persists_across_connection_reset():
    created = create_dog(_dog(name="Dolly"))
    reset_connection()
    loaded = get_dog(created.dog_id)
    assert loaded is not None
    assert loaded.name == "Dolly"
    assert loaded.weight_kg == 30.0
    assert loaded.owner_id == "prototype-local"


def test_patch_dog_updates_and_preserves_history():
    dog = create_dog(_dog())
    patch_dog(dog.dog_id, DogPatchRequest(weight_kg=24.5, confirmed=True))
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 24.5
    kinds = [item.event_type for item in events_for(dog.dog_id)]
    assert "PROFILE_UPDATE" in kinds
    assert "SYSTEM_EVENT" in kinds


def test_groomer_observation_is_not_a_diagnosis():
    dog = create_dog(_dog())
    event = record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="coat appears unusually dry",
        event_type="GROOMER_OBSERVATION",
        payload={"observation": "coat appears unusually dry", "category": "coat", "severity": "mild"},
    )
    assert event.source == "GROOMER"
    assert event.event_type == "GROOMER_OBSERVATION"
    assert event.kind == "observation"
    assert "dermatological disease" not in event.value
    history = events_for(dog.dog_id)
    assert history[-1].payload["severity"] == "mild"


def test_groomer_token_updates_observed_conditions_not_prose():
    dog = create_dog(_dog(observed_conditions=[]))
    record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="coat looks weird",
        event_type="GROOMER_OBSERVATION",
        payload={"observation": "coat looks weird"},
    )
    record_event(
        dog_id=dog.dog_id,
        source="GROOMER",
        kind="observation",
        value="itching",
        event_type="GROOMER_OBSERVATION",
        payload={"observed_condition": "itching", "observation": "itching"},
    )
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert "itching" in loaded.observed_conditions
    assert "coat looks weird" not in loaded.observed_conditions


def test_user_statement_is_not_groomer_and_does_not_overwrite_weight():
    dog = create_dog(_dog(weight_kg=30.0))
    event = record_event(
        dog_id=dog.dog_id,
        source="USER",
        kind="observation",
        value="I think my dog gained weight",
        event_type="USER_STATEMENT",
        payload={"field": "weight_kg", "value": 99},
        confirmed=False,
    )
    assert event.source == "USER"
    assert event.notes and "user_reported_observation" in event.notes
    loaded = get_dog(dog.dog_id)
    assert loaded is not None
    assert loaded.weight_kg == 30.0


def test_explicit_preference_persists_ambiguous_does_not():
    dog = create_dog(_dog())
    persist_explicit_preference(dog.dog_id, category="ingredient_exclusion", value="chicken")
    prefs = preferences_for(dog.dog_id)
    assert any(item.category == "ingredient_exclusion" and item.value == "chicken" for item in prefs)
    with pytest.raises(DogStateError) as exc:
        persist_explicit_preference(dog.dog_id, category="budget", value="That's expensive.")
    assert exc.value.code == "AMBIGUOUS_PREFERENCE"
    with pytest.raises(DogStateError):
        persist_explicit_preference(dog.dog_id, category="budget", value="80", status="inferred")


def test_preference_is_not_a_scientific_fact():
    dog = create_dog(_dog())
    persist_explicit_preference(dog.dog_id, category="ingredient_exclusion", value="chicken")
    profile = project_to_dog_profile_input(dog.dog_id)
    dumped = profile.model_dump()
    assert "ingredient_exclusion" not in dumped
    assert "prevalence" not in dumped
    assert dumped["monthly_budget"] == 100.0


def test_scientific_event_types_are_rejected():
    dog = create_dog(_dog())
    with pytest.raises(DogStateError) as exc:
        record_event(
            dog_id=dog.dog_id,
            source="SCIENTIFIC",
            kind="observation",
            value="warehouse row",
        )
    assert exc.value.code == "SCIENTIFIC_EVENT_FORBIDDEN"
    with pytest.raises(DogStateError):
        record_event(
            dog_id=dog.dog_id,
            source="USER",
            kind="observation",
            value="99% hip dysplasia",
            event_type="PREVALENCE_UPDATE",
            public=True,
        )


def test_projection_fail_closed_no_silent_defaults():
    created = create_dog(DogCreateRequest(name="Incomplete"))
    with pytest.raises(DogStateError) as exc:
        project_to_dog_profile_input(created.dog_id)
    assert exc.value.code == "MISSING_REQUIRED_PROFILE_INPUT"
    assert "5.0" not in str(exc.value)
    assert "20" not in str(exc.value)


def test_complete_projection_maps_to_engine_dto():
    dog = create_dog(_dog(age_years=5.4, birthday=None))
    profile = project_to_dog_profile_input(dog.dog_id)
    assert profile.name == "Dolly"
    assert profile.primary_breed == "Labrador Retriever"
    assert profile.weight_kg == 30.0
    assert profile.age_years == 5.4
    assert "joint_stiffness" in profile.observed_conditions


def test_analysis_metadata_persists_without_full_canonical_blob():
    dog = create_dog(_dog())
    save_analysis(
        dog_id=dog.dog_id,
        analysis_signature="sig-a",
        engine_version="2.1.0",
        warehouse_version="test",
        input_snapshot={"name": "Dolly", "weight_kg": 30},
        result_digest={"package_product_ids": {"balanced": ["P1"]}},
    )
    rows = analyses_for(dog.dog_id)
    assert len(rows) == 1
    assert rows[0].analysis_signature == "sig-a"
    assert "canonical" not in rows[0].model_dump()
    assert events_for(dog.dog_id)[-1].event_type == "ANALYSIS_RUN"


def test_conversation_stays_bound_to_analysis_signature():
    dog = create_dog(_dog())
    agent = WaggyExplanationAgent(FakeProvider())
    first = agent.explain(
        ExplainRequest(
            analysis_signature="sig-a",
            canonical={
                "schema": "canonical_analysis.v1",
                "analysis_id": "sig-a",
                "input": {"dog_profile": {"name": "Dolly"}},
                "scientific_analysis": {"findings": [], "nutrient_targets": [], "evidence": [], "warehouse_status": {}},
                "product_matching": {"recommendations": []},
                "package_optimization": {
                    "algorithm": "PACKAGE_OPTIMIZER_V2_1",
                    "package_options": {},
                    "search": {"llm_used": False},
                },
                "system": {"warnings": []},
            },
            user_message="Why?",
            dog_id=dog.dog_id,
        )
    )
    stored = get_conversation(first.conversation_id)
    assert stored is not None
    assert stored.dog_id == dog.dog_id
    assert stored.analysis_signature == "sig-a"
    with pytest.raises(AnalysisMismatchError):
        agent.explain(
            ExplainRequest(
                analysis_signature="sig-b",
                canonical={
                    "schema": "canonical_analysis.v1",
                    "analysis_id": "sig-b",
                    "input": {"dog_profile": {"name": "Dolly"}},
                    "scientific_analysis": {"findings": [], "nutrient_targets": [], "evidence": [], "warehouse_status": {}},
                    "product_matching": {"recommendations": []},
                    "package_optimization": {
                        "algorithm": "PACKAGE_OPTIMIZER_V2_1",
                        "package_options": {},
                        "search": {"llm_used": False},
                    },
                    "system": {"warnings": []},
                },
                user_message="Why the new one?",
                conversation_id=first.conversation_id,
                dog_id=dog.dog_id,
            )
        )


def test_state_layer_does_not_write_warehouse():
    text = (ROOT / "app" / "state" / "store.py").read_text(encoding="utf-8")
    for token in ("read_csv", "to_csv", "generate_reproducible_report", "package_optimizer", "scientific_care"):
        assert token not in text
    before = (ROOT / "app" / "agent" / "engine.py").stat().st_mtime
    dog = create_dog(_dog())
    persist_explicit_preference(dog.dog_id, category="ingredient_exclusion", value="chicken")
    after = (ROOT / "app" / "agent" / "engine.py").stat().st_mtime
    assert before == after
