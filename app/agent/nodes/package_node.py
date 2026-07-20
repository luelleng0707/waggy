from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class PackageNode(FormulaNode):
    """
    Packages are finalized in ExportNode via assemble_frontend_response
    (same as pre-Phase-3 engine) to preserve byte-compatible JSON.
    This node only marks readiness + records parameter mirrors.
    """

    id = "package"
    formula_id = "PACKAGE_OPTIMIZER_V2_1"
    dependencies = ["product", "ingredient", "risk"]
    produces = ["package_ready"]
    consumes = ["product", "ingredient", "risk"]
    tables = ["package_tiers"]

    def execute(self, context: ExecutionContext) -> None:
        score_weights = context.parameters.group("score_weights")
        product = context.require_output("product")
        context.set_output(
            self.id,
            {
                "package_ready": True,
                "deferred_to": "export",
                "score_weights": score_weights,
                "report_count": len(product.get("reports") or []),
                "ingredient_count": (context.get_output("ingredient") or {}).get("count"),
            },
        )
        self.emit_step(
            context,
            name="defer_packages_to_export",
            expression="assemble_frontend_response → build_wellness_packages (parity)",
            inputs={"score_weights": score_weights},
            result={"package_ready": True},
        )
