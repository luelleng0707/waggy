"""Constraint checks for Ω6 bundle candidates."""

from __future__ import annotations

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, BundleConstraint, CalorieReport

_LIFE_STAGE_ORDER = {"puppy": 0, "adult": 1, "senior": 2}


class DeterministicConstraintChecker:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def check(
        self,
        candidate: BundleCandidate,
        calorie_report: CalorieReport,
        life_stage: str,
        weight_kg: float,
    ) -> tuple[BundleConstraint, ...]:
        serving_table = self.warehouse.load_dataset("optimization.product_servings")
        feeding_table = self.warehouse.load_dataset("optimization.feeding_constraints")
        package_table = self.warehouse.load_dataset("optimization.package_constraints")

        serving_rows = {
            str(row.get("product_id", "")).strip(): {k: str(v) for k, v in row.items()}
            for _, row in serving_table.iterrows()
        }
        package_rows = {
            str(row.get("product_id", "")).strip(): {k: str(v) for k, v in row.items()}
            for _, row in package_table.iterrows()
        }

        constraints: list[BundleConstraint] = []
        constraints.append(_daily_calorie_constraint(feeding_table, life_stage, weight_kg, calorie_report.daily_calories))

        for item in sorted(candidate.items, key=lambda row: row.product_id):
            serving_row = serving_rows.get(item.product_id, {})
            package_row = package_rows.get(item.product_id, {})
            constraints.extend(_product_constraints(item.product_id, item.servings_per_day, life_stage, weight_kg, serving_row, package_row))

        return tuple(constraints)


def _daily_calorie_constraint(feeding_table, life_stage: str, weight_kg: float, calories: float) -> BundleConstraint:
    stage = life_stage.strip().lower()
    selected = None
    for _, row in feeding_table.iterrows():
        row_stage = str(row.get("life_stage", "")).strip().lower()
        min_weight = float(str(row.get("weight_min_kg", "0")).strip() or "0")
        max_weight = float(str(row.get("weight_max_kg", "9999")).strip() or "9999")
        if row_stage != stage:
            continue
        if weight_kg < min_weight or weight_kg > max_weight:
            continue
        selected = {k: str(v) for k, v in row.items()}
        break

    if selected is None:
        return BundleConstraint(
            constraint_id="CST_DAILY_CALORIES",
            passed=False,
            formula_id="CST-710",
            detail="No matching feeding constraint row for profile context.",
            input_values={"life_stage": life_stage, "weight_kg": weight_kg, "daily_calories": calories},
            warehouse_row_ids=("optimization.feeding_constraints:unmatched",),
            scientific_quotes=tuple(),
            paper_names=tuple(),
            paper_links=tuple(),
        )

    max_daily = float(selected.get("max_daily_calories", "0") or "0")
    passed = calories <= max_daily
    return BundleConstraint(
        constraint_id="CST_DAILY_CALORIES",
        passed=passed,
        formula_id="CST-710",
        detail=f"{round(calories, 4)} <= {round(max_daily, 4)}",
        input_values={"life_stage": life_stage, "weight_kg": weight_kg, "daily_calories": calories, "max_daily_calories": max_daily},
        warehouse_row_ids=(f"optimization.feeding_constraints:{selected.get('feeding_constraint_id', '')}",),
        scientific_quotes=(selected.get("scientific_quote", "").strip(),),
        paper_names=(selected.get("paper_name", "").strip(),),
        paper_links=(selected.get("paper_link", "").strip(),),
    )


