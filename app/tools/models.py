"""Typed tool inputs, caller identity, and the shared result envelope."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.ai.models import RoleName
from app.tools.version import TOOL_SCHEMA_VERSION, TOOL_VERSION, WAGGY_TOOL_RESULT_SCHEMA

PreferenceCandidateType = Literal["ingredient_exclusion", "monthly_budget"]
ToolStatus = Literal["ok", "error"]
ToolActor = Literal["user", "ai"]


class ToolCaller(BaseModel):
    """Application-authorized caller. The model does not own this object."""

    model_config = ConfigDict(extra="forbid")

    role: RoleName = "customer"
    owner_id: str | None = "prototype-local"
    authorized_dog_ids: list[str] | None = None
    actor: ToolActor = "ai"


class ToolMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    version: str = TOOL_VERSION
    schema_version: str = TOOL_SCHEMA_VERSION


class ToolRequestMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str


class ToolErrorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    field: str | None = None


class ToolEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_TOOL_RESULT_SCHEMA, alias="schema")
    tool: ToolMeta
    request: ToolRequestMeta
    status: ToolStatus
    data: dict[str, Any] | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    errors: list[ToolErrorItem] = Field(default_factory=list)
    scientific: bool = False
    llm_used: bool = False


class ToolInvokeRequest(BaseModel):
    """HTTP dispatcher payload. Per-tool arguments are validated inside the gateway."""

    model_config = ConfigDict(extra="forbid")

    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    role: RoleName = "customer"
    owner_id: str | None = "prototype-local"
    authorized_dog_ids: list[str] | None = None
    request_id: str | None = None
    actor: ToolActor = "ai"


class DogIdInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str


class AnalysisScopedInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str
    analysis_id: str | None = None
    analysis_signature: str | None = None


class GetDogProfileInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str
    include_preferences: bool = False


class GetProductsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str | None = None
    product_ids: list[str] | None = None
    product_type: str | None = None
    category: str | None = None
    limit: int = 25


class CompareAnalysesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str
    previous_analysis_id: str | None = None
    new_analysis_id: str | None = None
    previous_signature: str | None = None
    new_signature: str | None = None


class ProposePreferenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: PreferenceCandidateType
    value: str | float | int
    dog_id: str | None = None
    user_text: str | None = None
