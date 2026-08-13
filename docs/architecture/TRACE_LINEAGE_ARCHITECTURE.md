# TRACE_LINEAGE_ARCHITECTURE

## Canonical lineage chain

`request_id -> correlation_id -> runtime_stage -> formula_execution -> warehouse_lookup -> evidence -> intermediate_value -> output -> presentation`

## Current implementation mapping

| Lineage concept | Current representation |
|---|---|
| request_id | implicit per HTTP request (no canonical public request_id field across all endpoints) |
| correlation_id | `presentation_correlation_id` in `/api/v1/presentation/three-surfaces` |
| runtime_stage | node-level execution traces in app runtime (`FormulaGraph` stages) |
| formula_execution | debug/validation console `execution_records` |
| warehouse_lookup | debug lookup sections and repository warehouse trace tooling |
| evidence | scientific evidence payload + debug evidence status fields |
| intermediate_value | available in debug formula traces where emitted |
| output | analyze payload + assessment projection + presentations |
| presentation | customer/business/developer projections |

## Trace categories (must remain distinct)

- **Application trace**: HTTP timing/version headers and route lifecycle logs
- **Scientific provenance trace**: evidence/citation lineage and row-level support
- **Mathematical execution trace**: formula-level inputs/params/intermediate/output
- **Optimization trace**: candidate scoring, constraints, package selection logic
- **Presentation trace**: projection identity (`analysis_signature`, `presentation_correlation_id`) and route-specific visibility

Do not collapse these into one undifferentiated trace type.
