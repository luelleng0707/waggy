"""Immutable models for Ω8 warehouse QA pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QAIssue:
    severity: str
    code: str
    dataset: str
    row_ref: str
    column: str
    detail: str
    formula_id: str


@dataclass(frozen=True)
class QAStageReport:
    stage_name: str
    formula_id: str
    issues: tuple[QAIssue, ...] = field(default_factory=tuple)
    metrics: dict[str, float | int | str] = field(default_factory=dict)


@dataclass(frozen=True)
class CoverageRow:
    condition_id: str
    condition_name: str
    objectives_count: int
    mechanisms_count: int
    ingredients_count: int
    sources_count: int
    recipes_count: int
    products_count: int
    evidence_papers_count: int
    average_publication_year: float


@dataclass(frozen=True)
class CoverageReport:
    rows: tuple[CoverageRow, ...] = field(default_factory=tuple)
    metrics: dict[str, float | int | str] = field(default_factory=dict)
    formula_id: str = "QA-907"


@dataclass(frozen=True)
class PublicationReadinessReport:
    completeness_percent: float
    broken_links: int
    missing_evidence: int
    duplicate_claims: int
    ontology_orphans: int
    publication_score: float
    formula_ids: tuple[str, ...] = field(default_factory=tuple)
    markdown: str = ""


@dataclass(frozen=True)
class DashboardReport:
    top_missing_conditions: tuple[str, ...] = field(default_factory=tuple)
    top_missing_objectives: tuple[str, ...] = field(default_factory=tuple)
    top_missing_mechanisms: tuple[str, ...] = field(default_factory=tuple)
    top_missing_ingredients: tuple[str, ...] = field(default_factory=tuple)
    top_missing_products: tuple[str, ...] = field(default_factory=tuple)
    top_missing_papers: tuple[str, ...] = field(default_factory=tuple)
    coverage_heatmap: tuple[tuple[str, float], ...] = field(default_factory=tuple)
    evidence_density: tuple[tuple[str, float], ...] = field(default_factory=tuple)
    average_citation_age: float = 0.0


@dataclass(frozen=True)
class QARuntimeResult:
    schema: QAStageReport
    foreign_keys: QAStageReport
    evidence: QAStageReport
    units: QAStageReport
    duplicates: QAStageReport
    ontology: QAStageReport
    consistency: QAStageReport
    coverage: CoverageReport
    publication: PublicationReadinessReport
    dashboard: DashboardReport
    all_issues: tuple[QAIssue, ...] = field(default_factory=tuple)
