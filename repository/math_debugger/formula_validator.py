"""Formula constant audit and cross-layer checks."""

from __future__ import annotations

import ast
from pathlib import Path

from repository.formulas.runtime import get_formula_runtime

from .models import FormulaConstantAuditRow


class FormulaConstantValidator:
    def audit(self) -> tuple[FormulaConstantAuditRow, ...]:
        root = Path(__file__).resolve().parents[1] / "mathematics"
        files = sorted([path for path in root.glob("*.py") if path.name not in {"__init__.py", "formula_access.py", "formulas.py"}])
        rows: list[FormulaConstantAuditRow] = []
        for path in files:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            function_stack: list[str] = []

            class Visitor(ast.NodeVisitor):
                def visit_FunctionDef(self, node: ast.FunctionDef):  # type: ignore[override]
                    function_stack.append(node.name)
                    self.generic_visit(node)
                    function_stack.pop()

                def visit_Constant(self, node: ast.Constant):  # type: ignore[override]
                    if isinstance(node.value, (int, float)):
                        value = float(node.value)
                        if value in {0.0, 1.0, -1.0, 100.0}:
                            status = "VALID"
                            classification = "MATHEMATICAL_CONSTANT"
                            provenance = "Intrinsic mathematical constant."
                        else:
                            status = "ENGINEERING_ASSUMPTION"
                            classification = "ENGINEERING_THRESHOLD"
                            provenance = "Constant appears in executable mathematics code."
                        rows.append(
                            FormulaConstantAuditRow(
                                file=str(path.relative_to(Path(__file__).resolve().parents[2])).replace("\\", "/"),
                                function=function_stack[-1] if function_stack else "",
                                line=getattr(node, "lineno", 0),
                                constant=str(node.value),
                                formula="UNKNOWN_FORMULA",
                                classification=classification,
                                provenance=provenance,
                                status=status,
                            )
                        )
                    self.generic_visit(node)

            Visitor().visit(tree)
        return tuple(sorted(rows, key=lambda row: (row.file, row.line, row.constant)))

    def cross_validate_registry(self) -> tuple[str, ...]:
        runtime = get_formula_runtime()
        issues: list[str] = []
        for formula in runtime.registry.catalog:
            config = runtime.configuration(formula.formula_id, formula.latest_version)
            if not config.coefficients:
                issues.append(f"MISSING_COEFFICIENTS:{formula.formula_id}:{formula.latest_version}")
        return tuple(sorted(set(issues)))

    def cross_validate_layers(self) -> tuple[str, ...]:
        runtime = get_formula_runtime()
        issues: list[str] = []
        docs_root = Path(__file__).resolve().parents[2] / "docs" / "mathematics"
        tests_root = Path(__file__).resolve().parents[2] / "tests"

        docs_text = ""
        for path in docs_root.glob("*.md"):
            docs_text += path.read_text(encoding="utf-8") + "\n"

        tests_text = ""
        for path in tests_root.glob("**/*.py"):
            tests_text += path.read_text(encoding="utf-8") + "\n"

        for formula in runtime.registry.catalog:
            formula_id = formula.formula_id
            if formula_id not in docs_text:
                issues.append(f"MISSING_SPEC:{formula_id}")
            if formula_id not in tests_text:
                issues.append(f"MISSING_TEST_REFERENCE:{formula_id}")
            config = runtime.configuration(formula_id, formula.latest_version)
            if not config.coefficients:
                issues.append(f"MISSING_PARAMETER_CONFIGURATION:{formula_id}:{formula.latest_version}")
        return tuple(sorted(set(issues)))
