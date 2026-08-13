"""Interfaces for Ω8 warehouse QA modules."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from .models import CoverageReport, DashboardReport, PublicationReadinessReport, QAStageReport


class SchemaValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Validate required/extra columns, IDs, and schema fields."""


class ForeignKeyValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Validate FK relationships across warehouse datasets."""


class CitationValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Validate scientific evidence fields and quote quality."""


class UnitValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Validate units and unit basis consistency."""


class DuplicateDetector(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Detect duplicates of IDs, entities, and claims."""


class OntologyValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Validate ontology connectivity and orphan concepts."""


class ScientificConsistencyValidator(Protocol):
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        """Detect contradictory scientific assertions."""


class CoverageAnalyzer(Protocol):
    def analyze(self, tables: dict[str, pd.DataFrame]) -> CoverageReport:
        """Calculate network coverage and evidence density."""


class PublicationReporter(Protocol):
    def build(
        self,
        stage_reports: tuple[QAStageReport, ...],
        coverage: CoverageReport,
    ) -> PublicationReadinessReport:
        """Generate publication-readiness summary."""


class DashboardBuilder(Protocol):
    def build(self, coverage: CoverageReport, reports: tuple[QAStageReport, ...]) -> DashboardReport:
        """Build deterministic dashboard metrics from QA reports."""
