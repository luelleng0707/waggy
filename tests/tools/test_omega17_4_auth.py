"""Ω17.4 prototype permission and dog-scope checks."""

from __future__ import annotations

from app.state.models import DogCreateRequest
from app.state.store import create_dog, save_analysis
from app.tools.errors import DOG_ACCESS_DENIED, TOOL_NOT_ALLOWED
from app.tools.gateway import invoke_tool
from app.tools.models import ToolCaller


def _dog(**overrides) -> DogCreateRequest:
    body = {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "age_years": 5.4,
        "weight_kg": 30,
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
    }
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def test_other_owner_cannot_read_dog_profile():
    dog = create_dog(_dog(owner_id="owner-a"))
    envelope = invoke_tool(
        "get_dog_profile",
        {"dog_id": dog.dog_id},
        ToolCaller(role="customer", owner_id="owner-b", actor="ai"),
    )
    assert envelope.status == "error"
    assert envelope.errors[0].code == DOG_ACCESS_DENIED


def test_authorized_dog_ids_constrain_scope():
    dog = create_dog(_dog())
    other = create_dog(_dog(name="Other"))
    denied = invoke_tool(
        "get_dog_profile",
        {"dog_id": other.dog_id},
        ToolCaller(authorized_dog_ids=[dog.dog_id]),
    )
    assert denied.status == "error"
    assert denied.errors[0].code == DOG_ACCESS_DENIED
    allowed = invoke_tool(
        "get_dog_profile",
        {"dog_id": dog.dog_id},
        ToolCaller(authorized_dog_ids=[dog.dog_id]),
    )
    assert allowed.status == "ok"
    assert allowed.data["dog"]["name"] == "Dolly"


def test_business_role_cannot_read_health():
    dog = create_dog(_dog())
    save_analysis(
        dog_id=dog.dog_id,
        analysis_signature="sig-a",
        engine_version="2.1.0",
        warehouse_version="test",
        input_snapshot={},
        result_digest={"finding_titles": ["Joints"], "package_product_ids": {}},
    )
    envelope = invoke_tool(
        "analyze_health",
        {"dog_id": dog.dog_id},
        ToolCaller(role="business", actor="ai"),
    )
    assert envelope.status == "error"
    assert envelope.errors[0].code == TOOL_NOT_ALLOWED


def test_ai_actor_is_not_a_superuser():
    dog = create_dog(_dog(owner_id="owner-a"))
    envelope = invoke_tool(
        "analyze_health",
        {"dog_id": dog.dog_id},
        ToolCaller(role="customer", owner_id="owner-b", actor="ai"),
    )
    assert envelope.status == "error"
    assert envelope.errors[0].code == DOG_ACCESS_DENIED
