"""Coverage calculations for Ω6 bundle candidates."""

from __future__ import annotations

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, CoverageItem, CoverageReport, TargetIntakePlan


class DeterministicCoverageCalculator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def calculate(self, candidate: BundleCandidate, target_plan: TargetIntakePlan) -> CoverageReport:
        compositions = self.warehouse.load_dataset("optimization.product_compositions")
        provided = _provided_ingredients(candidate, compositions)

        items: list[CoverageItem] = []
        deviations: list[float] = []
        coverage_values: list[float] = []
        for target in sorted(target_plan.targets, key=lambda row: row.ingredient_id):
            required = max(0.000001, target.required_amount)
            provided_amount = provided.get(target.ingredient_id, 0.0)
            coverage = (provided_amount / required) * 100.0
            coverage_values.append(min(100.0, coverage))
            deviations.append(abs(coverage - 100.0))
            items.append(
                CoverageItem(
                    ingredient_id=target.ingredient_id,
                    required_amount=required,
                    provided_amount=round(provided_amount, 6),
                    coverage_percent=round(coverage, 6),
                    formula_id="COV-703",
                    warehouse_row_ids=target.warehouse_row_ids,
                )
            )

        mean_coverage = sum(coverage_values) / float(len(coverage_values)) if coverage_values else 0.0
        mean_deviation = sum(deviations) / float(len(deviations)) if deviations else 100.0
        dose_accuracy = max(0.0, 100.0 - mean_deviation)
        return CoverageReport(
            items=tuple(items),
            mean_coverage_percent=round(mean_coverage, 6),
            dose_accuracy_percent=round(dose_accuracy, 6),
            formula_ids_used=("COV-703", "COV-704"),
        )


def _provided_ingredients(candidate: BundleCandidate, compositions) -> dict[str, float]:
    composition_rows: dict[str, list[dict[str, str]]] = {}
    for _, row in compositions.iterrows():
        product_id = str(row.get("product_id", "")).strip()
        if not product_id:
            continue
        composition_rows.setdefault(product_id, []).append({k: str(v) for k, v in row.items()})

    provided: dict[str, float] = {}
    for item in candidate.items:
        for row in composition_rows.get(item.product_id, []):
            ingredient_id = row.get("ingredient_id", "").strip()
            if not ingredient_id:
                continue
            per_serving = float(row.get("amount_per_serving", "0") or "0")
            provided[ingredient_id] = provided.get(ingredient_id, 0.0) + (per_serving * item.servings_per_day)
    return provided
