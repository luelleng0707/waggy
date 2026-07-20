from __future__ import annotations

from app.agent.execution_context import ExecutionContext
from app.agent.formula_node import FormulaNode


REQUIRED_NODES = (
    "profile",
    "biology",
    "risk",
    "epidemiology",
    "nutrition",
    "product",
    "report",
)


class ValidationNode(FormulaNode):
    id = "validation"
    formula_id = "VALIDATION_V1"
    dependencies = ["assessment", "risk", "nutrition", "product", "confidence", "evidence"]
    produces = ["validation"]
    consumes = ["assessment", "risk", "nutrition", "product"]
    tables: list[str] = []

    def execute(self, context: ExecutionContext) -> None:
        missing = [n for n in REQUIRED_NODES if n not in context.outputs]
        warnings = list(context.warnings)
        errors = list(context.errors)
        risk_count = len((context.get_output("risk") or {}).get("risks") or [])
        if risk_count == 0:
            warnings.append("No risks produced")
        nutrition_targets = (context.get_output("nutrition") or {}).get("nutrient_targets") or []
        coverage = {
            "risks": risk_count,
            "nutrient_targets": len(nutrition_targets),
            "ingredients": (context.get_output("ingredient") or {}).get("count"),
            "reports": (context.get_output("report") or {}).get("count"),
        }
        payload = {
            "ok": not missing and not errors,
            "missing_inputs": missing,
            "required_inputs": list(REQUIRED_NODES),
            "expected_outputs": ["legacy_json"],
            "coverage": coverage,
            "warnings": warnings,
            "errors": errors,
        }
        context.set_output(self.id, payload)
        self.emit_step(context, name="validate_graph_outputs", result=payload)
