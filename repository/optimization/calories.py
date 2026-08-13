"""Calorie and energy-density calculations."""

from __future__ import annotations

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, CalorieReport


class DeterministicCalorieCalculator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def calculate(self, candidate: BundleCandidate, life_stage: str, weight_kg: float) -> CalorieReport:
        calorie_table = self.warehouse.load_dataset("optimization.calorie_density")
        feeding_table = self.warehouse.load_dataset("optimization.feeding_constraints")
        kcal_by_product = {
            str(row.get("product_id", "")).strip(): float(str(row.get("kcal_per_serving", "0")).strip() or "0")
            for _, row in calorie_table.iterrows()
        }

        daily_calories = 0.0
        total_servings = 0.0
        row_ids: set[str] = set()
        for item in candidate.items:
            kcal = kcal_by_product.get(item.product_id, 0.0)
            daily_calories += kcal * item.servings_per_day
            total_servings += item.servings_per_day
            row_ids.add(f"optimization.calorie_density:{item.product_id}")

        max_daily = _resolve_max_daily_calories(feeding_table, life_stage, weight_kg)
        energy_density = daily_calories / total_servings if total_servings > 0 else 0.0
        pct_daily = (daily_calories / max_daily) * 100.0 if max_daily > 0 else 0.0
        row_ids.add(f"optimization.feeding_constraints:{life_stage}:{weight_kg}")
        return CalorieReport(
            daily_calories=round(daily_calories, 6),
            energy_density_kcal_per_serving=round(energy_density, 6),
            percent_of_daily_requirement=round(pct_daily, 6),
            formula_ids_used=("CAL-708", "CAL-709"),
            warehouse_row_ids=tuple(sorted(row_ids)),
        )


def _resolve_max_daily_calories(feeding_table, life_stage: str, weight_kg: float) -> float:
    stage = life_stage.strip().lower()
    matches: list[tuple[str, float]] = []
    for _, row in feeding_table.iterrows():
        row_stage = str(row.get("life_stage", "")).strip().lower()
        min_weight = float(str(row.get("weight_min_kg", "0")).strip() or "0")
        max_weight = float(str(row.get("weight_max_kg", "9999")).strip() or "9999")
        if row_stage != stage:
            continue
        if weight_kg < min_weight or weight_kg > max_weight:
            continue
        max_daily = float(str(row.get("max_daily_calories", "0")).strip() or "0")
        matches.append((str(row.get("feeding_constraint_id", "")), max_daily))
    if not matches:
        return 1.0
    matches.sort(key=lambda row: row[0])
    return matches[0][1]
