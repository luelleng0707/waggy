"""Registry builder for formula-as-data entries."""

from __future__ import annotations

import pandas as pd

from .models import (
    CoefficientEntry,
    FormulaCatalogEntry,
    FormulaConfiguration,
    FormulaVersionEntry,
    ParameterSetEntry,
)


class FormulaRegistry:
    def __init__(self, tables: dict[str, pd.DataFrame]):
        self._catalog = _catalog_entries(tables["formulas.formulas"])
        self._versions = _version_entries(tables["formulas.formula_versions"])
        self._parameter_sets = _parameter_set_entries(tables["formulas.parameter_sets"])
        self._coefficients = _coefficient_entries(tables["formulas.coefficients"])

    @property
    def catalog(self) -> tuple[FormulaCatalogEntry, ...]:
        return self._catalog

    @property
    def versions(self) -> tuple[FormulaVersionEntry, ...]:
        return self._versions

    @property
    def parameter_sets(self) -> tuple[ParameterSetEntry, ...]:
        return self._parameter_sets

    @property
    def coefficients(self) -> tuple[CoefficientEntry, ...]:
        return self._coefficients

    def configuration(self, formula_id: str, version: str) -> FormulaConfiguration | None:
        versions = [entry for entry in self._versions if entry.formula_id == formula_id and entry.version == version]
        if not versions:
            return None
        selected = versions[0]
        coeffs = tuple(
            sorted(
                [
                    entry
                    for entry in self._coefficients
                    if entry.formula_id == formula_id
                    and entry.version == version
                    and entry.parameter_set_id == selected.parameter_set_id
                ],
                key=lambda row: row.parameter_name,
            )
        )
        return FormulaConfiguration(
            formula_id=formula_id,
            version=version,
            status=selected.status,
            parameter_set_id=selected.parameter_set_id,
            coefficients=coeffs,
        )


def _catalog_entries(table: pd.DataFrame) -> tuple[FormulaCatalogEntry, ...]:
    entries = []
    for _, row in table.iterrows():
        entries.append(
            FormulaCatalogEntry(
                formula_id=str(row.get("formula_id", "")).strip(),
                formula_name=str(row.get("formula_name", "")).strip(),
                latest_version=str(row.get("latest_version", "")).strip(),
                description=str(row.get("description", "")).strip(),
            )
        )
    return tuple(sorted(entries, key=lambda item: item.formula_id))


def _version_entries(table: pd.DataFrame) -> tuple[FormulaVersionEntry, ...]:
    entries = []
    for _, row in table.iterrows():
        entries.append(
            FormulaVersionEntry(
                formula_id=str(row.get("formula_id", "")).strip(),
                version=str(row.get("version", "")).strip(),
                status=str(row.get("status", "")).strip(),
                publication_date=str(row.get("publication_date", "")).strip(),
                description=str(row.get("description", "")).strip(),
                parameter_set_id=str(row.get("parameter_set_id", "")).strip(),
            )
        )
    return tuple(sorted(entries, key=lambda item: (item.formula_id, item.version)))


def _parameter_set_entries(table: pd.DataFrame) -> tuple[ParameterSetEntry, ...]:
    entries = []
    for _, row in table.iterrows():
        entries.append(
            ParameterSetEntry(
                parameter_set_id=str(row.get("parameter_set_id", "")).strip(),
                formula_id=str(row.get("formula_id", "")).strip(),
                version=str(row.get("version", "")).strip(),
                status=str(row.get("status", "")).strip(),
                description=str(row.get("description", "")).strip(),
            )
        )
    return tuple(sorted(entries, key=lambda item: item.parameter_set_id))


def _coefficient_entries(table: pd.DataFrame) -> tuple[CoefficientEntry, ...]:
    entries = []
    for _, row in table.iterrows():
        value = str(row.get("value", "")).strip()
        entries.append(
            CoefficientEntry(
                formula_id=str(row.get("formula_id", "")).strip(),
                version=str(row.get("version", "")).strip(),
                parameter_set_id=str(row.get("parameter_set_id", "")).strip(),
                parameter_name=str(row.get("parameter_name", "")).strip(),
                value=float(value) if value else 0.0,
                unit=str(row.get("unit", "")).strip(),
                description=str(row.get("description", "")).strip(),
            )
        )
    return tuple(sorted(entries, key=lambda item: (item.formula_id, item.version, item.parameter_set_id, item.parameter_name)))
