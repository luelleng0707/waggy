"""Scientific contradiction detection (QA-906)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport


class DeterministicConsistencyValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        ingredient_mechanisms = tables.get("mechanisms.ingredient_mechanisms", pd.DataFrame())
        if not ingredient_mechanisms.empty and {"ingredient_id", "mechanism_id", "observed_effect", "paper_name"}.issubset(
            set(ingredient_mechanisms.columns)
        ):
            grouped: dict[tuple[str, str], set[str]] = {}
            for _, row in ingredient_mechanisms.iterrows():
                key = (
                    str(row.get("ingredient_id", "")).strip(),
                    str(row.get("mechanism_id", "")).strip(),
                )
                effect = str(row.get("observed_effect", "")).strip().lower()
                direction = "neutral"
                if any(token in effect for token in ("reduce", "decrease", "improve", "support")):
                    direction = "beneficial"
                if any(token in effect for token in ("increase", "worsen", "impair", "harm")):
                    direction = "harmful"
                grouped.setdefault(key, set()).add(direction)
            for (ingredient_id, mechanism_id), directions in sorted(grouped.items()):
                if "beneficial" in directions and "harmful" in directions:
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="CONTRADICTORY_EFFECT",
                            dataset="mechanisms.ingredient_mechanisms",
                            row_ref=f"{ingredient_id}|{mechanism_id}",
                            column="observed_effect",
                            detail="Conflicting beneficial/harmful effects detected.",
                            formula_id="QA-906",
                        )
                    )

        trait_assoc = tables.get("biology.trait_condition_associations", pd.DataFrame())
        if not trait_assoc.empty and {"trait_name", "trait_value", "condition_id", "effect_direction"}.issubset(
            set(trait_assoc.columns)
        ):
            grouped: dict[tuple[str, str, str], set[str]] = {}
            for _, row in trait_assoc.iterrows():
                key = (
                    str(row.get("trait_name", "")).strip().lower(),
                    str(row.get("trait_value", "")).strip().lower(),
                    str(row.get("condition_id", "")).strip(),
                )
                grouped.setdefault(key, set()).add(str(row.get("effect_direction", "")).strip().lower())
            for key, directions in sorted(grouped.items()):
                if "positive" in directions and "negative" in directions:
                    issues.append(
                        QAIssue(
                            severity="warning",
                            code="CONTRADICTORY_TRAIT_CLAIM",
                            dataset="biology.trait_condition_associations",
                            row_ref="|".join(key),
                            column="effect_direction",
                            detail="Same trait-condition pair has positive and negative directions.",
                            formula_id="QA-906",
                        )
                    )
        return QAStageReport(
            stage_name="Scientific Consistency",
            formula_id="QA-906",
            issues=tuple(issues),
            metrics={"issue_count": len(issues)},
        )
