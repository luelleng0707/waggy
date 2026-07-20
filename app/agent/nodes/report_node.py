from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class ReportNode(FormulaNode):
    id = "report"
    formula_id = "REPORT_V1"
    dependencies = ["product", "assessment"]
    produces = ["reports"]
    consumes = ["product"]
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        product = context.require_output("product")
        reports = product.get("reports") or []
        context.set_output(self.id, {"reports": reports, "count": len(reports)})
        self.emit_step(context, name="collect_wellness_reports", result={"count": len(reports)})
