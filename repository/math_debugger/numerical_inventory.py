"""Ω9.3 numerical inventory and provenance classification."""

from __future__ import annotations

import ast
import csv
import re
from dataclasses import dataclass
from pathlib import Path


CLASSIFICATIONS = {
    "SCIENTIFIC_FACT",
    "SCIENTIFIC_PARAMETER",
    "EMPIRICALLY_DERIVED",
    "CALCULATED_VALUE",
    "ENGINEERING_PARAMETER",
    "ENGINEERING_THRESHOLD",
    "MATHEMATICAL_CONSTANT",
    "UNIT_CONVERSION_CONSTANT",
    "IMPLEMENTATION_CONSTANT",
    "UNKNOWN",
}


@dataclass(frozen=True)
class NumericalProvenanceRow:
    provenance_id: str
    value: str
    unit: str
    classification: str
    formula_id: str
    formula_version: str
    file: str
    function: str
    line: int
    variable: str
    description: str
    source_type: str
    source_id: str
    paper_name: str
    paper_link: str
    scientific_quote: str
    derivation: str
    status: str
    review_required: str


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?:\d+\.\d+|\d+)(?![A-Za-z0-9_])")


class NumericalInventoryBuilder:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def build(self) -> tuple[NumericalProvenanceRow, ...]:
        rows: list[NumericalProvenanceRow] = []
        rows.extend(self._scan_formula_coefficients())
        rows.extend(self._scan_python_constants())
        return tuple(sorted(rows, key=lambda row: row.provenance_id))

    def export_csv(self, path: Path) -> None:
        rows = self.build()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(
                [
                    "provenance_id",
                    "value",
                    "unit",
                    "classification",
                    "formula_id",
                    "formula_version",
                    "file",
                    "function",
                    "line",
                    "variable",
                    "description",
                    "source_type",
                    "source_id",
                    "paper_name",
                    "paper_link",
                    "scientific_quote",
                    "derivation",
                    "status",
                    "review_required",
                ]
            )
            for row in rows:
                writer.writerow(
                    [
                        row.provenance_id,
                        row.value,
                        row.unit,
                        row.classification,
                        row.formula_id,
                        row.formula_version,
                        row.file,
                        row.function,
                        row.line,
                        row.variable,
                        row.description,
                        row.source_type,
                        row.source_id,
                        row.paper_name,
                        row.paper_link,
                        row.scientific_quote,
                        row.derivation,
                        row.status,
                        row.review_required,
                    ]
                )

    def _scan_formula_coefficients(self) -> list[NumericalProvenanceRow]:
        coeff_path = self.repo_root / "warehouse" / "formulas" / "coefficients.csv"
        if not coeff_path.exists():
            return []
        rows: list[NumericalProvenanceRow] = []
        with coeff_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for idx, row in enumerate(reader, start=2):
                value = str(row.get("value", "")).strip()
                if not value:
                    continue
                formula_id = str(row.get("formula_id", "")).strip()
                version = str(row.get("version", "")).strip()
                parameter = str(row.get("parameter_name", "")).strip()
                classification = _classify_parameter(parameter)
                rows.append(
                    NumericalProvenanceRow(
                        provenance_id=f"PV_COEFF_{idx}",
                        value=value,
                        unit=str(row.get("unit", "")).strip(),
                        classification=classification,
                        formula_id=formula_id,
                        formula_version=version,
                        file="warehouse/formulas/coefficients.csv",
                        function="",
                        line=idx,
                        variable=parameter,
                        description=str(row.get("description", "")).strip(),
                        source_type="FORMULA_CONFIGURATION",
                        source_id=str(row.get("parameter_set_id", "")).strip(),
                        paper_name="",
                        paper_link="",
                        scientific_quote="",
                        derivation="Configured coefficient from formula-as-data.",
                        status="ENGINEERING_ASSUMPTION" if classification.startswith("ENGINEERING") else "VALID",
                        review_required="YES" if classification.startswith("ENGINEERING") else "NO",
                    )
                )
        return rows

    def _scan_python_constants(self) -> list[NumericalProvenanceRow]:
        targets = [
            self.repo_root / "repository",
            self.repo_root / "warehouse" / "formulas",
            self.repo_root / "config",
            self.repo_root / "tests",
            self.repo_root / "docs" / "mathematics",
        ]
        files: list[Path] = []
        for target in targets:
            if not target.exists():
                continue
            files.extend(target.glob("**/*.py"))
            files.extend(target.glob("**/*.json"))
            files.extend(target.glob("**/*.csv"))
            files.extend(target.glob("**/*.md"))
            files.extend(target.glob("**/*.yaml"))
            files.extend(target.glob("**/*.yml"))
            files.extend(target.glob("**/*.toml"))

        rows: list[NumericalProvenanceRow] = []
        counter = 0
        for path in sorted(set(files)):
            rel = str(path.relative_to(self.repo_root)).replace("\\", "/")
            if rel.startswith("warehouse/formulas/coefficients.csv"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if path.suffix == ".py":
                rows.extend(self._scan_python_file_constants(path, rel))
            else:
                for line_no, line in enumerate(text.splitlines(), start=1):
                    for match in NUMBER_PATTERN.finditer(line):
                        value = match.group(0)
                        if value in {"2026", "2027", "100"} and path.suffix in {".md", ".json"}:
                            continue
                        counter += 1
                        classification = _classify_generic_constant(value, rel)
                        rows.append(
                            NumericalProvenanceRow(
                                provenance_id=f"PV_MISC_{counter:06d}",
                                value=value,
                                unit="",
                                classification=classification,
                                formula_id="",
                                formula_version="",
                                file=rel,
                                function="",
                                line=line_no,
                                variable="",
                                description="Numeric token discovered by static scan.",
                                source_type="STATIC_SCAN",
                                source_id=f"{rel}:{line_no}",
                                paper_name="",
                                paper_link="",
                                scientific_quote="",
                                derivation="Static numeric extraction.",
                                status="VALID" if classification != "UNKNOWN" else "REVIEW_REQUIRED",
                                review_required="YES" if classification == "UNKNOWN" else "NO",
                            )
                        )
        return rows

    def _scan_python_file_constants(self, path: Path, rel: str) -> list[NumericalProvenanceRow]:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []
        rows: list[NumericalProvenanceRow] = []
        counter = 0
        function_stack: list[str] = []

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef):  # type: ignore[override]
                function_stack.append(node.name)
                self.generic_visit(node)
                function_stack.pop()

            def visit_Constant(self, node: ast.Constant):  # type: ignore[override]
                nonlocal counter
                if isinstance(node.value, (int, float)):
                    value = str(node.value)
                    classification = _classify_generic_constant(value, rel)
                    counter += 1
                    rows.append(
                        NumericalProvenanceRow(
                            provenance_id=f"PV_PY_{rel.replace('/','_')}_{counter}",
                            value=value,
                            unit="",
                            classification=classification,
                            formula_id="",
                            formula_version="",
                            file=rel,
                            function=function_stack[-1] if function_stack else "",
                            line=getattr(node, "lineno", 0),
                            variable="",
                            description="Python numeric literal affecting execution.",
                            source_type="CODE_CONSTANT",
                            source_id=f"{rel}:{getattr(node, 'lineno', 0)}",
                            paper_name="",
                            paper_link="",
                            scientific_quote="",
                            derivation="AST constant extraction.",
                            status="VALID" if classification != "UNKNOWN" else "REVIEW_REQUIRED",
                            review_required="YES" if classification == "UNKNOWN" else "NO",
                        )
                    )
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call):  # type: ignore[override]
                nonlocal counter
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                if func_name in {"float", "int", "round", "min", "max", "abs"}:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                            value = str(arg.value)
                            classification = _classify_generic_constant(value, rel)
                            counter += 1
                            rows.append(
                                NumericalProvenanceRow(
                                    provenance_id=f"PV_PY_CALL_{rel.replace('/','_')}_{counter}",
                                    value=value,
                                    unit="",
                                    classification=classification,
                                    formula_id="",
                                    formula_version="",
                                    file=rel,
                                    function=function_stack[-1] if function_stack else "",
                                    line=getattr(arg, "lineno", 0),
                                    variable="",
                                    description=f"Numeric argument inside {func_name}(...)",
                                    source_type="CODE_CALL_ARGUMENT",
                                    source_id=f"{rel}:{getattr(arg, 'lineno', 0)}",
                                    paper_name="",
                                    paper_link="",
                                    scientific_quote="",
                                    derivation=f"AST call-argument extraction for {func_name}.",
                                    status="VALID" if classification != "UNKNOWN" else "REVIEW_REQUIRED",
                                    review_required="YES" if classification == "UNKNOWN" else "NO",
                                )
                            )
                self.generic_visit(node)

        Visitor().visit(tree)
        return rows


def _classify_parameter(parameter_name: str) -> str:
    lowered = parameter_name.lower()
    if any(token in lowered for token in ("weight", "threshold", "scale", "denominator", "multiplier")):
        return "ENGINEERING_PARAMETER"
    return "ENGINEERING_PARAMETER"


def _classify_generic_constant(value: str, file_path: str) -> str:
    if value in {"0", "1", "0.0", "1.0", "100", "100.0"}:
        return "MATHEMATICAL_CONSTANT"
    if value in {"1000", "1000.0"}:
        return "UNIT_CONVERSION_CONSTANT"
    if file_path.startswith("tests/"):
        return "IMPLEMENTATION_CONSTANT"
    if file_path.startswith("warehouse/"):
        return "SCIENTIFIC_FACT"
    if "mathematics" in file_path or "optimization" in file_path:
        return "ENGINEERING_THRESHOLD"
    return "UNKNOWN"
