"""Bounded agent context. Not a warehouse dump and not an everything bag."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import ActorRole
from app.contracts.agent.registry import FUTURE_TOOL_NAMES


class AgentActor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    actor_id: str
    role: ActorRole


class AgentContext(BaseModel):
    """What a future AI agent may receive. Authorization is not implemented here.

    Must not contain: entire warehouse, all customers, secrets, API keys,
    authoring credentials, raw tables, or filesystem paths.
    """

    model_config = ConfigDict(extra="forbid")

    actor: AgentActor
    authorized_subject_id: str | None = None
    current_dog_id: str | None = None
    current_analysis_id: str | None = None
    current_view: str | None = None
    session_id: str | None = None
    available_tools: list[str] = Field(default_factory=lambda: list(FUTURE_TOOL_NAMES))
    correlation_id: str | None = None
