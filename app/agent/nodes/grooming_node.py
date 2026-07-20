from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class GroomingNode(FormulaNode):
    id = "grooming"
    formula_id = "GROOMING_V1"
    dependencies = ["profile", "biology"]
    produces = ["grooming_defs"]
    consumes = ["profile", "biology"]
    tables = ["grooming_observation_defs"]

    def execute(self, context: ExecutionContext) -> None:
        df = context.repository.grooming_observation_defs()
        rows = df.to_dict(orient="records") if not df.empty else []
        context.set_output(self.id, {"grooming_defs": rows, "count": len(rows)})
        self.emit_lookup(context, table="grooming_observation_defs", rows=len(rows))
        self.emit_step(context, name="load_grooming_defs", result={"count": len(rows)})
