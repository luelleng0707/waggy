from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.formulas.stages.optimization import run_optimization_stage


class ProductNode(FormulaNode):
    id = "product"
    formula_id = "PRODUCT_MATCH_V2_1"
    dependencies = ["profile", "nutrition"]
    produces = ["products", "feeding_plan", "reports"]
    consumes = ["nutrition"]
    tables = ["products", "product_components", "product_pricing", "product_feeding_rules"]

    def execute(self, context: ExecutionContext) -> None:
        nutrition = context.require_output("nutrition").get("nutrition") or {}
        products, reports, trace = run_optimization_stage(
            context.repository, context.profile, nutrition
        )
        context.append_pipeline(trace)
        context.set_output(
            self.id,
            {
                "products": products,
                "feeding_plan": products.get("feeding_plan", {}),
                "reports": reports,
                "trace": trace.model_dump(),
            },
        )
        self.emit_lookup(
            context,
            table="product_catalog+components",
            rows=len(reports),
            selection_rule="run_optimization_stage",
        )
        self.emit_step(
            context,
            name="run_optimization_stage",
            result={"reports": len(reports)},
        )
