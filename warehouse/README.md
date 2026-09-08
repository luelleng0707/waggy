# Warehouse

Canonical scientific and commercial facts for the running system. See [docs/WAGGY_SYSTEM.md](../docs/WAGGY_SYSTEM.md).

```
warehouse/biology/*.csv
warehouse/prevention/*.csv
warehouse/reference/papers.csv
warehouse/commercial/*.csv
        ↓
DataRepository + scientific_care.resolve_care_model
        ↓
PACKAGE_OPTIMIZER_V2_1 → API → workbench
```

Do not invent prevalence, citations, or breed–condition links. Do not convert `NEEDS_VALIDATION` or `MISSING_PROVENANCE` into validated science. Do not write runtime inference back into these CSVs.

`warehouse/recovery_original/` is **read-only** intern recovery material.

`warehouse/science/` is **not** the current Health Analysis path. Historical MAT / mechanism CSVs used by warehouse-backed mathematics tests may still load through `repository/warehouse`.

Package tier discounts and product defaults are Repository policy constants (not CSVs).
