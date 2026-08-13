"""Foreign key validation (QA-902)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport

FK_RULES: tuple[tuple[str, str, str, str], ...] = (
    ("objectives.condition_objectives", "condition_id", "biology.conditions", "condition_id"),
    ("objectives.condition_objectives", "objective_id", "objectives.objectives", "objective_id"),
    ("objectives.objective_mechanisms", "objective_id", "objectives.objectives", "objective_id"),
    ("objectives.objective_mechanisms", "mechanism_id", "mechanisms.mechanisms", "mechanism_id"),
    ("mechanisms.ingredient_mechanisms", "mechanism_id", "mechanisms.mechanisms", "mechanism_id"),
    ("mechanisms.ingredient_mechanisms", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
    ("sources.ingredient_sources", "ingredient_id", "nutrition.ingredients", "ingredient_id"),
    ("science_graph.source_recipes", "source_id", "sources.ingredient_sources", "source_id"),
    ("science_graph.source_recipes", "recipe_id", "recipes.recipes", "recipe_id"),
    ("science_graph.recipe_products", "recipe_id", "recipes.recipes", "recipe_id"),
    ("science_graph.recipe_products", "product_id", "optimization.product_servings", "product_id"),
)


class DeterministicForeignKeyValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        for src_ds, src_col, dst_ds, dst_col in FK_RULES:
            src = tables.get(src_ds)
            dst = tables.get(dst_ds)
            if src is None or dst is None:
                continue
            if src_col not in src.columns or dst_col not in dst.columns:
                issues.append(
                    QAIssue(
                        severity="error",
                        code="FK_COLUMN_MISSING",
                        dataset=src_ds,
                        row_ref=f"{src_col}->{dst_ds}.{dst_col}",
                        column=src_col,
                        detail="Foreign-key column missing.",
                        formula_id="QA-902",
                    )
                )
                continue
            src_values = set(src[src_col].astype(str).str.strip()) - {""}
            dst_values = set(dst[dst_col].astype(str).str.strip()) - {""}
            for value in sorted(src_values - dst_values):
                issues.append(
                    QAIssue(
                        severity="error",
                        code="BROKEN_FOREIGN_KEY",
                        dataset=src_ds,
                        row_ref=value,
                        column=src_col,
                        detail=f"{value} missing in {dst_ds}.{dst_col}",
                        formula_id="QA-902",
                    )
                )
        return QAStageReport(
            stage_name="Foreign Key Validation",
            formula_id="QA-902",
            issues=tuple(issues),
            metrics={"fk_rules": len(FK_RULES), "issue_count": len(issues)},
        )
