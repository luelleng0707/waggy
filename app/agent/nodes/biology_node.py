from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.stages.biological import run_biological_stage


class BiologyNode(FormulaNode):
    id = "biology"
    formula_id = "BIOLOGY_V2_1"
    dependencies = ["profile", "breed"]
    produces = ["biology"]
    consumes = ["profile", "breed"]
    tables = ["breeds", "trait_purposes", "environmental_matrices"]

    def execute(self, context: ExecutionContext) -> None:
        biology, trace = run_biological_stage(context.repository, context.profile)
        context.append_pipeline(trace)
        context.set_output(self.id, {"biology": biology, "trace": trace.model_dump()})
        self.emit_lookup(context, table="breeds", selection_rule="run_biological_stage", rows=None)
        self.emit_step(
            context,
            name="run_biological_stage",
            expression="run_biological_stage(repo, profile)",
            result={"keys": sorted(biology.keys()) if isinstance(biology, dict) else None},
        )
