"""Validate formula configuration completeness and consistency."""

from __future__ import annotations

from .models import FormulaValidationIssue, FormulaValidationReport
from .registry import FormulaRegistry


class FormulaRegistryValidator:
    def validate(self, registry: FormulaRegistry) -> FormulaValidationReport:
        issues: list[FormulaValidationIssue] = []
        catalog_by_formula = {entry.formula_id: entry for entry in registry.catalog}

        for formula_id, catalog in sorted(catalog_by_formula.items()):
            config = registry.configuration(formula_id, catalog.latest_version)
            if config is None:
                issues.append(
                    FormulaValidationIssue(
                        severity="error",
                        code="MISSING_LATEST_VERSION",
                        formula_id=formula_id,
                        version=catalog.latest_version,
                        detail="Latest version declared in formulas.csv not found in formula_versions.csv.",
                    )
                )
                continue
            if not config.coefficients:
                issues.append(
                    FormulaValidationIssue(
                        severity="error",
                        code="MISSING_COEFFICIENTS",
                        formula_id=formula_id,
                        version=config.version,
                        detail="No coefficients available for selected parameter set.",
                    )
                )

        for version in registry.versions:
            matched_parameter_sets = [
                item
                for item in registry.parameter_sets
                if item.parameter_set_id == version.parameter_set_id
                and item.formula_id == version.formula_id
                and item.version == version.version
            ]
            if not matched_parameter_sets:
                issues.append(
                    FormulaValidationIssue(
                        severity="error",
                        code="MISSING_PARAMETER_SET",
                        formula_id=version.formula_id,
                        version=version.version,
                        detail=f"Parameter set `{version.parameter_set_id}` not found in parameter_sets.csv.",
                    )
                )
        ok = not any(issue.severity == "error" for issue in issues)
        return FormulaValidationReport(ok=ok, issues=tuple(issues))
