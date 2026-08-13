# MATHEMATICAL_AUDIT_GUIDE

## End-to-end audit flow

1. `EvidenceGraph` enters `ScientificMathematicsRuntime`.
2. Condition nodes are enumerated deterministically by `condition_id`.
3. Formula version resolution loads coefficients from `warehouse/formulas/*` through `repository/formulas/runtime.py`.
4. Each formula stage executes in order:
   - `MAT-1001` observed prevalence
   - `MAT-1002` trait aggregation
   - `MAT-1003` bayesian update
   - `MAT-1004` agreement
   - `MAT-1005` confidence
   - `MAT-1006` novelty
   - `MAT-1008` uncertainty
   - `MAT-1007` priority
5. Each stage emits a `MathematicalFormulaTrace` with:
   - equation
   - substituted equation
   - input values
   - parameters
   - intermediate values
   - output
   - code reference
   - evidence provenance
6. `repository/math_debugger` replay re-executes real runtime and returns `ExecutionTrace`.

## How to replay a number

1. Build `EvidenceGraph` from live warehouse-backed pipeline.
2. Call:
   - `MathDebuggerRuntime.trace(evidence_graph, condition_assessments, formula_version_overrides)`
3. Locate target condition formula chain in `execution_tree`.
4. Inspect each `FormulaTrace`:
   - generic equation
   - substituted equation
   - intermediate calculations
   - output variable/value
5. Cross-open code via `code_reference`.
6. Cross-open formula docs in `docs/mathematics/*`.
7. Verify warehouse citations from `warehouse_trace_rows`.

## Missing evidence handling

- If observed evidence is absent, `MAT-1001` trace status is `NO_EVIDENCE`.
- The debugger reports missing evidence; it does not synthesize values.
- Any stage lacking explicit intermediate values is marked with `REVIEW_REQUIRED` warning.

## Formula version switching

- Versions are selected by `repository/formulas/resolver.py`.
- Active defaults come from `formula_versions.csv`.
- Explicit version overrides are passed per formula ID.
- Backward compatibility test ensures default and explicit v1 output equality for current active behavior.

## Manual reproducibility checklist

For any final value:

1. confirm formula ID + version
2. confirm parameter set and coefficient values
3. confirm equation text
4. recompute substituted equation
5. verify intermediate values
6. verify output
7. verify evidence row IDs + quote/paper/link
8. verify code function + line range

## Ω9.3 provenance workflow

1. Build repository-wide numerical inventory:
   - `NumericalInventoryBuilder().build()`
2. Export provenance manifest:
   - `NumericalInventoryBuilder().export_csv(Path("docs/mathematics/NUMERICAL_PROVENANCE.csv"))`
3. Review all rows where:
   - `classification == UNKNOWN`, or
   - `status == ENGINEERING_ASSUMPTION`, or
   - `review_required == YES`
4. Cross-check constants in executable mathematics modules:
   - `FormulaConstantValidator().audit()`
5. Validate replay triangulation:
   - production trace output
   - independent replay output
   - absolute delta vs tolerance (`3e-5`)

## Independent replay workflow

1. Get production trace with `MathDebuggerRuntime.trace(...)`.
2. Select formula trace to verify.
3. Run `IndependentFormulaReplay.replay_formula(trace)`.
4. Confirm `status == MATCH`.
5. Persist calculation artifact under `docs/mathematics/replays/`.

## Sensitivity analysis workflow

1. Select a formula trace with parameter variables.
2. Run `SensitivityAnalyzer.analyze(trace)`.
3. Inspect for large absolute or relative output changes under +-10 percent parameter perturbation.
4. Treat high-impact parameters as publication-risk assumptions unless numerically supported.

## Uncertainty and confidence interpretation

- `MAT-1008` represents model dispersion from trait/environment prevalence spread and scaling factor.
- `MAT-1005` confidence is a composite model score from:
  - evidence quantity component,
  - study-count component,
  - agreement component.
- Current runtime does not fully separate:
  - scientific uncertainty,
  - model uncertainty,
  - parameter uncertainty,
  - data absence.
- Ω9.3 audit documents this behavior without changing production outputs.

## Ω9.5 methodology workflow

1. Freeze current model semantics in `docs/mathematics/OMEGA9_CURRENT_MODEL.md`.
2. Review dependency and duplication paths in `docs/mathematics/MATHEMATICAL_DEPENDENCY_GRAPH.md`.
3. Audit MAT-1002 parameter provenance in `docs/mathematics/MAT1002_PARAMETER_AUDIT.csv`.
4. Record environment assumptions in `docs/mathematics/ENVIRONMENT_MODEL_AUDIT.md`.
5. Record priority dependency propagation in `docs/mathematics/MAT1007_DEPENDENCY_AUDIT.csv`.
6. Record scientific/engineering boundary in `docs/mathematics/SCIENTIFIC_ENGINEERING_BOUNDARY.md`.
7. Track warehouse validation blockers in `docs/mathematics/WAREHOUSE_BLOCKERS.md`.
8. Maintain proposed migration disposition in `docs/mathematics/PROPOSED_FORMULA_REGISTRY.md`.
