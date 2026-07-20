from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.stages.nutrition import run_nutrition_stage


class NutritionNode(FormulaNode):
    id = "nutrition"
    formula_id = "NUTRITION_V2_1"
    dependencies = ["profile", "epidemiology"]
    produces = ["nutrition", "nutrient_targets"]
    consumes = ["epidemiology"]
    tables = ["condition_ingredients"]

    def execute(self, context: ExecutionContext) -> None:
        epidemiology = context.require_output("epidemiology").get("epidemiology") or {}
        nutrition, trace = run_nutrition_stage(
            context.repository, context.profile, epidemiology
        )
        context.append_pipeline(trace)
        targets = nutrition.get("nutrient_targets") or []
        context.set_output(
            self.id,
            {"nutrition": nutrition, "nutrient_targets": targets, "trace": trace.model_dump()},
        )
        self.emit_lookup(
            context,
            table="condition_ingredients",
            rows=len(targets),
            selection_rule="priority_conditions join",
        )
        self.emit_step(
            context,
            name="run_nutrition_stage",
            expression="run_nutrition_stage(repo, profile, epidemiology)",
            result={"targets": len(targets)},
        )
