"""Body-system aggregation stage."""

from __future__ import annotations

from dataclasses import replace

from repository.reasoning.models import ConditionAssessment
from repository.warehouse import WarehouseInterface


class WarehouseSystemAggregator:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def aggregate(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ConditionAssessment, ...]:
        mapping = self.warehouse.load_dataset("reference.condition_systems")
        by_condition = {
            str(r["condition_name"]).strip().lower(): str(r["body_system"]).strip()
            for _, r in mapping.iterrows()
        } if not mapping.empty else {}
        out: list[ConditionAssessment] = []
        for a in assessments:
            system = by_condition.get(a.condition_name.strip().lower(), "Unknown")
            out.append(replace(a, body_system=system))
        return tuple(out)
