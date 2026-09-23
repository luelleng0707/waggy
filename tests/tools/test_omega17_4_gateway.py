"""Ω17.4 gateway allowlist and typed input validation."""

from __future__ import annotations

from app.tools.errors import INVALID_TOOL_INPUT, TOOL_NOT_ALLOWED, UNKNOWN_TOOL
from app.tools.gateway import WaggyToolGateway, invoke_tool
from app.tools.registry import FORBIDDEN_TOOL_NAMES, registered_names
from app.tools.version import TOOL_SCHEMA_VERSION, TOOL_VERSION, WAGGY_TOOL_RESULT_SCHEMA


def test_registry_is_exactly_the_eight_read_tools():
    assert registered_names() == (
        "get_dog_profile",
        "analyze_health",
        "calculate_nutrition",
        "get_products",
        "get_package_options",
        "get_recalculation_explanation",
        "compare_analyses",
        "propose_preference",
    )
    listed = WaggyToolGateway().list_registered_tools()
    assert [item["name"] for item in listed] == list(registered_names())
    assert all(item["mutates"] is False for item in listed)
    assert all(item["version"] == TOOL_VERSION for item in listed)
    assert all(item["schema_version"] == TOOL_SCHEMA_VERSION for item in listed)


def test_unknown_tool_is_rejected():
    envelope = invoke_tool("run_optimizer", {"dog_id": "d1"})
    assert envelope.status == "error"
    assert envelope.schema_name == WAGGY_TOOL_RESULT_SCHEMA
    assert envelope.scientific is False
    assert envelope.llm_used is False
    assert envelope.errors[0].code == UNKNOWN_TOOL
    dumped = envelope.model_dump(by_alias=True)
    assert dumped["schema"] == WAGGY_TOOL_RESULT_SCHEMA
    text = str(dumped)
    assert "Traceback" not in text
    assert "sqlite" not in text.lower()


def test_forbidden_tool_names_are_never_callable():
    for name in sorted(FORBIDDEN_TOOL_NAMES):
        envelope = invoke_tool(name, {})
        assert envelope.status == "error", name
        assert envelope.errors[0].code == TOOL_NOT_ALLOWED, name


def test_extra_fields_are_rejected():
    envelope = invoke_tool("get_dog_profile", {"dog_id": "dog-1", "hack": True})
    assert envelope.status == "error"
    assert envelope.errors[0].code == INVALID_TOOL_INPUT


def test_sql_and_path_arguments_are_rejected():
    envelope = invoke_tool("get_products", {"sql": "SELECT * FROM dogs", "dog_id": "dog-1"})
    assert envelope.status == "error"
    assert envelope.errors[0].code == INVALID_TOOL_INPUT
    assert envelope.errors[0].field == "sql"
    path_env = invoke_tool("get_products", {"path": "warehouse/biology.csv", "product_ids": ["SF001"]})
    assert path_env.status == "error"
    assert path_env.errors[0].code == INVALID_TOOL_INPUT


def test_set_preferences_is_not_a_registered_tool():
    envelope = invoke_tool("set_preferences", {"dog_id": "dog-1", "type": "ingredient_exclusion", "value": "chicken"})
    assert envelope.status == "error"
    assert envelope.errors[0].code == TOOL_NOT_ALLOWED
