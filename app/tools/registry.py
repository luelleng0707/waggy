"""Explicit allowlist. No dynamic imports, eval, or model-supplied callables."""

from __future__ import annotations

from dataclasses import dataclass

from app.tools.models import (
    AnalysisScopedInput,
    CompareAnalysesInput,
    GetDogProfileInput,
    GetProductsInput,
    ProposePreferenceInput,
)
from app.tools.version import TOOL_SCHEMA_VERSION, TOOL_VERSION


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    input_model: type
    handler: str
    roles: frozenset[str]
    dog_scoped: bool
    version: str = TOOL_VERSION
    schema_version: str = TOOL_SCHEMA_VERSION
    mutates: bool = False


# Executable Ω17.4 tools. Distinct from Ω11 FUTURE_TOOL_REGISTRY (descriptors only).
REGISTERED_TOOLS: dict[str, RegisteredTool] = {
    "get_dog_profile": RegisteredTool(
        name="get_dog_profile",
        description="Return an authorized dog profile. Does not run the engine.",
        input_model=GetDogProfileInput,
        handler="get_dog_profile",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "analyze_health": RegisteredTool(
        name="analyze_health",
        description="Return the stored canonical health-analysis slice. Does not reason scientifically.",
        input_model=AnalysisScopedInput,
        handler="analyze_health",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "calculate_nutrition": RegisteredTool(
        name="calculate_nutrition",
        description="Return stored canonical nutrition targets. Does not calculate a second model.",
        input_model=AnalysisScopedInput,
        handler="calculate_nutrition",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "get_products": RegisteredTool(
        name="get_products",
        description="Return approved catalog product facts with narrow filters only.",
        input_model=GetProductsInput,
        handler="get_products",
        roles=frozenset({"customer", "groomer", "business", "developer"}),
        dog_scoped=False,
    ),
    "get_package_options": RegisteredTool(
        name="get_package_options",
        description="Return stored canonical package options. Does not run a second optimizer.",
        input_model=AnalysisScopedInput,
        handler="get_package_options",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "get_recalculation_explanation": RegisteredTool(
        name="get_recalculation_explanation",
        description="Return waggy_recalculation_explanation.v1 from stored digests. No LLM.",
        input_model=CompareAnalysesInput,
        handler="get_recalculation_explanation",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "compare_analyses": RegisteredTool(
        name="compare_analyses",
        description="Diff two stored analysis digests. engine_ran is always false.",
        input_model=CompareAnalysesInput,
        handler="compare_analyses",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=True,
    ),
    "propose_preference": RegisteredTool(
        name="propose_preference",
        description="Validate a structured preference candidate. Does not persist or recompute.",
        input_model=ProposePreferenceInput,
        handler="propose_preference",
        roles=frozenset({"customer", "groomer", "developer"}),
        dog_scoped=False,
    ),
}

FORBIDDEN_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "run_sql",
        "execute_python",
        "read_file",
        "write_file",
        "edit_warehouse",
        "modify_scientific_fact",
        "set_package",
        "set_ranking",
        "override_optimizer",
        "create_product",
        "modify_product",
        "set_preferences",
        "recompute",
        "eval",
        "exec",
    }
)

FORBIDDEN_ARGUMENT_KEYS: frozenset[str] = frozenset(
    {
        "sql",
        "query_sql",
        "path",
        "file_path",
        "filesystem",
        "python",
        "code",
        "eval",
        "exec",
        "warehouse_path",
        "csv_path",
        "expression",
    }
)


def registered_tool(name: str) -> RegisteredTool | None:
    return REGISTERED_TOOLS.get(str(name or "").strip())


def registered_names() -> tuple[str, ...]:
    return tuple(REGISTERED_TOOLS)
