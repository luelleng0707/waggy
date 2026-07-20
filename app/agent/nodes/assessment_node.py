from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class AssessmentNode(FormulaNode):
    id = "assessment"
    formula_id = "ASSESSMENT_PROJECT_V1"
    dependencies = ["biology", "risk", "nutrition", "activity", "product", "package"]
    produces = ["assessment_summary"]
    consumes = ["biology", "risk", "nutrition", "activity", "product"]
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        risk = context.require_output("risk")
        nutrition = context.require_output("nutrition")
        product = context.require_output("product")
        summary = {
            "risk_count": len(risk.get("risks") or []),
            "nutrient_target_count": len(nutrition.get("nutrient_targets") or []),
            "report_count": len(product.get("reports") or []),
            "has_biology": bool(context.get_output("biology")),
            "has_management": bool(context.get_output("activity")),
        }
        context.set_output(self.id, {"assessment_summary": summary, **summary})
        self.emit_step(context, name="project_assessment_summary", result=summary)
