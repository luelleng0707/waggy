from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


class EvidenceNode(FormulaNode):
    id = "evidence"
    formula_id = "EVIDENCE_V1"
    dependencies = ["risk", "ingredient"]
    produces = ["evidence_bundle"]
    consumes = ["risk", "ingredient"]
    tables = ["ingredient_evidence", "clinical_evidence_base"]

    def execute(self, context: ExecutionContext) -> None:
        risks = context.require_output("risk").get("risks") or []
        ingredients = (context.get_output("ingredient") or {}).get("ingredients") or []
        evidence_rows = []
        for r in risks:
            fe = r.get("formula_execution") or {}
            lookups = fe.get("lookups") or []
            if lookups:
                evidence_rows.append(
                    {
                        "condition": r.get("condition_name"),
                        "lookup_count": len(lookups),
                        "paper_ids": [
                            lk.get("paper_id") or lk.get("source_name")
                            for lk in lookups
                            if isinstance(lk, dict)
                        ][:5],
                    }
                )
        for ing in ingredients[:30]:
            ev = ing.get("evidence") or ing.get("source_name")
            if ev:
                evidence_rows.append(
                    {
                        "ingredient": ing.get("ingredient_name") or ing.get("name"),
                        "evidence": ev if isinstance(ev, dict) else {"source_name": ev},
                    }
                )
        df = context.repository.clinical_evidence_base()
        self.emit_lookup(
            context,
            table="clinical_evidence_base",
            rows=0 if df.empty else len(df),
        )
        context.set_output(
            self.id,
            {"evidence_bundle": evidence_rows, "count": len(evidence_rows)},
        )
        self.emit_step(context, name="collect_evidence_signals", result={"count": len(evidence_rows)})
