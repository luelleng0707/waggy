"""Ω5.5 deterministic ingredient-source planning runtime modules."""

from __future__ import annotations

from repository.mechanisms.models import MechanismPlan
from repository.objectives.formulas import as_float
from repository.objectives.models import IngredientPlan, IngredientSourcePlan
from repository.warehouse import WarehouseInterface


class WarehouseBackedIngredientSourceResolver:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse
        self._ingredient_aliases = {
            "ING_EPA": "ING_F9E1B8CF",  # Omega-3
            "ING_DHA": "ING_F9E1B8CF",  # Omega-3
            "ING_GLUCOSAMINE": "ING_41BF6A84",
            "ING_MSM": "ING_996AE66D",
            "ING_ZINC": "ING_723DBC80",
            "ING_LUTEIN": "ING_C873A4B5",
            "ING_PROBIOTIC": "ING_5030A666",
            "ING_TAURINE": "ING_8A38C944",
        }

    def _canonical_ingredient_id(self, ingredient_id: str) -> str:
        return self._ingredient_aliases.get(ingredient_id, ingredient_id)

    def resolve(self, mechanism_plan: tuple[MechanismPlan, ...]) -> tuple[IngredientPlan, ...]:
        ingredient_mechanisms = self.warehouse.load_dataset("mechanisms.ingredient_mechanisms")
        dose_response = self.warehouse.load_dataset("mechanisms.dose_response")

        mechanism_importance = {item.mechanism_id: item.importance for item in mechanism_plan}
        objective_by_mechanism = {item.mechanism_id: item.objective for item in mechanism_plan}
        if not mechanism_importance:
            return tuple()

        dose_index: dict[str, dict[str, str]] = {}
        for _, row in dose_response.iterrows():
            ingredient_id = self._canonical_ingredient_id(str(row.get("ingredient", "")).strip())
            if ingredient_id and ingredient_id not in dose_index:
                dose_index[ingredient_id] = {k: str(v) for k, v in row.items()}

        ingredient_rollup: dict[str, dict[str, object]] = {}
        for _, row in ingredient_mechanisms.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            mechanism_id = row_data.get("mechanism_id", "").strip()
            ingredient_id = self._canonical_ingredient_id(row_data.get("ingredient_id", "").strip())
            if mechanism_id not in mechanism_importance or not ingredient_id:
                continue
            effect_size = as_float(row_data.get("effect_size", 0))
            contribution = mechanism_importance[mechanism_id] * (effect_size / 100.0)
            bucket = ingredient_rollup.setdefault(
                ingredient_id,
                {
                    "target_amount": 0.0,
                    "papers": set(),
                    "quotes": [],
                    "mechanisms": set(),
                    "objectives": set(),
                    "rows": set(),
                },
            )
            bucket["target_amount"] = float(bucket["target_amount"]) + contribution
            if row_data.get("paper_name", "").strip():
                bucket["papers"].add(row_data["paper_name"].strip())
            if row_data.get("scientific_quote", "").strip():
                bucket["quotes"].append(row_data["scientific_quote"].strip())
            bucket["mechanisms"].add(mechanism_id)
            bucket["objectives"].add(objective_by_mechanism.get(mechanism_id, ""))
            bucket["rows"].add(f"mechanisms.ingredient_mechanisms:{ingredient_id}:{mechanism_id}")

        plans: list[IngredientPlan] = []
        for ingredient_id in sorted(ingredient_rollup):
            dose_row = dose_index.get(ingredient_id, {})
            baseline_dose = as_float(dose_row.get("dose", 1.0))
            unit = dose_row.get("unit", "observed_unit").strip() or "observed_unit"
            target_amount = baseline_dose * max(0.5, min(2.0, float(ingredient_rollup[ingredient_id]["target_amount"])))
            papers = set(ingredient_rollup[ingredient_id]["papers"])
            quotes = list(ingredient_rollup[ingredient_id]["quotes"])
            if dose_row.get("paper", "").strip():
                papers.add(dose_row["paper"].strip())
            if dose_row.get("quote", "").strip():
                quotes.append(dose_row["quote"].strip())

            plans.append(
                IngredientPlan(
                    ingredient_id=ingredient_id,
                    ingredient_name=ingredient_id,
                    source_mechanisms=tuple(sorted(ingredient_rollup[ingredient_id]["mechanisms"])),
                    source_objectives=tuple(
                        sorted([value for value in ingredient_rollup[ingredient_id]["objectives"] if value])
                    ),
                    target_amount=round(target_amount, 6),
                    unit=unit,
                    formula_ids_used=("ING-506",),
                    supporting_papers=tuple(sorted(papers)),
                    supporting_quotes=tuple(dict.fromkeys(quotes)),
                    warehouse_rows_used=tuple(sorted(ingredient_rollup[ingredient_id]["rows"])),
                )
            )
        return tuple(plans)


