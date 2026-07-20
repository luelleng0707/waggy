"""Inference value models — explainable outputs without owning API routes."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class InferredValue:
    """Standard envelope for inference outputs (future wiring)."""

    value: Any
    confidence: float
    formula_id: str
    source: str
    reason: str = ""
    unit: str | None = None
    trace: tuple[dict[str, Any], ...] = ()
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["trace"] = list(self.trace)
        return d


@dataclass
class ModifierStep:
    """One step in a risk / score modifier ledger (RISK_TRACE_V1)."""

    name: str
    op: str  # baseline | multiply | add | set
    value: Any
    unit: str | None = None
    source: str | None = None
    formula_id: str | None = None
    traceable: bool = True
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


NOT_TRACEABLE = "NOT CURRENTLY TRACEABLE"
