from __future__ import annotations

from typing import Any

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.state import PipelineTraceEntry


class ActivityNode(FormulaNode):
    """Former engine._run_management_stage — lifestyle mapping only."""

    id = "activity"
    formula_id = "ACTIVITY_V2_1"
    dependencies = ["epidemiology"]
    produces = ["management", "lifestyle_requirements"]
    consumes = ["epidemiology"]
    tables = ["condition_activities"]

    def execute(self, context: ExecutionContext) -> None:
        epidemiology = context.require_output("epidemiology").get("epidemiology") or {}
        activities_df = context.repository.condition_activities()
        priorities = epidemiology.get("priority_conditions", [])
        lifestyle: list[dict[str, Any]] = []

        if not activities_df.empty and priorities:
            top_conditions = [p["condition"] for p in priorities[:10]]
            cond_col = "condition" if "condition" in activities_df.columns else "condition_name"
            hits = activities_df[activities_df[cond_col].isin(top_conditions)]
            lifestyle = hits.to_dict(orient="records")

        payload = {"lifestyle_requirements": lifestyle}
        trace = PipelineTraceEntry(
            stage="management",
            message="Mapped lifestyle interventions for ranked conditions",
            record_count=len(lifestyle),
        )
        context.append_pipeline(trace)
        context.set_output(self.id, {"management": payload, "lifestyle_requirements": lifestyle})
        self.emit_lookup(
            context,
            table="condition_activities",
            rows=len(lifestyle),
            selection_rule="top-10 priority conditions",
        )
        self.emit_step(context, name="map_lifestyle", result={"rows": len(lifestyle)})