class WarehouseBackedSourcePlanner:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def plan(self, ingredient_plan: tuple[IngredientPlan, ...]) -> tuple[IngredientSourcePlan, ...]:
        ingredient_sources = self.warehouse.load_dataset("sources.ingredient_sources")
        source_bio = self.warehouse.load_dataset("sources.source_bioavailability")

        bio_by_pair: dict[tuple[str, str], dict[str, str]] = {}
        for _, row in source_bio.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            key = (row_data.get("source_id", "").strip(), row_data.get("ingredient_id", "").strip())
            if key[0] and key[1]:
                bio_by_pair[key] = row_data

        plans: list[IngredientSourcePlan] = []
        by_ingredient = {item.ingredient_id: item for item in ingredient_plan}
        for _, row in ingredient_sources.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            ingredient_id = row_data.get("ingredient_id", "").strip()
            source_id = row_data.get("source_id", "").strip()
            if ingredient_id not in by_ingredient or not source_id:
                continue

            ingredient_target = max(0.000001, by_ingredient[ingredient_id].target_amount)
            natural_amount = as_float(row_data.get("natural_amount", 0))
            base_bio = as_float(row_data.get("bioavailability", 0))
            bio_row = bio_by_pair.get((source_id, ingredient_id), {})
            bio_factor = as_float(bio_row.get("bioavailability_factor", base_bio))
            source_value = natural_amount * bio_factor
            coverage = source_value / ingredient_target

            papers = [row_data.get("paper_name", "").strip()]
            quotes = [row_data.get("scientific_quote", "").strip()]
            if bio_row:
                papers.append(bio_row.get("paper_name", "").strip())
                quotes.append(bio_row.get("scientific_quote", "").strip())

            plans.append(
                IngredientSourcePlan(
                    source_id=source_id,
                    ingredient_id=ingredient_id,
                    ingredient_name=by_ingredient[ingredient_id].ingredient_name,
                    natural_amount=natural_amount,
                    unit=row_data.get("unit", "").strip() or "observed_unit",
                    bioavailability=round(bio_factor, 6),
                    coverage_score=round(coverage, 6),
                    formula_ids_used=("SRC-601", "SRC-602"),
                    supporting_papers=tuple(sorted({paper for paper in papers if paper})),
                    supporting_quotes=tuple(dict.fromkeys([quote for quote in quotes if quote])),
                    warehouse_rows_used=(
                        f"sources.ingredient_sources:{source_id}:{ingredient_id}",
                        f"sources.source_bioavailability:{source_id}:{ingredient_id}",
                    ),
                )
            )
        plans.sort(key=lambda item: (item.ingredient_id, -item.coverage_score, item.source_id))
        return tuple(plans)


class DeterministicBioavailabilityAnalyzer:
    def analyze(self, source_plan: tuple[IngredientSourcePlan, ...]) -> tuple[IngredientSourcePlan, ...]:
        # Normalization is deterministic and purely ordering/rounding safety.
        normalized: list[IngredientSourcePlan] = []
        for row in source_plan:
            normalized.append(
                IngredientSourcePlan(
                    source_id=row.source_id,
                    ingredient_id=row.ingredient_id,
                    ingredient_name=row.ingredient_name,
                    natural_amount=round(row.natural_amount, 6),
                    unit=row.unit,
                    bioavailability=round(row.bioavailability, 6),
                    coverage_score=round(row.coverage_score, 6),
                    formula_ids_used=row.formula_ids_used,
                    supporting_papers=row.supporting_papers,
                    supporting_quotes=row.supporting_quotes,
                    warehouse_rows_used=row.warehouse_rows_used,
                )
            )
        return tuple(normalized)
