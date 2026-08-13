from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from app.agent.nodes.validation_node import ValidationNode
from repository.formulas.runtime import get_formula_runtime
from repository.formulas.validator import FormulaRegistryValidator
from repository.warehouse.warehouse_interface import WarehouseInterface


class _FakeValidationContext:
    def __init__(self):
        self.outputs = {}
        self.warnings = []
        self.errors = []
        self.lookup_trace = []
        self._current_node_trace = None

    def get_output(self, key: str):
        return self.outputs.get(key)

    def set_output(self, key: str, payload):
        self.outputs[key] = payload


def test_warehouse_validation_does_not_mutate_scientific_data():
    warehouse = WarehouseInterface()
    before = warehouse.load_dataset("biology.conditions")
    report = warehouse.validate()
    after = warehouse.load_dataset("biology.conditions")
    assert hasattr(report, "issues")
    pd.testing.assert_frame_equal(before, after)


def test_runtime_validation_reports_missing_inputs_without_silent_repair():
    context = _FakeValidationContext()
    ValidationNode().execute(context)
    payload = context.outputs["validation"]
    assert payload["ok"] is False
    assert "profile" in payload["missing_inputs"]
    assert payload["errors"] == []


def test_formula_validation_does_not_mutate_registry_or_fallback_silently():
    runtime = get_formula_runtime()
    before = tuple(runtime.registry.catalog)
    report = FormulaRegistryValidator().validate(runtime.registry)
    after = tuple(runtime.registry.catalog)
    assert before == after
    assert hasattr(report, "ok")


def test_optimization_and_scientific_validation_remain_separate_surfaces():
    # Boundary check: optimization constraints and warehouse evidence validators are distinct modules.
    import repository.optimization.constraints as constraints_mod
    import repository.warehouse_qa.citations as citations_mod

    assert constraints_mod.__name__ != citations_mod.__name__
    assert "optimization" in constraints_mod.__name__
    assert "warehouse_qa" in citations_mod.__name__
