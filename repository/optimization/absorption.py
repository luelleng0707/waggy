"""Absorption effects calculator."""

from __future__ import annotations

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, InteractionReport, InteractionSignal


class DeterministicAbsorptionCalculator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def calculate(self, candidate: BundleCandidate) -> InteractionReport:
        interactions = self.warehouse.load_dataset("optimization.ingredient_interactions")
        present = _present_ingredients(candidate, self.warehouse)

        signals: list[InteractionSignal] = []
        factors: list[float] = []
        for _, row in interactions.iterrows():
            ingredient_a = str(row.get("ingredient_A", "")).strip()
            ingredient_b = str(row.get("ingredient_B", "")).strip()
            if ingredient_a not in present or ingredient_b not in present:
                continue
            factor = float(str(row.get("effect_factor", "1")).strip() or "1")
            factors.append(factor)
            signals.append(
                InteractionSignal(
                    signal_id=str(row.get("interaction_id", "")).strip(),
                    ingredient_a=ingredient_a,
                    ingredient_b=ingredient_b,
                    effect_value=factor,
                    scientific_quote=str(row.get("scientific_quote", "")).strip(),
                    paper_name=str(row.get("paper_name", "")).strip(),
                    paper_link=str(row.get("paper_link", "")).strip(),
                    warehouse_row_id=f"optimization.ingredient_interactions:{row.get('interaction_id', '')}",
                )
            )

        score = (sum(factors) / float(len(factors))) * 100.0 if factors else 100.0
        return InteractionReport(
            absorption_signals=tuple(sorted(signals, key=lambda row: row.signal_id)),
            synergy_signals=tuple(),
            conflict_signals=tuple(),
            absorption_score_percent=round(score, 6),
            synergy_score_percent=0.0,
            conflict_penalty_percent=0.0,
            formula_ids_used=("ABS-705",),
        )


def _present_ingredients(candidate: BundleCandidate, warehouse: WarehouseInterface) -> set[str]:
    compositions = warehouse.load_dataset("optimization.product_compositions")
    rows_by_product: dict[str, list[dict[str, str]]] = {}
    for _, row in compositions.iterrows():
        product_id = str(row.get("product_id", "")).strip()
        if not product_id:
            continue
        rows_by_product.setdefault(product_id, []).append({k: str(v) for k, v in row.items()})

    present: set[str] = set()
    for item in candidate.items:
        if item.servings_per_day <= 0:
            continue
        for row in rows_by_product.get(item.product_id, []):
            ingredient_id = row.get("ingredient_id", "").strip()
            if ingredient_id:
                present.add(ingredient_id)
    return present
