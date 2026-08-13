"""Immutable models for formula-as-data configuration."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FormulaCatalogEntry:
    formula_id: str
    formula_name: str
    latest_version: str
    description: str


@dataclass(frozen=True)
class FormulaVersionEntry:
    formula_id: str
    version: str
    status: str
    publication_date: str
    description: str
    parameter_set_id: str


@dataclass(frozen=True)
class ParameterSetEntry:
    parameter_set_id: str
    formula_id: str
    version: str
    status: str
    description: str


@dataclass(frozen=True)
class CoefficientEntry:
    formula_id: str
    version: str
    parameter_set_id: str
    parameter_name: str
    value: float
    unit: str
    description: str


@dataclass(frozen=True)
class FormulaConfiguration:
    formula_id: str
    version: str
    status: str
    parameter_set_id: str
    coefficients: tuple[CoefficientEntry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FormulaValidationIssue:
    severity: str
    code: str
    formula_id: str
    version: str
    detail: str


@dataclass(frozen=True)
class FormulaValidationReport:
    ok: bool
    issues: tuple[FormulaValidationIssue, ...] = field(default_factory=tuple)
