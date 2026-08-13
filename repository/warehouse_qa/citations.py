"""Evidence and citation quality validation (QA-904)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport


class DeterministicCitationValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        quote_index: dict[str, set[str]] = {}
        for dataset, table in sorted(tables.items()):
            required = ("scientific_quote", "paper_name", "paper_link", "publication_year", "study_type")
            missing = [col for col in required if col not in table.columns]
            if missing:
                for col in missing:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="MISSING_EVIDENCE_COLUMN",
                            dataset=dataset,
                            row_ref="dataset",
                            column=col,
                            detail=f"Required evidence column missing: {col}",
                            formula_id="QA-904",
                        )
                    )
                continue
            for idx, row in table.iterrows():
                quote = str(row.get("scientific_quote", "")).strip()
                paper = str(row.get("paper_name", "")).strip()
                link = str(row.get("paper_link", "")).strip()
                year = str(row.get("publication_year", "")).strip()
                study = str(row.get("study_type", "")).strip()
                row_ref = str(row.get("fact_id", row.get("condition_id", idx)))
                if not quote or not paper or not link or not year or not study:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="MISSING_EVIDENCE_FIELD",
                            dataset=dataset,
                            row_ref=row_ref,
                            column="scientific_quote/paper_name/paper_link/publication_year/study_type",
                            detail="Evidence payload incomplete.",
                            formula_id="QA-904",
                        )
                    )
                if len(quote) < 24:
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="SHORT_QUOTE",
                            dataset=dataset,
                            row_ref=row_ref,
                            column="scientific_quote",
                            detail="Quote may be too short to support claim.",
                            formula_id="QA-904",
                        )
                    )
                if quote:
                    quote_index.setdefault(quote.lower(), set()).add(dataset)
        for quote, datasets in sorted(quote_index.items()):
            if len(datasets) > 1:
                issues.append(
                    QAIssue(
                        severity="warning",
                        code="SUSPICIOUS_QUOTE_REUSE",
                        dataset="*",
                        row_ref=quote[:64],
                        column="scientific_quote",
                        detail=f"Same quote reused across datasets: {', '.join(sorted(datasets))}",
                        formula_id="QA-904",
                    )
                )
        return QAStageReport(
            stage_name="Evidence Validation",
            formula_id="QA-904",
            issues=tuple(issues),
            metrics={"issue_count": len(issues), "unique_quotes": len(quote_index)},
        )
