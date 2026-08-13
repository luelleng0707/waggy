"""Unit and basis validation (QA-905)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport


VALID_UNIT_TOKENS = ("mg", "g", "kg", "iu", "percent", "ratio", "cfu", "kcal")
BASIS_TOKENS = ("per_100g", "per_serving", "per_day", "dry_matter", "fresh_weight")


class DeterministicUnitValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        for dataset, table in sorted(tables.items()):
            if "unit" not in table.columns:
                continue
            series = table["unit"].astype(str).str.strip().str.lower()
            for idx, value in enumerate(series):
                row_ref = str(table.iloc[idx].get("fact_id", idx))
                if not value:
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="MISSING_UNIT",
                            dataset=dataset,
                            row_ref=row_ref,
                            column="unit",
                            detail="Unit is blank.",
                            formula_id="QA-905",
                        )
                    )
                    continue
                if not any(token in value for token in VALID_UNIT_TOKENS):
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="UNKNOWN_UNIT",
                            dataset=dataset,
                            row_ref=row_ref,
                            column="unit",
                            detail=f"Unknown unit token: {value}",
                            formula_id="QA-905",
                        )
                    )
                if ("per" in value or "%" in value or "percent" in value) and not any(
                    token in value for token in BASIS_TOKENS
                ):
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="MISSING_UNIT_BASIS",
                            dataset=dataset,
                            row_ref=row_ref,
                            column="unit",
                            detail=f"Unit missing clear basis: {value}",
                            formula_id="QA-905",
                        )
                    )
            unique_units = tuple(sorted(set(series)))
            if len(unique_units) > 1 and any("percent" in row for row in unique_units) and any(
                "mg" in row or "g" in row for row in unique_units
            ):
                issues.append(
                    QAIssue(
                        severity="warning",
                        code="MIXED_UNIT_SYSTEM",
                        dataset=dataset,
                        row_ref="dataset",
                        column="unit",
                        detail=f"Mixed mass and percent units: {', '.join(unique_units)}",
                        formula_id="QA-905",
                    )
                )
        return QAStageReport(
            stage_name="Unit Validation",
            formula_id="QA-905",
            issues=tuple(issues),
            metrics={"issue_count": len(issues)},
        )
