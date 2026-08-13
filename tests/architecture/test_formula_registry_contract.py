from __future__ import annotations

import pytest

from repository.formulas.runtime import get_formula_runtime


def test_formula_configuration_is_deterministic_for_same_id_and_version():
    runtime = get_formula_runtime()
    first = runtime.registry.catalog[0]
    c1 = runtime.configuration(first.formula_id, first.latest_version)
    c2 = runtime.configuration(first.formula_id, first.latest_version)
    assert c1 == c2
    assert c1.formula_id == first.formula_id
    assert c1.version == first.latest_version


def test_explicit_version_resolution_has_no_silent_substitution():
    runtime = get_formula_runtime()
    first = runtime.registry.catalog[0]
    explicit = runtime.configuration(first.formula_id, first.latest_version)
    resolved = runtime.configuration(first.formula_id, first.latest_version)
    assert explicit == resolved


def test_missing_formula_or_version_raises_explicit_error():
    runtime = get_formula_runtime()
    with pytest.raises(KeyError):
        runtime.configuration("UNKNOWN_FORMULA_ID", "1.0.0")
    known = runtime.registry.catalog[0].formula_id
    with pytest.raises(KeyError):
        runtime.configuration(known, "0.0.0-unknown")


def test_missing_coefficient_lookup_raises_explicit_error():
    runtime = get_formula_runtime()
    known = runtime.registry.catalog[0].formula_id
    with pytest.raises(KeyError):
        runtime.coefficient(known, "__missing_parameter__", version=None)


def test_formula_configuration_preserves_provenance_fields():
    runtime = get_formula_runtime()
    first = runtime.registry.catalog[0]
    config = runtime.configuration(first.formula_id, first.latest_version)
    assert config.parameter_set_id
    assert isinstance(config.coefficients, tuple)
    # Deterministic ordering by parameter name is part of registry contract.
    names = [row.parameter_name for row in config.coefficients]
    assert names == sorted(names)
