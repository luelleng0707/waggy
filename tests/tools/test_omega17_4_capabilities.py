"""Ω17.4 adapters wrap stored state. They do not run the engine."""

from __future__ import annotations

import pytest

from app.state.models import DogCreateRequest
from app.state.store import create_dog, preferences_for, save_analysis
from app.state.version import WAGGY_RECALCULATION_EXPLANATION_SCHEMA, WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA
from app.tools.errors import ANALYSIS_NOT_FOUND, INVALID_PREFERENCE
from app.tools.gateway import WaggyToolGateway, invoke_tool
from app.tools.models import ToolCaller


def _dog(**overrides) -> DogCreateRequest:
    body = {
        "name": "Dolly",
        "primary_breed": "Labrador Retriever",
        "age_years": 5.4,
        "weight_kg": 30,
        "activity_level": "Moderate",
        "current_environment": "Temperate Outdoor",
        "observed_conditions": ["joint_stiffness"],
        "monthly_budget": 120,
    }
    body.update(overrides)
    return DogCreateRequest.model_validate(body)


def _packages(chicken: bool = True) -> dict:
    ids = ["SF001", "SF002"] if chicken else ["SF001"]
    names = ["Demo Fresh Beef Bowl", "Demo Fresh Chicken Bowl"] if chicken else ["Demo Fresh Beef Bowl"]
    return {
        "essential": {
            "bundle_id": "e1",
            "product_ids": ["SF001"],
            "product_names": ["Demo Fresh Beef Bowl"],
            "monthly_cost": 50,
        },
        "balanced": {
            "bundle_id": "b1" if chicken else "b2",
            "product_ids": ids,
            "product_names": names,
            "monthly_cost": 80,
        },
        "optimal": {
            "bundle_id": "o1",
            "product_ids": ids,
            "product_names": names,
            "monthly_cost": 120,
        },
    }


def _digest(*, signature: str, chicken: bool = True, exclusions: list[str] | None = None) -> dict:
    packages = _packages(chicken=chicken)
    titles = ["Joints"]
    nutrients = [{"nutrient": "protein", "min": 40, "max": 90}]
    removed = [] if chicken else ["SF002"]
    return {
        "analysis_signature": signature,
        "finding_titles": titles,
        "package_product_ids": {tier: row["product_ids"] for tier, row in packages.items()},
        "recommendation_snapshot": {
            "schema": WAGGY_RECOMMENDATION_SNAPSHOT_SCHEMA,
            "scientific": False,
            "analysis_signature": signature,
            "engine_version": "2.1.0",
            "optimizer_version": "PACKAGE_OPTIMIZER_V2_1",
            "science": {"finding_titles": titles, "nutrients": nutrients},
            "recommendations": packages,
            "eligibility": {
                "scientific": False,
                "applied": bool(exclusions),
                "ingredient_exclusions": exclusions or [],
                "removed_product_ids": removed,
                "removed": [
                    {"product_id": "SF002", "reason": "ingredient_exclusion:chicken"}
                    for _ in removed
                ],
            },
            "monthly_budget": None,
            "llm_used": False,
        },
    }


def _save(dog_id: str, signature: str, **digest_kwargs):
    return save_analysis(
        dog_id=dog_id,
        analysis_signature=signature,
        engine_version="2.1.0",
        warehouse_version="test",
        input_snapshot={"name": "Dolly"},
        result_digest=_digest(signature=signature, **digest_kwargs),
    )


@pytest.fixture
def dog():
    return create_dog(_dog())


@pytest.fixture
def caller():
    return ToolCaller(role="customer", owner_id="prototype-local", actor="ai")


@pytest.fixture
def engine_guard(monkeypatch: pytest.MonkeyPatch):
    import app.agent.engine as engine_mod

    def boom(*_args, **_kwargs):
        raise AssertionError("Ω17.4 tools must not call generate_reproducible_report")

    monkeypatch.setattr(engine_mod.PPIEWellnessAgent, "generate_reproducible_report", boom)


def test_get_dog_profile_does_not_run_engine(dog, caller, engine_guard):
    envelope = invoke_tool("get_dog_profile", {"dog_id": dog.dog_id, "include_preferences": True}, caller)
    assert envelope.status == "ok"
    assert envelope.data["engine_ran"] is False
    assert envelope.data["dog"]["name"] == "Dolly"
    assert envelope.data["dog"]["primary_breed"] == "Labrador Retriever"
    assert envelope.data["completeness"]["ready_for_analysis"] is True
    assert envelope.data["preferences"] == []


