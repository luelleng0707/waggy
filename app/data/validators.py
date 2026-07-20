"""Schema and relationship validation for the data platform."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

from app.data.schemas import FileSpec, Manifest

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _pk_cols(spec: FileSpec) -> list[str]:
    return list(spec.primary_key)


def validate_tables(manifest: Manifest, tables: dict[str, pd.DataFrame]) -> ValidationReport:
    report = ValidationReport()
    by_table = manifest.by_table()

    for spec in manifest.files:
        df = tables.get(spec.table)
        if df is None:
            report.errors.append(f"Table not loaded: {spec.table}")
            continue

        missing_cols = [c for c in spec.required_columns if c not in df.columns]
        if missing_cols:
            report.errors.append(
                f"{spec.path}: missing required columns {missing_cols}"
            )

        unknown = [c for c in df.columns if c not in set(spec.required_columns) | set(df.columns)]
        # Unknown = present in DF but not in required — warn for extras beyond required
        extras = [c for c in df.columns if c not in spec.required_columns]
        # Only warn if we want to flag schema drift; extras are allowed with warning
        if extras and spec.required_columns:
            # soft: warn once per file about columns outside required set when they look unexpected
            # All extras are "unknown" relative to required_columns list in manifest
            declared = set(spec.required_columns) | set(spec.primary_key)
            unknown_cols = [c for c in df.columns if c not in declared]
            # Optional evidence / metadata columns are expected; log at debug.
            if unknown_cols:
                logger.debug(
                    "DATA WARN: %s columns not listed as required: %s",
                    spec.path,
                    unknown_cols,
                )

        if df.empty:
            if spec.allow_empty:
                continue
            report.warnings.append(f"{spec.path}: table is empty")
            continue

        for col in spec.required_columns:
            if col not in df.columns:
                continue
            blank = df[col].astype(str).str.strip() == ""
            if blank.any():
                n = int(blank.sum())
                report.errors.append(
                    f"{spec.path}: {n} empty value(s) in required column '{col}'"
                )

        pk = _pk_cols(spec)
        if pk and all(c in df.columns for c in pk):
            dup_mask = df.duplicated(subset=pk, keep=False)
            if dup_mask.any():
                n = int(dup_mask.sum())
                report.errors.append(
                    f"{spec.path}: {n} duplicate primary key row(s) on {pk}"
                )

    # Foreign keys (exact join — never fuzzy)
    for spec in manifest.files:
        df = tables.get(spec.table)
        if df is None or df.empty:
            continue
        for fk in spec.foreign_keys:
            parent = tables.get(fk.ref_table)
            if parent is None:
                report.errors.append(
                    f"{spec.path}: FK {fk.column} → missing parent table {fk.ref_table}"
                )
                continue
            if fk.column not in df.columns:
                report.errors.append(
                    f"{spec.path}: FK column '{fk.column}' not present"
                )
                continue
            if fk.ref_column not in parent.columns:
                report.errors.append(
                    f"{spec.path}: FK parent column '{fk.ref_table}.{fk.ref_column}' missing"
                )
                continue
            child_vals = df[fk.column].astype(str).str.strip()
            child_vals = child_vals[child_vals != ""]
            parent_vals = set(parent[fk.ref_column].astype(str).str.strip())
            orphans = sorted(set(child_vals) - parent_vals)
            if orphans:
                sample = orphans[:8]
                more = f" (+{len(orphans) - 8} more)" if len(orphans) > 8 else ""
                # Soft FK: warn so storefront CSV edits (add/remove catalog rows)
                # can hot-reload without requiring every child table updated in lockstep.
                report.warnings.append(
                    f"{spec.path}: FK {fk.column} → {fk.ref_table}.{fk.ref_column} "
                    f"orphans: {sample}{more}"
                )

    for warning in report.warnings:
        logger.warning("DATA WARN: %s", warning)
    for error in report.errors:
        logger.error("DATA ERROR: %s", error)

    return report


class DataValidationError(RuntimeError):
    """Raised when required CSV schema/integrity checks fail."""

    def __init__(self, report: ValidationReport):
        self.report = report
        msg = "; ".join(report.errors[:12])
        if len(report.errors) > 12:
            msg += f" … (+{len(report.errors) - 12} more)"
        super().__init__(f"Data platform validation failed: {msg}")
