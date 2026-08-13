# FUTURE_MATH_REPLACEMENT_BOUNDARY

## INPUT CONTRACT
- Accept `EvidenceGraph` and optional condition metadata, deterministic ordering by `condition_id`.
- Inputs remain warehouse-backed and provenance-traceable.

## OUTPUT CONTRACT
- Produce `MathematicsRuntimeResult` / `MathematicalAssessment` compatible outputs.
- Preserve fields: observed_prevalence, estimated_prevalence, agreement, confidence, novelty, priority, uncertainty, bounds.

## PROVENANCE CONTRACT
- Every output metric must provide source evidence traceability (fact IDs, citations where available).
- Engineering parameters must be explicitly labeled.

## FORMULA TRACE CONTRACT
- Emit per-formula traces with equation, substituted equation, inputs, parameters, intermediates, code reference, and status.
- Maintain replayability through `repository/math_debugger` interfaces.

## VERSION CONTRACT
- Formula IDs and versioning managed via formula-as-data in `repository/formulas` and `warehouse/formulas/*`.
- Replacement models must support controlled version rollout without API contract breakage.


## CURRENT_MODEL_STATUS
- Current Omega 9 formulas are audited current implementations, not scientifically final architecture.
- Omega 9.5 dispositions must be preserved during architecture cleanup:
  - MAT-1001 REVISE
  - MAT-1002 REPLACE
  - MAT-1003 REPLACE
  - MAT-1004 KEEP
  - MAT-1005 REVISE
  - MAT-1006 REPLACE
  - MAT-1007 REPLACE
  - MAT-1008 REPLACE

## REPLACEMENT_SAFETY
- Replacement estimator must preserve API payload compatibility and trace contracts.
- Formula replacement must not require frontend, warehouse, or optimization rewrites.
