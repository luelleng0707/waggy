"""Publication-readiness report generation (QA-908)."""

from __future__ import annotations

from .models import CoverageReport, PublicationReadinessReport, QAStageReport


class DeterministicPublicationReporter:
    def build(
        self,
        stage_reports: tuple[QAStageReport, ...],
        coverage: CoverageReport,
    ) -> PublicationReadinessReport:
        issues = [issue for report in stage_reports for issue in report.issues]
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]
        total_checks = max(1, len(issues) + len(coverage.rows))
        completeness = max(0.0, 100.0 - (len(errors) / float(total_checks) * 100.0))

        broken_links = sum(1 for issue in issues if issue.code == "INVALID_URL")
        missing_evidence = sum(1 for issue in issues if "EVIDENCE" in issue.code or issue.code == "BLANK_EVIDENCE_FIELD")
        duplicate_claims = sum(1 for issue in issues if "DUPLICATE" in issue.code)
        ontology_orphans = sum(1 for issue in issues if issue.code.startswith("ORPHAN_"))
        publication_score = max(
            0.0,
            min(
                100.0,
                (0.45 * completeness)
                + (0.20 * (100.0 - min(100.0, broken_links * 5.0)))
                + (0.20 * (100.0 - min(100.0, missing_evidence * 3.0)))
                + (0.15 * (100.0 - min(100.0, duplicate_claims * 2.0))),
            ),
        )
        markdown = _render_markdown(
            completeness=completeness,
            publication_score=publication_score,
            errors=len(errors),
            warnings=len(warnings),
            broken_links=broken_links,
            missing_evidence=missing_evidence,
            duplicate_claims=duplicate_claims,
            ontology_orphans=ontology_orphans,
            conditions_total=int(coverage.metrics.get("conditions_total", 0)),
        )
        return PublicationReadinessReport(
            completeness_percent=round(completeness, 4),
            broken_links=broken_links,
            missing_evidence=missing_evidence,
            duplicate_claims=duplicate_claims,
            ontology_orphans=ontology_orphans,
            publication_score=round(publication_score, 4),
            formula_ids=("QA-908",),
            markdown=markdown,
        )


def _render_markdown(
    *,
    completeness: float,
    publication_score: float,
    errors: int,
    warnings: int,
    broken_links: int,
    missing_evidence: int,
    duplicate_claims: int,
    ontology_orphans: int,
    conditions_total: int,
) -> str:
    return "\n".join(
        [
            "# Warehouse QA Publication Readiness",
            "",
            f"- Completeness: {completeness:.2f}%",
            f"- Publication score: {publication_score:.2f}",
            f"- Errors: {errors}",
            f"- Warnings: {warnings}",
            f"- Broken links: {broken_links}",
            f"- Missing evidence: {missing_evidence}",
            f"- Duplicate claims: {duplicate_claims}",
            f"- Ontology orphans: {ontology_orphans}",
            f"- Conditions reviewed: {conditions_total}",
        ]
    )
