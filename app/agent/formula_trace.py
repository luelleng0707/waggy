"""
Formula execution ledger helpers — Phase 6 provenance.

Observability only. Never changes clinical math.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import perf_counter
from typing import Any

TRAIT_TABLE_FILES = {
    "size": "SIZE_CONDITIONS.csv",
    "body_type": "BODYTYPE_CONDITIONS.csv",
    "coat_type": "COATTYPE_CONDITIONS.csv",
    "energy": "ENERGY_CONDITIONS.csv",
    "skull_type": "SKULLTYPE_CONDITIONS.csv",
    "climate": "CLIMATE_CONDITIONS.csv",
    "function_group": "FUNCTIONGROUP_CONDITIONS.csv",
    "weakness_group": "WEAKNESSGROUP_CONDITIONS.csv",
    "lifespan": "LIFESPAN_CONDITIONS.csv",
}

FORMULA_META = {
    "RISK_V2_1": {
        "formula_name": "Condition Risk Ranking",
        "stage": "Health Risk",
        "code": {"file": "app/agent/stages/health_risk.py", "function": "compute_risks"},
        "consumers": ["NUTRIENT_TARGET_V2_1", "PACKAGE_OPTIMIZER_V2_1", "ASSESSMENT_PROJECT_V1"],
    },
    "NUTRIENT_TARGET_V2_1": {
        "formula_name": "Condition → Nutrient Targets",
        "stage": "Nutrition",
        "code": {"file": "app/agent/ingredient_engine.py", "function": "map_ingredients"},
        "consumers": ["PRODUCT_MATCH_V2_1", "PACKAGE_OPTIMIZER_V2_1", "COVERAGE_V2_1"],
    },
    "PACKAGE_OPTIMIZER_V2_1": {
        "formula_name": "Tier Package Optimizer",
        "stage": "Package Optimization",
        "code": {"file": "app/agent/package_optimizer.py", "function": "build_optimized_packages"},
        "consumers": ["ASSESSMENT_PROJECT_V1", "wellnessPackages UI"],
    },
    "COVERAGE_V2_1": {
        "formula_name": "Nutrient Coverage Ratio",
        "stage": "Package Optimization",
        "code": {"file": "app/agent/package_optimizer.py", "function": "coverage_matrix"},
        "consumers": ["PACKAGE_OPTIMIZER_V2_1"],
    },
}


@dataclass
class LookupResult:
    """Repository-style lookup with provenance (propagated into formula_execution)."""

    value: Any
    table: str
    column: str
    primary_key: dict[str, Any] = field(default_factory=dict)
    csv_row: Any = None
    csv_file: str | None = None
    row_id: str | None = None
    evidence_id: Any = None
    matched: bool = True
    matched_on: list[str] = field(default_factory=list)
    selected_columns: dict[str, Any] = field(default_factory=dict)
    decision: str | None = None

    def to_lookup(self) -> dict[str, Any]:
        return lookup_row(
            table=self.table,
            primary_key=self.primary_key,
            columns=self.selected_columns or {self.column: self.value},
            csv_row=self.csv_row,
            csv_file=self.csv_file,
            evidence_id=self.evidence_id,
            matched=self.matched,
            matched_on=self.matched_on or list(self.primary_key.keys()),
            decision=self.decision,
            column=self.column,
        )

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def empty_execution(
    formula_id: str,
    *,
    condition: str | None = None,
    subject: str | None = None,
) -> dict[str, Any]:
    meta = FORMULA_META.get(formula_id) or {}
    return {
        "schema": "formula_execution.v2",
        "formula_id": formula_id,
        "formula_name": meta.get("formula_name") or formula_id,
        "stage": meta.get("stage") or "Unknown",
        "condition": condition,
        "subject": subject or condition,
        "inputs": {},
        "lookups": [],
        "competitions": [],
        "steps": [],
        "modifiers": [],
        "decisions": [],
        "confidence": [],
        "confidence_steps": [],  # alias kept for Phase 5 consumers
        "outputs": {},
        "timing": {},
        "consumers": list(meta.get("consumers") or []),
        "code": dict(meta.get("code") or {}),
        "provenance": [],
    }


def _is_num(v: Any) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _normalize_csv_row(csv_row: Any) -> Any:
    if csv_row in (None, "", "nan"):
        return None
    if isinstance(csv_row, bool):
        return csv_row
    if isinstance(csv_row, int):
        return csv_row
    if isinstance(csv_row, float) and csv_row == int(csv_row):
        return int(csv_row)
    s = str(csv_row).strip()
    if s.isdigit():
        return int(s)
    if _is_num(csv_row):
        try:
            f = float(csv_row)
            return int(f) if f == int(f) else f
        except (TypeError, ValueError):
            return csv_row
    return csv_row


def make_row_id(table: str, csv_row: Any) -> str | None:
    row = _normalize_csv_row(csv_row)
    if row is None:
        return None
    base = str(table or "ROW").replace(".csv", "").replace(" ", "_").upper()
    return f"{base}_{row}"


def lookup_row(
    *,
    table: str,
    primary_key: dict[str, Any],
    columns: dict[str, Any],
    csv_row: Any = None,
    csv_file: str | None = None,
    evidence_id: Any = None,
    matched: bool = True,
    matched_on: list[str] | None = None,
    decision: str | None = None,
    column: str | None = None,
) -> dict[str, Any]:
    file_name = csv_file or (table if str(table).lower().endswith(".csv") else f"{table}.csv")
    row = _normalize_csv_row(csv_row)
    return {
        "table": str(table).replace(".csv", "") if str(table).lower().endswith(".csv") else str(table),
        "csv_file": file_name if str(file_name).lower().endswith(".csv") else f"{file_name}.csv",
        "csv_row": row,
        "row_id": make_row_id(file_name, row),
        "primary_key": primary_key or {},
        "matched": matched,
        "matched_on": matched_on if matched_on is not None else list((primary_key or {}).keys()),
        "selected_columns": columns or {},
        "columns": columns or {},  # Phase 5 alias
        "column": column,
        "evidence_id": evidence_id,
        "decision": decision,
    }


def lookup_competition(
    *,
    purpose: str,
    candidates: list[dict[str, Any]],
    selected: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "purpose": purpose,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "selected": selected,
        "reason": reason,
    }


def step(
    n: int,
    name: str,
    *,
    expression: str | None = None,
    inputs: Any = None,
    before: Any = None,
    after: Any = None,
    result: Any = None,
    unit: str | None = None,
    lookups: list | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    return {
        "step": n,
        "name": name,
        "expression": expression,
        "inputs": inputs if inputs is not None else {},
        "before": before,
        "after": after,
        "result": result if result is not None else after,
        "unit": unit,
        "lookups": lookups or [],
        "note": note,
    }


def modifier(
    name: str,
    *,
    source_table: str | None,
    source_row: Any = None,
    primary_key: dict | None = None,
    effect: str,
    op: str,
    value: Any,
    running_total_before: Any,
    running_total_after: Any,
    unit: str = "%",
    details: Any = None,
    row_id: str | None = None,
) -> dict[str, Any]:
    return {
        "modifier": name,
        "source_table": source_table,
        "csv_row": source_row,
        "row_id": row_id or (make_row_id(source_table or "ROW", source_row) if source_row is not None else None),
        "primary_key": primary_key or {},
        "effect": effect,
        "op": op,
        "value": value,
        "before": running_total_before,
        "after": running_total_after,
        "running_total_before": running_total_before,
        "running_total_after": running_total_after,
        "unit": unit,
        "details": details,
    }


def decision(
    outcome: str,
    *,
    subject: str | None = None,
    reasons: list[str] | None = None,
    score: Any = None,
    threshold: Any = None,
    details: Any = None,
) -> dict[str, Any]:
    return {
        "decision": outcome,
        "subject": subject,
        "reasons": reasons or [],
        "score": score,
        "threshold": threshold,
        "details": details,
    }


def confidence_factor(
    factor: str,
    *,
    delta: Any,
    running: Any,
    expression: str | None = None,
    note: str | None = None,
    value: Any = None,
    denominator: Any = None,
) -> dict[str, Any]:
    """
    Confidence ledger entry.

    RISK_V2_1 uses a single coverage factor (not an additive study ladder).
    Emit actual algorithm only — do not invent fake deltas.
    """
    return {
        "factor": factor,
        "delta": delta,
        "running": running,
        "running_confidence": running,
        "contribution_percent": delta if isinstance(delta, (int, float)) else None,
        "value": value if value is not None else delta,
        "denominator": denominator,
        "expression": expression,
        "note": note,
    }


def provenance_link(
    *,
    display_value: Any,
    csv_file: str | None,
    row_id: str | None = None,
    csv_row: Any = None,
    primary_key: dict | None = None,
    column: str | None = None,
    formula_step: str | None = None,
    contribution: Any = None,
    final_output: Any = None,
    evidence_id: Any = None,
) -> dict[str, Any]:
    return {
        "display_value": display_value,
        "csv_file": csv_file,
        "row_id": row_id or make_row_id(csv_file or "ROW", csv_row),
        "csv_row": _normalize_csv_row(csv_row),
        "primary_key": primary_key or {},
        "column": column,
        "evidence_id": evidence_id,
        "formula_step": formula_step,
        "contribution": contribution,
        "final_output": final_output,
    }


def start_timer() -> float:
    return perf_counter()


def timing_ms(started: float, *, lookups: int = 0, matched: int = 0, warnings: list | None = None) -> dict[str, Any]:
    return {
        "elapsed_ms": round((perf_counter() - started) * 1000, 3),
        "lookup_count": lookups,
        "rows_matched": matched,
        "cache": "NOT CURRENTLY TRACEABLE",
        "warnings": warnings or [],
    }


def seal_execution(
    exec_ledger: dict[str, Any],
    *,
    started: float | None = None,
    rebuild_provenance: bool = True,
) -> dict[str, Any]:
    """Normalize aliases and optional timing before attach."""
    conf = list(exec_ledger.get("confidence") or exec_ledger.get("confidence_steps") or [])
    exec_ledger["confidence"] = conf
    exec_ledger["confidence_steps"] = conf
    if started is not None:
        exec_ledger["timing"] = timing_ms(
            started,
            lookups=len(exec_ledger.get("lookups") or []),
            matched=sum(1 for lu in (exec_ledger.get("lookups") or []) if isinstance(lu, dict) and lu.get("matched")),
        )
    # Build flat provenance from selected lookups
    if rebuild_provenance or not exec_ledger.get("provenance"):
        prov = []
        for lu in exec_ledger.get("lookups") or []:
            if not isinstance(lu, dict) or lu.get("decision") in (
                "skipped_lower_than_category_max",
                "not_selected",
            ):
                continue
            cols = lu.get("selected_columns") or lu.get("columns") or {}
            for col, val in list(cols.items())[:3]:
                prov.append(
                    provenance_link(
                        display_value=val,
                        csv_file=lu.get("csv_file") or lu.get("table"),
                        row_id=lu.get("row_id"),
                        csv_row=lu.get("csv_row"),
                        primary_key=lu.get("primary_key"),
                        column=col,
                        formula_step=lu.get("decision"),
                        evidence_id=lu.get("evidence_id"),
                        final_output=(exec_ledger.get("outputs") or {}).get("final_risk_percent")
                        or (exec_ledger.get("outputs") or {}).get("daily_dose")
                        or (exec_ledger.get("outputs") or {}).get("overall_score"),
                    )
                )
        exec_ledger["provenance"] = prov[:40]
    return exec_ledger
