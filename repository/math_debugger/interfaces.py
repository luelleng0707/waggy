"""Interfaces for Ω9.2 math debugger."""

from __future__ import annotations

from typing import Protocol

from repository.models.runtime import EvidenceGraph

from .models import ExecutionTrace, FormulaConstantAuditRow


class FormulaTraceBuilder(Protocol):
    def build(self, evidence_graph: EvidenceGraph) -> ExecutionTrace:
        """Build full deterministic formula trace for mathematics runtime execution."""


class ReplayEngine(Protocol):
    def replay(self, evidence_graph: EvidenceGraph) -> ExecutionTrace:
        """Replay the real formulas and produce deterministic trace output."""


class FormulaConstantValidator(Protocol):
    def audit(self) -> tuple[FormulaConstantAuditRow, ...]:
        """Audit mathematical constants in code for documentation provenance."""