def test_health_nutrition_and_packages_use_stored_digest(dog, caller, engine_guard):
    _save(dog.dog_id, "sig-a")
    health = invoke_tool("analyze_health", {"dog_id": dog.dog_id}, caller)
    assert health.status == "ok"
    assert health.data["engine_ran"] is False
    assert health.data["evidence_status"] == "NOT_AVAILABLE"
    assert health.data["findings"][0]["title"] == "Joints"
    nutrition = invoke_tool("calculate_nutrition", {"dog_id": dog.dog_id}, caller)
    assert nutrition.status == "ok"
    assert nutrition.data["nutrient_targets"][0]["nutrient"] == "protein"
    assert nutrition.data["nutrient_targets"][0]["min"] == 40
    packages = invoke_tool("get_package_options", {"dog_id": dog.dog_id}, caller)
    assert packages.status == "ok"
    assert packages.data["optimizer_version"] == "PACKAGE_OPTIMIZER_V2_1"
    assert packages.data["engine_ran"] is False
    assert "SF002" in packages.data["package_options"]["balanced"][0]["product_ids"]


def test_missing_analysis_is_not_an_engine_run(dog, caller, engine_guard):
    envelope = invoke_tool("analyze_health", {"dog_id": dog.dog_id}, caller)
    assert envelope.status == "error"
    assert envelope.errors[0].code == ANALYSIS_NOT_FOUND


def test_get_products_uses_injected_catalog(dog, caller, engine_guard):
    gateway = WaggyToolGateway(
        catalog_loader=lambda: [
            {
                "product_id": "SF001",
                "product_name": "Demo Fresh Beef Bowl",
                "category": "fresh",
                "price": 42,
                "currency": "USD",
                "ingredients": None,
            }
        ]
    )
    envelope = gateway.invoke(
        "get_products",
        {"product_ids": ["SF001"]},
        caller,
    )
    assert envelope.status == "ok"
    assert envelope.data["engine_ran"] is False
    row = envelope.data["products"][0]
    assert row["product_id"] == "SF001"
    assert row["ingredients"] == "NOT_AVAILABLE"


def test_compare_and_explanation_are_digest_only(dog, caller, engine_guard):
    previous = _save(dog.dog_id, "sig-a", chicken=True)
    current = _save(dog.dog_id, "sig-b", chicken=False, exclusions=["chicken"])
    compared = invoke_tool(
        "compare_analyses",
        {
            "dog_id": dog.dog_id,
            "previous_analysis_id": previous.analysis_id,
            "new_analysis_id": current.analysis_id,
        },
        caller,
    )
    assert compared.status == "ok"
    assert compared.data["engine_ran"] is False
    assert compared.data["llm_used"] is False
    assert compared.data["explanation"]["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA
    explained = invoke_tool(
        "get_recalculation_explanation",
        {"dog_id": dog.dog_id},
        caller,
    )
    assert explained.status == "ok"
    assert explained.data["engine_ran"] is False
    assert explained.data["explanation"]["schema"] == WAGGY_RECALCULATION_EXPLANATION_SCHEMA
    assert explained.data["explanation"]["llm_used"] is False
    assert "SF002" in compared.data["explanation"]["recommendation_changes"]["balanced"]["removed_product_ids"]


def test_propose_preference_validates_and_does_not_persist(dog, caller, engine_guard):
    envelope = invoke_tool(
        "propose_preference",
        {"type": "ingredient_exclusion", "value": "Chicken", "dog_id": dog.dog_id, "user_text": "I don't want chicken."},
        caller,
    )
    assert envelope.status == "ok"
    assert envelope.data["persisted"] is False
    assert envelope.data["recomputed"] is False
    assert envelope.data["requires_authorized_mutation"] is True
    assert envelope.data["candidate"]["value"] == "chicken"
    assert envelope.data["candidate"]["scientific"] is False
    assert "application-authorized" in envelope.data["note"]
    assert preferences_for(dog.dog_id) == []
    budget = invoke_tool("propose_preference", {"type": "monthly_budget", "value": 100}, caller)
    assert budget.status == "ok"
    assert budget.data["candidate"]["value"] == 100.0
    ranking = invoke_tool(
        "propose_preference",
        {"type": "ingredient_exclusion", "value": "make this product #1"},
        caller,
    )
    assert ranking.status == "error"
    assert ranking.errors[0].code == INVALID_PREFERENCE
    assert preferences_for(dog.dog_id) == []
