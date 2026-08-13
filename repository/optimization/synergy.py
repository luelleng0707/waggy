"""Synergy effects calculator."""

from __future__ import annotations

from repository.warehouse import WarehouseInterface

from .models import BundleCandidate, InteractionReport, InteractionSignal
from .absorption import _present_ingredients


class DeterministicSynergyCalculator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def calculate(self, candidate: BundleCandidate, report: InteractionReport) -> InteractionReport:
        table = self.warehouse.load_dataset("optimization.ingredient_synergies")
        present = _present_ingredients(candidate, self.warehouse)

        signals = list(report.synergy_signals)
        effects: list[float] = []
        for _, row in table.iterrows():
            ingredient_a = str(row.get("ingredient_A", "")).strip()
            ingredient_b = str(row.get("ingredient_B", "")).strip()
            if ingredient_a not in present or ingredient_b not in present:
                continue
            effect = float(str(row.get("effect_strength", "0")).strip() or "0")
            effects.append(effect)
            signals.append(
                InteractionSignal(
                    signal_id=str(row.get("synergy_id", "")).strip(),
                    ingredient_a=ingredient_a,
                    ingredient_b=ingredient_b,
                    effect_value=effect,
                    scientific_quote=str(row.get("scientific_quote", "")).strip(),
                    paper_name=str(row.get("paper_name", "")).strip(),
                    paper_link=str(row.get("paper_link", "")).strip(),
                    warehouse_row_id=f"optimization.ingredient_synergies:{row.get('synergy_id', '')}",
                )
            )

        score = (sum(effects) / float(len(effects))) * 100.0 if effects else 0.0
        return InteractionReport(
            absorption_signals=report.absorption_signals,
            synergy_signals=tuple(sorted(signals, key=lambda row: row.signal_id)),
            conflict_signals=report.conflict_signals,
            absorption_score_percent=report.absorption_score_percent,
            synergy_score_percent=round(score, 6),
            conflict_penalty_percent=report.conflict_penalty_percent,
            formula_ids_used=tuple(sorted(set(report.formula_ids_used + ("SYN-706",)))),
        )
