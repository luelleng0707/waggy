# FORMULA_DEPENDENCY_GRAPH

```text
Observed evidence values [OBSERVED]
    ↓
MAT-1001 Observed prevalence mean [CALCULATED]
    ↓
Trait/Environment/Interaction evidence [OBSERVED]
    ↓
MAT-1002 Weighted logit aggregation [CALCULATED]
    ↓
MAT-1003 Prior-evidence logit blend + interaction delta [ASSUMED+CALCULATED]
    ↓
MAT-1004 Relative error agreement [CALCULATED]
    ↓
MAT-1005 Composite confidence score [ASSUMED+CALCULATED]
    ↓
MAT-1006 Novelty score [CALCULATED]
    ↓
MAT-1008 Uncertainty band factor [ASSUMED+CALCULATED]
    ↓
MAT-1007 Priority ranking signal [CALCULATED]
```

## Node semantics

- `OBSERVED`: value comes directly from warehouse evidence rows.
- `DERIVED`: value computed from observed dataset aggregates before formula output.
- `ASSUMED`: engineering parameter/threshold from formula coefficients.
- `CALCULATED`: runtime formula output from inputs and parameters.
