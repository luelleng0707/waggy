"""Ontology connectivity validation (QA-906)."""

from __future__ import annotations

import pandas as pd

from .models import QAIssue, QAStageReport


class DeterministicOntologyValidator:
    def validate(self, tables: dict[str, pd.DataFrame]) -> QAStageReport:
        issues: list[QAIssue] = []
        condition_objectives = tables.get("objectives.condition_objectives", pd.DataFrame())
        objective_mechanisms = tables.get("objectives.objective_mechanisms", pd.DataFrame())
        ingredient_mechanisms = tables.get("mechanisms.ingredient_mechanisms", pd.DataFrame())
        ingredients = tables.get("nutrition.ingredients", pd.DataFrame())
        objectives = tables.get("objectives.objectives", pd.DataFrame())
        mechanisms = tables.get("mechanisms.mechanisms", pd.DataFrame())
        conditions = tables.get("biology.conditions", pd.DataFrame())
        condition_systems = tables.get("reference.condition_systems", pd.DataFrame())

        ing_linked = set(ingredient_mechanisms.get("ingredient_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        for ingredient_id in sorted(
            set(ingredients.get("ingredient_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        ):
            if ingredient_id not in ing_linked:
                issues.append(
                    QAIssue("warning", "ORPHAN_INGREDIENT", "nutrition.ingredients", ingredient_id, "ingredient_id", "Ingredient has no mechanism link.", "QA-906")
                )

        mech_linked = set(objective_mechanisms.get("mechanism_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        for mechanism_id in sorted(
            set(mechanisms.get("mechanism_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        ):
            if mechanism_id not in mech_linked:
                issues.append(
                    QAIssue("warning", "ORPHAN_MECHANISM", "mechanisms.mechanisms", mechanism_id, "mechanism_id", "Mechanism has no objective link.", "QA-906")
                )

        obj_linked = set(condition_objectives.get("objective_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        for objective_id in sorted(
            set(objectives.get("objective_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        ):
            if objective_id not in obj_linked:
                issues.append(
                    QAIssue("warning", "ORPHAN_OBJECTIVE", "objectives.objectives", objective_id, "objective_id", "Objective has no condition link.", "QA-906")
                )

        cond_linked = set(condition_systems.get("condition_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        for condition_id in sorted(
            set(conditions.get("condition_id", pd.Series(dtype=str)).astype(str).str.strip()) - {""}
        ):
            if condition_id not in cond_linked:
                issues.append(
                    QAIssue("warning", "ORPHAN_CONDITION_SYSTEM", "biology.conditions", condition_id, "condition_id", "Condition has no body-system link.", "QA-906")
                )

        return QAStageReport(
            stage_name="Ontology Validation",
            formula_id="QA-906",
            issues=tuple(issues),
            metrics={"issue_count": len(issues)},
        )
