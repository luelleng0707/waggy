"""Coefficient access helper for formula-as-data integration."""

from __future__ import annotations

from repository.formulas.runtime import get_formula_runtime


def coefficient(
    formula_id: str,
    parameter_name: str,
    fallback: float,
    version_overrides: dict[str, str] | None = None,
) -> float:
    runtime = get_formula_runtime()
    version = None
    if version_overrides:
        version = version_overrides.get(formula_id)
    try:
        return float(runtime.coefficient(formula_id=formula_id, parameter_name=parameter_name, version=version))
    except Exception:
        return float(fallback)
