"""Typed boundary errors for future tool calls."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import ToolErrorCode

# Engine scientific gap token. Equivalent to ToolErrorCode.NOT_AVAILABLE.
ENGINE_NOT_AVAILABLE = "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE"


class ToolError(BaseModel):
    """Machine-readable failure. Not a prose 'AI could not answer'."""

    model_config = ConfigDict(extra="forbid")

    code: ToolErrorCode
    message: str
    fields: list[str] = Field(default_factory=list)
    details: str | None = None

    def to_json_dict(self) -> dict[str, object]:
        return self.model_dump(mode="json")


def missing_required_input(fields: list[str], *, message: str | None = None) -> ToolError:
    named = ", ".join(fields) if fields else "required fields"
    return ToolError(
        code=ToolErrorCode.MISSING_REQUIRED_INPUT,
        message=message or f"Missing required input: {named}",
        fields=list(fields),
    )


def invalid_input(fields: list[str], *, message: str | None = None) -> ToolError:
    named = ", ".join(fields) if fields else "input"
    return ToolError(
        code=ToolErrorCode.INVALID_INPUT,
        message=message or f"Invalid input: {named}",
        fields=list(fields),
    )
