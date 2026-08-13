"""Runtime API for formula-as-data configuration access."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from repository.warehouse import WarehouseInterface

from .loader import FormulaWarehouseLoader
from .models import FormulaConfiguration
from .registry import FormulaRegistry
from .resolver import FormulaVersionResolver
from .validator import FormulaRegistryValidator


@dataclass(frozen=True)
class FormulaRuntime:
    registry: FormulaRegistry
    resolver: FormulaVersionResolver

    def configuration(self, formula_id: str, version: str | None = None) -> FormulaConfiguration:
        return self.resolver.resolve(formula_id, version)

    def coefficient(self, formula_id: str, parameter_name: str, version: str | None = None) -> float:
        config = self.configuration(formula_id, version)
        for entry in config.coefficients:
            if entry.parameter_name == parameter_name:
                return entry.value
        raise KeyError(f"Missing coefficient: {formula_id}:{config.version}:{parameter_name}")


@lru_cache(maxsize=1)
def get_formula_runtime() -> FormulaRuntime:
    warehouse = WarehouseInterface()
    tables = FormulaWarehouseLoader(warehouse).load()
    registry = FormulaRegistry(tables)
    report = FormulaRegistryValidator().validate(registry)
    if not report.ok:
        errors = "; ".join(
            [f"{issue.code}:{issue.formula_id}:{issue.version}:{issue.detail}" for issue in report.issues if issue.severity == "error"]
        )
        raise ValueError(f"Formula registry invalid: {errors}")
    return FormulaRuntime(registry=registry, resolver=FormulaVersionResolver(registry))
