from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class ConfidenceNode(FormulaNode):
    id = "confidence"
    formula_id = "CONFIDENCE_V1"
    dependencies = ["risk"]
    produces = ["confidence_summary"]
    consumes = ["risk"]
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        risks = context.require_output("risk").get("risks") or []
        confs = [
            {
                "condition": r.get("condition_name"),
                "confidence_percent": r.get("confidence_percent"),
                "risk_percent": r.get("risk_percent"),
            }
            for r in risks
        ]
        context.set_output(
            self.id,
            {
                "confidence_summary": confs,
                "count": len(confs),
            },
        )
        self.emit_step(context, name="extract_confidence", result={"count": len(confs)})
