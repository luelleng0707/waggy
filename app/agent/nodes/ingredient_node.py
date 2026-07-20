from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.ingredient_engine import map_ingredients


class IngredientNode(FormulaNode):
    """Wraps ingredient_engine.map_ingredients — no dose math changes."""

    id = "ingredient"
    formula_id = "NUTRIENT_TARGET_V2_1"
    dependencies = ["profile", "risk", "nutrition"]
    produces = ["ingredients"]
    consumes = ["risk"]
    tables = ["condition_ingredients", "ingredient_evidence", "ingredient_mechanisms"]

    def execute(self, context: ExecutionContext) -> None:
        risks = context.require_output("risk").get("risks") or []
        weight = float(context.profile.weight_kg or 10)
        ingredients = map_ingredients(risks, weight, context.repository)
        context.set_output(self.id, {"ingredients": ingredients, "count": len(ingredients)})
        self.emit_lookup(
            context,
            table="condition_ingredients",
            rows=len(ingredients),
            selection_rule="map_ingredients",
        )
        self.emit_step(
            context,
            name="map_ingredients",
            expression="map_ingredients(risks, weight_kg, repo)",
            inputs={"weight_kg": weight, "risk_count": len(risks)},
            result={"ingredient_count": len(ingredients)},
        )
