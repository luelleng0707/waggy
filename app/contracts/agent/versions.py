"""Version stamp. Reuses ALGORITHM_VERSION; does not invent a second engine version."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.agent.version import ALGORITHM_VERSION, ENGINE_NAME

AGENT_CONTRACT_SCHEMA_VERSION = "1.0.0"
DEFAULT_TOOL_VERSION = "1.0.0"


class VersionStamp(BaseModel):
    """What exact engine and data produced (or will produce) an answer."""

    model_config = ConfigDict(extra="forbid")

    engine_name: str = Field(default=ENGINE_NAME)
    engine_version: str = Field(
        default=ALGORITHM_VERSION,
        description="Must remain app.agent.version.ALGORITHM_VERSION (currently 2.1.0).",
    )
    warehouse_version: str | None = Field(
        default=None,
        description="DataRepository.version / platform manifest version. Not invented here.",
    )
    csv_hash: str | None = Field(
        default=None,
        description="DataRepository.csv_hash when known.",
    )
    schema_version: str = Field(default=AGENT_CONTRACT_SCHEMA_VERSION)
    tool_version: str | None = Field(
        default=None,
        description="Reserved for Ω13 tool envelopes. Registry entries already carry 1.0.0.",
    )
    analysis_version: str | None = Field(
        default=None,
        description="When sourced from analyze, equals engine_version.",
    )


def runtime_engine_version() -> str:
    return ALGORITHM_VERSION
