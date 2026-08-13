from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode
from app.agent.state import PipelineTraceEntry
from app.formulas.stages.health_risk import compute_risks


class RiskNode(FormulaNode):
    """Wraps health_risk.compute_risks — no math changes."""

    id = "risk"
    formula_id = "RISK_V2_1"
    dependencies = ["profile", "breed", "biology"]
    produces = ["risks", "meta"]
    consumes = ["profile", "biology"]
    tables = [
        "breed_conditions",
        "trait_condition_tables",
        "trait_interactions",
        "trait_benefits",
        "mixed_breed_matrix",
    ]

    def execute(self, context: ExecutionContext) -> None:
        # Parameters available on context for future wiring; compute_risks unchanged.
        _ = context.param("risk_interaction", "INTERACTION_MIN", 0.8)
        _ = context.param("risk_interaction", "INTERACTION_MAX", 1.2)

        health_risk = compute_risks(context.repository, context.profile)
        risks = health_risk.get("risks") or []
        context.append_pipeline(
            PipelineTraceEntry(
                stage="health_risk",
                message="Computed trait/overlap/benefit/significance risks (JS parity)",
                record_count=len(risks),
                metadata=health_risk.get("meta") or {},
            )
        )
        context.set_output(
            self.id,
            {
                "health_risk": health_risk,
                "risks": risks,
                "meta": health_risk.get("meta") or {},
            },
        )
        self.emit_lookup(
            context,
            table="breed_conditions+trait_conditions",
            selection_rule="compute_risks",
            rows=len(risks),
        )
        self.emit_step(
            context,
            name="compute_risks",
            expression="compute_risks(repo, profile)  # RISK_V2_1 wrap",
            result={"risk_count": len(risks)},
        )
        # Attach per-risk formula_execution ledgers into node steps when present
        for r in risks[:20]:
            fe = r.get("formula_execution")
            if isinstance(fe, dict):
                self.emit_step(
                    context,
                    name=f"risk_ledger:{r.get('condition_name')}",
                    expression="formula_execution",
                    result={
                        "risk_percent": r.get("risk_percent"),
                        "confidence_percent": r.get("confidence_percent"),
                        "steps": len(fe.get("steps") or []),
                    },
                )
