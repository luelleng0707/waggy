"""App core — shared paths and frozen-architecture constants."""

from app.core.paths import REPO_ROOT, WAREHOUSE_CURRENT, clinical_root_str, resolve_clinical_root

__all__ = [
    "REPO_ROOT",
    "WAREHOUSE_CURRENT",
    "resolve_clinical_root",
    "clinical_root_str",
]
