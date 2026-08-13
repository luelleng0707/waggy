"""Trace builder for Ω6 optimization runtime."""

from __future__ import annotations

from .models import OptimizationStageTrace, OptimizationTrace


class DeterministicTraceBuilder:
    def build(self, run_id: str, stages: tuple[dict[str, object], ...]) -> OptimizationTrace:
        trace_items: list[OptimizationStageTrace] = []
        for stage in stages:
            trace_items.append(
                OptimizationStageTrace(
                    stage_name=str(stage.get("stage_name", "")),
                    formula_ids=tuple(sorted(set(stage.get("formula_ids", tuple())))),
                    input_summary=str(stage.get("input_summary", "")),
                    output_summary=str(stage.get("output_summary", "")),
                    warehouse_row_ids=tuple(sorted(set(stage.get("warehouse_row_ids", tuple())))),
                    elapsed_ms=float(stage.get("elapsed_ms", 0.0)),
                )
            )
        return OptimizationTrace(run_id=run_id, stages=tuple(trace_items))
