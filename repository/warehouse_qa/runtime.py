"""Ω8 warehouse QA runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from repository.optimization.runtime import register_optimization_datasets
from repository.science_graph.builder import register_science_graph_datasets
from repository.warehouse import WarehouseInterface
from repository.warehouse.warehouse_interface import CANONICAL_DATASETS

from .citations import DeterministicCitationValidator
from .consistency import DeterministicConsistencyValidator
from .coverage import DeterministicCoverageAnalyzer
from .dashboard import DeterministicDashboardBuilder
from .duplicates import DeterministicDuplicateDetector
from .foreign_keys import DeterministicForeignKeyValidator
from .models import QARuntimeResult
from .ontology import DeterministicOntologyValidator
from .reports import DeterministicPublicationReporter
from .units import DeterministicUnitValidator
from .validator import DeterministicSchemaValidator


def load_qa_tables(warehouse: WarehouseInterface) -> dict[str, pd.DataFrame]:
    register_optimization_datasets()
    register_science_graph_datasets()
    tables: dict[str, pd.DataFrame] = {}
    for dataset in sorted(CANONICAL_DATASETS):
        try:
            tables[dataset] = warehouse.load_dataset(dataset)
        except Exception:
            continue
    return tables


@dataclass(frozen=True)
class WarehouseQARuntime:
    warehouse: WarehouseInterface

    def run(self, tables_override: dict[str, pd.DataFrame] | None = None) -> QARuntimeResult:
        tables = tables_override if tables_override is not None else load_qa_tables(self.warehouse)

        schema = DeterministicSchemaValidator().validate(tables)
        foreign_keys = DeterministicForeignKeyValidator().validate(tables)
        evidence = DeterministicCitationValidator().validate(tables)
        units = DeterministicUnitValidator().validate(tables)
        duplicates = DeterministicDuplicateDetector().validate(tables)
        ontology = DeterministicOntologyValidator().validate(tables)
        consistency = DeterministicConsistencyValidator().validate(tables)
        coverage = DeterministicCoverageAnalyzer().analyze(tables)

        stage_reports = (schema, foreign_keys, evidence, units, duplicates, ontology, consistency)
        publication = DeterministicPublicationReporter().build(stage_reports, coverage)
        dashboard = DeterministicDashboardBuilder().build(coverage, stage_reports)
        all_issues = tuple([issue for report in stage_reports for issue in report.issues])
        return QARuntimeResult(
            schema=schema,
            foreign_keys=foreign_keys,
            evidence=evidence,
            units=units,
            duplicates=duplicates,
            ontology=ontology,
            consistency=consistency,
            coverage=coverage,
            publication=publication,
            dashboard=dashboard,
            all_issues=all_issues,
        )
