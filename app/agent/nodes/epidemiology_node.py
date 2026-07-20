from __future__ import annotations

from typing import Any

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.stages.epidemiology import run_epidemiology_stage


class EpidemiologyNode(FormulaNode):
    id = "epidemiology"
    formula_id = "EPIDEMIOLOGY_V2_1"
    dependencies = ["profile", "biology", "risk"]
    produces = ["epidemiology", "priority_conditions"]
    consumes = ["biology", "risk"]
    tables = ["breed_conditions", "trait_condition_tables"]

    def execute(self, context: ExecutionContext) -> None:
        biology = context.require_output("biology").get("biology") or {}
        health_risk = context.require_output("risk").get("health_risk") or {}

        epidemiology, trace = run_epidemiology_stage(
            context.repository, context.profile, biology
        )
        # Exact merge logic from engine.py — preserve priority_conditions from RISK_V2_1
        if health_risk.get("risks"):
            epidemiology = {
                **epidemiology,
                "priority_conditions": [
                    {
                        "condition": r.get("condition_name"),
                        "condition_key": r.get("condition_key"),
                        "prevalence": float(
                            r.get("risk_decimal")
                            or (float(r.get("risk_percent") or 0) / 100.0)
                        ),
                        "weighted_priority_score": float(
                            r.get("risk_decimal")
                            or (float(r.get("risk_percent") or 0) / 100.0)
                        ),
                        "risk_percent": r.get("risk_percent"),
                        "confidence_percent": r.get("confidence_percent"),
                    }
                    for r in health_risk["risks"]
                ],
            }
        context.append_pipeline(trace)
        context.set_output(
            self.id,
            {
                "epidemiology": epidemiology,
                "priority_conditions": epidemiology.get("priority_conditions") or [],
                "trace": trace.model_dump(),
            },
        )
        self.emit_step(
            context,
            name="run_epidemiology_stage+merge_risk_priorities",
            result={"priorities": len(epidemiology.get("priority_conditions") or [])},
        )
