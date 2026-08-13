"""Bundle candidate enumeration for Ω6."""

from __future__ import annotations

from itertools import product

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, BundleCandidateItem, TargetIntakePlan


class ExhaustiveCandidateGenerator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def generate(self, target_plan: TargetIntakePlan) -> tuple[BundleCandidate, ...]:
        del target_plan  # Candidate generation is based on full catalog only.
        serving_table = self.warehouse.load_dataset("optimization.product_servings")
        package_table = self.warehouse.load_dataset("optimization.package_constraints")

        package_limits = {
            str(row.get("product_id", "")).strip(): {
                "max": float(str(row.get("max_packages_per_day", "0")).strip() or "0"),
                "availability": str(row.get("availability", "")).strip().lower(),
                "row_id": f"optimization.package_constraints:{row.get('package_constraint_id', '')}",
            }
            for _, row in package_table.iterrows()
        }

        product_specs: list[dict[str, object]] = []
        for _, row in serving_table.iterrows():
            product_id = str(row.get("product_id", "")).strip()
            if not product_id:
                continue
            package = package_limits.get(product_id, {"max": 0.0, "availability": "unavailable", "row_id": ""})
            if package["availability"] != "available":
                continue
            min_servings = int(float(str(row.get("min_servings_per_day", "0")).strip() or "0"))
            max_servings = int(float(str(row.get("max_servings_per_day", "0")).strip() or "0"))
            max_packages = int(float(package["max"]))
            upper = min(max_servings, max_packages)
            if upper < min_servings:
                continue
            product_specs.append(
                {
                    "product_id": product_id,
                    "serving_unit": str(row.get("serving_unit", "")).strip() or "serving",
                    "range": tuple(range(min_servings, upper + 1)),
                    "rows": (
                        f"optimization.product_servings:{product_id}",
                        str(package["row_id"]),
                    ),
                }
            )

        if not product_specs:
            return tuple()

        serving_ranges = [spec["range"] for spec in product_specs]
        candidates: list[BundleCandidate] = []
        counter = 0
        for combo in product(*serving_ranges):
            if sum(combo) <= 0:
                continue
            items: list[BundleCandidateItem] = []
            row_ids: list[str] = []
            for spec, servings in zip(product_specs, combo):
                if servings <= 0:
                    continue
                rows = tuple(spec["rows"])
                row_ids.extend(rows)
                items.append(
                    BundleCandidateItem(
                        product_id=str(spec["product_id"]),
                        servings_per_day=float(servings),
                        serving_unit=str(spec["serving_unit"]),
                        warehouse_row_ids=rows,
                    )
                )
            if not items:
                continue
            counter += 1
            candidates.append(
                BundleCandidate(
                    candidate_id=f"CAND_{counter:05d}",
                    items=tuple(items),
                    formula_ids_used=("CND-702",),
                    warehouse_row_ids=tuple(sorted(set(row_ids))),
                )
            )
        return tuple(candidates)
