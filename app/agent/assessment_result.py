"""AssessmentResult — typed envelope over ExecutionContext outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agent.execution_context import ExecutionContext
from app.agent.state import DogProfileInput


@dataclass
class AssessmentResult:
    profile: DogProfileInput
    biology: dict[str, Any] = field(default_factory=dict)
    health: dict[str, Any] = field(default_factory=dict)
    epidemiology: dict[str, Any] = field(default_factory=dict)
    nutrition: dict[str, Any] = field(default_factory=dict)
    activities: dict[str, Any] = field(default_factory=dict)
    grooming: dict[str, Any] = field(default_factory=dict)
    products: dict[str, Any] = field(default_factory=dict)
    packages: dict[str, Any] = field(default_factory=dict)
    assessment: dict[str, Any] = field(default_factory=dict)
    reports: list[Any] = field(default_factory=list)
    validation: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    confidence: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)
    performance: dict[str, Any] = field(default_factory=dict)
    debug: dict[str, Any] = field(default_factory=dict)
    # Legacy public API payload (FRONTEND_LAYOUT_SPEC / analyze JSON)
    legacy_json: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_context(cls, context: ExecutionContext) -> "AssessmentResult":
        biology = context.get_output("biology") or {}
        risk = context.get_output("risk") or {}
        epi = context.get_output("epidemiology") or {}
        nutrition = context.get_output("nutrition") or {}
        activity = context.get_output("activity") or {}
        grooming = context.get_output("grooming") or {}
        product = context.get_output("product") or {}
        package = context.get_output("package") or {}
        assessment = context.get_output("assessment") or {}
        report = context.get_output("report") or {}
        validation = context.get_output("validation") or {}
        evidence = context.get_output("evidence") or {}
        confidence = context.get_output("confidence") or {}
        export = context.get_output("export") or {}
        trace_out = context.get_output("trace") or {}

        return cls(
            profile=context.profile,
            biology=biology.get("biology") or biology,
            health=risk,
            epidemiology=epi.get("epidemiology") or epi,
            nutrition=nutrition,
            activities=activity,
            grooming=grooming,
            products=product,
            packages=package,
            assessment=assessment,
            reports=report.get("reports") or product.get("reports") or [],
            validation=validation,
            evidence=evidence,
            confidence=confidence,
            trace={
                "execution": context.execution_trace,
                "lookups": context.lookup_trace,
                "pipeline": [e.model_dump() for e in context.pipeline_trace],
                "dependency_graph": context.dependency_graph,
                "graph_order": context.runtime.get("graph_order"),
                **(trace_out if isinstance(trace_out, dict) else {}),
            },
            performance={"metrics": context.metrics, "stage_timings_ms": context.metrics.get("stage_timings_ms")},
            debug={**context.debug, **(export.get("debug") or {})},
            legacy_json=export.get("legacy_json") or {},
        )

    def to_analyze_dict(self) -> dict[str, Any]:
        """Public API: legacy analyze JSON (byte-compatible clinical fields)."""
        return self.legacy_json
