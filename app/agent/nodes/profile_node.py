from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class ProfileNode(FormulaNode):
    id = "profile"
    formula_id = "PROFILE_V1"
    dependencies: list[str] = []
    produces = ["profile"]
    consumes = []
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        p = context.profile
        payload = {
            "profile": p.model_dump(),
            "name": p.name,
            "primary_breed": p.primary_breed,
            "secondary_breed": p.secondary_breed,
            "age_years": p.age_years,
            "weight_kg": p.weight_kg,
        }
        context.inputs["profile"] = payload
        context.set_output(self.id, payload)
        self.emit_step(context, name="load_profile", result=p.name)
