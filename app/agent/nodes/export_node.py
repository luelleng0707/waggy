"""ExportNode — legacy JSON compatibility via assemble_frontend_response."""

from __future__ import annotations

import time

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.response_assembler import assemble_frontend_response


class ExportNode(FormulaNode):
    """
    Maps FormulaGraph outputs into the public analyze JSON contract.
    Clinical fields must match the pre-graph engine path.
    """

    id = "export"
    formula_id = "EXPORT_LEGACY_V1"
    dependencies = [
        "biology",
        "epidemiology",
        "nutrition",
        "activity",
        "product",
        "risk",
        "report",
        "trace",
        "validation",
    ]
    produces = ["legacy_json"]
    consumes = ["biology", "epidemiology", "nutrition", "activity", "product", "risk", "report"]
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        biology = context.require_output("biology").get("biology") or {}
        epidemiology = context.require_output("epidemiology").get("epidemiology") or {}
        nutrition = context.require_output("nutrition").get("nutrition") or {}
        management = context.require_output("activity").get("management") or {
            "lifestyle_requirements": []
        }
        product = context.require_output("product")
        health_risk = context.require_output("risk").get("health_risk") or {}
        reports = context.require_output("report").get("reports") or product.get("reports") or []
        feeding_plan = product.get("feeding_plan") or {}

        # Stage timings from node metrics (additive debug only)
        stage_timings_ms = {
            "biology": context.metrics.get("node.biology.ms"),
            "health_risk": context.metrics.get("node.risk.ms"),
            "epidemiology": context.metrics.get("node.epidemiology.ms"),
            "management": context.metrics.get("node.activity.ms"),
            "nutrition": context.metrics.get("node.nutrition.ms"),
            "optimization": context.metrics.get("node.product.ms"),
        }
        # Drop Nones for cleaner debug
        stage_timings_ms = {k: v for k, v in stage_timings_ms.items() if v is not None}

        t_asm = time.perf_counter()
        analyze = assemble_frontend_response(
            profile=context.profile,
            biology=biology,
            epidemiology=epidemiology,
            nutrition=nutrition,
            reports=reports,
            feeding_plan=feeding_plan,
            management=management,
            pipeline_trace=[entry.model_dump() for entry in context.pipeline_trace],
            repo=context.repository,
            health_risk=health_risk,
            stage_timings_ms=stage_timings_ms,
        )
        asm_ms = round((time.perf_counter() - t_asm) * 1000, 3)
        stage_timings_ms["assembly"] = asm_ms
        total = sum(v for v in stage_timings_ms.values() if isinstance(v, (int, float)))
        stage_timings_ms["total_pipeline"] = round(total, 3)
        context.metrics["stage_timings_ms"] = stage_timings_ms

        debug = analyze.get("debug") if isinstance(analyze.get("debug"), dict) else {}
        debug["stage_timings_ms"] = stage_timings_ms
        # Additive: formula graph for Validation Console (does not alter clinical fields)
        debug["formula_graph"] = context.debug.get("formula_graph") or {}
        debug["formula_execution_trace"] = context.execution_trace
        debug["assessment_validation"] = context.get_output("validation") or {}
        analyze["debug"] = debug

        context.set_output(
            self.id,
            {
                "legacy_json": analyze,
                "debug": debug,
            },
        )
        self.emit_step(
            context,
            name="assemble_frontend_response",
            expression="legacy compatibility adapter",
            result={"keys": sorted(analyze.keys())[:30], "assembly_ms": asm_ms},
        )
