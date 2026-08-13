"""Research dashboard metrics for Ω8 QA outputs."""

from __future__ import annotations

from datetime import datetime, timezone

from .models import CoverageReport, DashboardReport, QAStageReport


class DeterministicDashboardBuilder:
    def build(self, coverage: CoverageReport, reports: tuple[QAStageReport, ...]) -> DashboardReport:
        top_missing_conditions = tuple(
            row.condition_name
            for row in sorted(
                coverage.rows,
                key=lambda row: (row.products_count, row.objectives_count, row.evidence_papers_count, row.condition_id),
            )[:5]
        )

        top_missing_objectives = _top_missing(reports, "ORPHAN_OBJECTIVE")
        top_missing_mechanisms = _top_missing(reports, "ORPHAN_MECHANISM")
        top_missing_ingredients = _top_missing(reports, "ORPHAN_INGREDIENT")
        top_missing_products = tuple(
            row.condition_name
            for row in sorted(coverage.rows, key=lambda row: (row.products_count, row.condition_id))[:5]
        )
        top_missing_papers = _top_missing(reports, "MISSING_EVIDENCE_FIELD")

        heatmap = tuple(
            sorted(
                [
                    (
                        row.condition_name,
                        float(row.objectives_count + row.mechanisms_count + row.ingredients_count + row.products_count),
                    )
                    for row in coverage.rows
                ],
                key=lambda item: item[0],
            )
        )
        density = tuple(sorted([(row.condition_name, float(row.evidence_papers_count)) for row in coverage.rows], key=lambda item: item[0]))
        years = [row.average_publication_year for row in coverage.rows if row.average_publication_year > 0]
        current_year = datetime.now(timezone.utc).year
        average_citation_age = (sum(current_year - year for year in years) / float(len(years))) if years else 0.0
        return DashboardReport(
            top_missing_conditions=top_missing_conditions,
            top_missing_objectives=top_missing_objectives,
            top_missing_mechanisms=top_missing_mechanisms,
            top_missing_ingredients=top_missing_ingredients,
            top_missing_products=top_missing_products,
            top_missing_papers=top_missing_papers,
            coverage_heatmap=heatmap,
            evidence_density=density,
            average_citation_age=round(average_citation_age, 4),
        )


def _top_missing(reports: tuple[QAStageReport, ...], code: str) -> tuple[str, ...]:
    values = []
    for report in reports:
        for issue in report.issues:
            if issue.code == code:
                values.append(f"{issue.dataset}:{issue.row_ref}")
    return tuple(sorted(values)[:5])