def _product_constraints(
    product_id: str,
    servings: float,
    life_stage: str,
    weight_kg: float,
    serving_row: dict[str, str],
    package_row: dict[str, str],
) -> list[BundleConstraint]:
    output: list[BundleConstraint] = []
    min_servings = float(serving_row.get("min_servings_per_day", "0") or "0")
    max_servings = float(serving_row.get("max_servings_per_day", "0") or "0")
    max_packages = float(package_row.get("max_packages_per_day", "0") or "0")
    availability = package_row.get("availability", serving_row.get("availability", "")).strip().lower()

    output.append(
        BundleConstraint(
            constraint_id=f"CST_SERVING_LIMIT_{product_id}",
            passed=(servings >= min_servings and servings <= max_servings),
            formula_id="CST-710",
            detail=f"{servings} in [{min_servings}, {max_servings}]",
            input_values={"servings": servings, "min": min_servings, "max": max_servings},
            warehouse_row_ids=(f"optimization.product_servings:{product_id}",),
            scientific_quotes=(serving_row.get("scientific_quote", "").strip(),),
            paper_names=(serving_row.get("paper_name", "").strip(),),
            paper_links=(serving_row.get("paper_link", "").strip(),),
        )
    )
    output.append(
        BundleConstraint(
            constraint_id=f"CST_PACKAGE_LIMIT_{product_id}",
            passed=servings <= max_packages,
            formula_id="CST-710",
            detail=f"{servings} <= {max_packages}",
            input_values={"servings": servings, "max_packages_per_day": max_packages},
            warehouse_row_ids=(f"optimization.package_constraints:{package_row.get('package_constraint_id', '')}",),
            scientific_quotes=(package_row.get("scientific_quote", "").strip(),),
            paper_names=(package_row.get("paper_name", "").strip(),),
            paper_links=(package_row.get("paper_link", "").strip(),),
        )
    )
    output.append(
        BundleConstraint(
            constraint_id=f"CST_AVAILABILITY_{product_id}",
            passed=(availability == "available"),
            formula_id="CST-710",
            detail=f"availability={availability}",
            input_values={"availability": availability},
            warehouse_row_ids=(f"optimization.package_constraints:{package_row.get('package_constraint_id', '')}",),
            scientific_quotes=(package_row.get("scientific_quote", "").strip(),),
            paper_names=(package_row.get("paper_name", "").strip(),),
            paper_links=(package_row.get("paper_link", "").strip(),),
        )
    )

    stage = life_stage.strip().lower()
    min_stage = serving_row.get("life_stage_min", "").strip().lower()
    max_stage = serving_row.get("life_stage_max", "").strip().lower()
    min_stage_rank = _LIFE_STAGE_ORDER.get(min_stage, -1)
    max_stage_rank = _LIFE_STAGE_ORDER.get(max_stage, 999)
    stage_rank = _LIFE_STAGE_ORDER.get(stage, -1)
    output.append(
        BundleConstraint(
            constraint_id=f"CST_LIFESTAGE_{product_id}",
            passed=(stage_rank >= min_stage_rank and stage_rank <= max_stage_rank),
            formula_id="CST-710",
            detail=f"{stage} in [{min_stage}, {max_stage}]",
            input_values={"life_stage": life_stage, "life_stage_min": min_stage, "life_stage_max": max_stage},
            warehouse_row_ids=(f"optimization.product_servings:{product_id}",),
            scientific_quotes=(serving_row.get("scientific_quote", "").strip(),),
            paper_names=(serving_row.get("paper_name", "").strip(),),
            paper_links=(serving_row.get("paper_link", "").strip(),),
        )
    )

    min_weight = float(serving_row.get("weight_min_kg", "0") or "0")
    max_weight = float(serving_row.get("weight_max_kg", "9999") or "9999")
    output.append(
        BundleConstraint(
            constraint_id=f"CST_WEIGHT_{product_id}",
            passed=(weight_kg >= min_weight and weight_kg <= max_weight),
            formula_id="CST-710",
            detail=f"{weight_kg} in [{min_weight}, {max_weight}]",
            input_values={"weight_kg": weight_kg, "weight_min_kg": min_weight, "weight_max_kg": max_weight},
            warehouse_row_ids=(f"optimization.product_servings:{product_id}",),
            scientific_quotes=(serving_row.get("scientific_quote", "").strip(),),
            paper_names=(serving_row.get("paper_name", "").strip(),),
            paper_links=(serving_row.get("paper_link", "").strip(),),
        )
    )
    return output
