"""Mechanism mapping stage."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from repository.reasoning.models import ConditionAssessment
from repository.warehouse import WarehouseInterface


class WarehouseMechanismMapper:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def map(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ConditionAssessment, ...]:
        rows = self.warehouse.load_dataset("reference.condition_mechanisms")
        by_condition: dict[str, list[str]] = defaultdict(list)
        for _, r in rows.iterrows():
            cname = str(r.get("condition_name", "")).strip().lower()
            mech = str(r.get("mechanism_name", "")).strip()
            if cname and mech:
                by_condition[cname].append(mech)

        out: list[ConditionAssessment] = []
        for a in assessments:
            mechs = tuple(sorted(set(by_condition.get(a.condition_name.strip().lower(), []))))
            out.append(replace(a, required_mechanisms=mechs))
        return tuple(out)
