"""Schema validation (QA-901)."""

from __future__ import annotations

import re

import pandas as pd

from .models import QAIssue, QAStageReport

REQUIRED_SCIENCE_COLUMNS = (
    "scientific_quote",
    "paper_name",
    "paper_link",
    "publication_year",
    "study_type",
)
RESERVED_ID_PREFIXES = ("TMP_", "TEST_", "DRAFT_")
URL_PATTERN = re.compile(r"^https?://")


class DeterministicSchemaValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        for dataset, table in sorted(tables.items()):
            columns = tuple(str(col).strip() for col in table.columns)
            for required in REQUIRED_SCIENCE_COLUMNS:
                if required not in columns:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="MISSING_COLUMN",
                            dataset=dataset,
                            row_ref="dataset",
                            column=required,
                            detail=f"Required column `{required}` missing.",
                            formula_id="QA-901",
                        )
                    )

            id_columns = [col for col in columns if col.endswith("_id") or col == "fact_id"]
            for id_col in id_columns:
                series = table[id_col].astype(str).str.strip()
                empties = series == ""
                if empties.any():
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="EMPTY_ID",
                            dataset=dataset,
                            row_ref=id_col,
                            column=id_col,
                            detail=f"{int(empties.sum())} empty IDs",
                            formula_id="QA-901",
                        )
                    )
                duplicates = series[series != ""].duplicated()
                if duplicates.any():
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="DUPLICATE_ID",
                            dataset=dataset,
                            row_ref=id_col,
                            column=id_col,
                            detail=f"{int(duplicates.sum())} duplicate IDs",
                            formula_id="QA-901",
                        )
                    )
                reserved = series[series.str.startswith(RESERVED_ID_PREFIXES)]
                if not reserved.empty:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="RESERVED_ID",
                            dataset=dataset,
                            row_ref=id_col,
                            column=id_col,
                            detail=f"{len(reserved)} reserved IDs",
                            formula_id="QA-901",
                        )
                    )

            for field in ("scientific_quote", "paper_name", "paper_link"):
                if field not in columns:
                    continue
                blanks = table[field].astype(str).str.strip() == ""
                if blanks.any():
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="BLANK_EVIDENCE_FIELD",
                            dataset=dataset,
                            row_ref=field,
                            column=field,
                            detail=f"{int(blanks.sum())} blank values",
                            formula_id="QA-901",
                        )
                    )
            if "paper_link" in columns:
                links = table["paper_link"].astype(str).str.strip()
                invalid = links[(links != "") & ~links.str.match(URL_PATTERN)]
                if not invalid.empty:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="INVALID_URL",
                            dataset=dataset,
                            row_ref="paper_link",
                            column="paper_link",
                            detail=f"{len(invalid)} invalid URLs",
                            formula_id="QA-901",
                        )
                    )
        return QAStageReport(
            stage_name="Schema Validation",
            formula_id="QA-901",
            issues=tuple(issues),
            metrics={"datasets_checked": len(tables), "issue_count": len(issues)},
        )
