"""Runtime stage-trace model used by orchestrator execution."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StageTrace:
    stage_name: str
    input_summary: str
    output_summary: str
    runtime_ms: float
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    evidence_collected_count: str = ""


@dataclass(frozen=True)
class RuntimeTrace:
    run_id: str
    stages: tuple[StageTrace, ...] = field(default_factory=tuple)
