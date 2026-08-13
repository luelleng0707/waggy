"""Duplicate detection (QA-903)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport


class DeterministicDuplicateDetector:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        for dataset, table in sorted(tables.items()):
            columns = set(table.columns)
            id_cols = [col for col in table.columns if col.endswith("_id") or col == "fact_id"]
            for id_col in id_cols:
                dupes = table[id_col].astype(str).str.strip()
                dupes = dupes[(dupes != "") & dupes.duplicated()]
                for value in sorted(set(dupes)):
                    issues.append(
                        QAIssue(
                            severity="error",
                            code="DUPLICATE_ID",
                            dataset=dataset,
                            row_ref=value,
                            column=id_col,
                            detail=f"Duplicate ID `{value}`",
                            formula_id="QA-903",
                        )
                    )

            name_cols = [col for col in ("condition_name", "objective_name", "mechanism_name", "ingredient_name", "product_name") if col in columns]
            for name_col in name_cols:
                normalized = table[name_col].astype(str).str.strip().str.lower()
                dupes = normalized[(normalized != "") & normalized.duplicated()]
                for value in sorted(set(dupes)):
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="DUPLICATE_CONCEPT",
                            dataset=dataset,
                            row_ref=value,
                            column=name_col,
                            detail=f"Potential duplicate concept name `{value}`",
                            formula_id="QA-903",
                        )
                    )

            claim_cols = [col for col in ("condition_id", "objective_id", "mechanism_id", "ingredient_id", "observed_effect") if col in columns]
            if claim_cols:
                claim_keys = table[claim_cols].astype(str).agg("|".join, axis=1).str.lower()
                dupes = claim_keys[claim_keys.duplicated()]
                if not dupes.empty:
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="DUPLICATE_CLAIM",
                            dataset=dataset,
                            row_ref="dataset",
                            column=",".join(claim_cols),
                            detail=f"{len(dupes)} duplicate claim rows",
                            formula_id="QA-903",
                        )
                    )

        return QAStageReport(
            stage_name="Duplicate Detection",
            formula_id="QA-903",
            issues=tuple(issues),
            metrics={"issue_count": len(issues)},
        )
