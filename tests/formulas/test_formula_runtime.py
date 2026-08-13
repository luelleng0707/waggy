from __future__ import annotations

from repository.formulas.loader import FormulaWarehouseLoader
from repository.formulas.registry import FormulaRegistry
from repository.formulas.resolver import FormulaVersionResolver
from repository.formulas.runtime import get_formula_runtime
from repository.formulas.validator import FormulaRegistryValidator
from repository.warehouse import WarehouseInterface


def test_formula_loading_and_validation():
    tables = FormulaWarehouseLoader(WarehouseInterface()).load()
    registry = FormulaRegistry(tables)
    report = FormulaRegistryValidator().validate(registry)
    assert report.ok
    assert registry.catalog
    assert registry.versions
    assert registry.coefficients


def test_version_resolution_active_and_explicit():
    tables = FormulaWarehouseLoader(WarehouseInterface()).load()
    registry = FormulaRegistry(tables)
    resolver = FormulaVersionResolver(registry)
    active = resolver.resolve("MAT-1005")
    explicit_v1 = resolver.resolve("MAT-1005", "v1.0")
    explicit_v2 = resolver.resolve("MAT-1005", "v2.0")
    assert active.version == "v1.0"
    assert explicit_v1.version == "v1.0"
    assert explicit_v2.version == "v2.0"
    assert explicit_v1.parameter_set_id != explicit_v2.parameter_set_id


def test_runtime_coefficient_lookup_is_deterministic():
    runtime = get_formula_runtime()
    c1 = runtime.coefficient("MAT-1005", "evidence_weight")
    c2 = runtime.coefficient("MAT-1005", "evidence_weight")
    assert c1 == c2
    assert c1 == 0.45
