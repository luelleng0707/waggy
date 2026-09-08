"""Future tool registry shape. Does not execute tools."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import OperationType
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION, DEFAULT_TOOL_VERSION


class ToolRegistryEntry(BaseModel):
    """Capability descriptor for Ω13. No invoke/execute method."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    tool_version: str = DEFAULT_TOOL_VERSION
    schema_version: str = AGENT_CONTRACT_SCHEMA_VERSION
    operation: OperationType
    permission: str
    input_schema_name: str
    output_schema_name: str


FUTURE_TOOL_REGISTRY: tuple[ToolRegistryEntry, ...] = (
    ToolRegistryEntry(
        name="analyze_health",
        description="Warehouse-backed preventative health findings for one dog.",
        operation=OperationType.READ_CALCULATE,
        permission="analysis:health",
        input_schema_name="CanonicalDogInput",
        output_schema_name="HealthAnalysisResult",
    ),
    ToolRegistryEntry(
        name="calculate_nutrition",
        description="Deterministic nutrient requirement profile for one dog.",
        operation=OperationType.READ_CALCULATE,
        permission="analysis:nutrition",
        input_schema_name="CanonicalDogInput",
        output_schema_name="NutritionAnalysisResult",
    ),
    ToolRegistryEntry(
        name="optimize_bundles",
        description="Exhaustive PACKAGE_OPTIMIZER_V2_1 bundle search for one dog.",
        operation=OperationType.READ_CALCULATE,
        permission="analysis:bundles",
        input_schema_name="CanonicalDogInput",
        output_schema_name="BundleSearchResult",
    ),
    ToolRegistryEntry(
        name="generate_report",
        description="Presentation projection of a completed canonical analysis.",
        operation=OperationType.PROJECTION,
        permission="analysis:report",
        input_schema_name="CanonicalAnalysis",
        output_schema_name="ReportProjection",
    ),
)

FUTURE_TOOL_NAMES: tuple[str, ...] = tuple(entry.name for entry in FUTURE_TOOL_REGISTRY)

# Authoring WRITE routes stay off this registry.
EXCLUDED_FROM_AGENT_SURFACE: tuple[str, ...] = (
    "POST /api/v1/authoring/evidence",
    "POST /api/v1/authoring/evidence/{id}/materialize",
)
