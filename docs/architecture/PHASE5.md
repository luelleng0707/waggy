# Architecture notes (Phase 5)

Do **not** insert new layers inside:

```
Warehouse → Repository → ExecutionContext → FormulaGraph → AssessmentResult
```

Governance, validators, benchmarks, and dashboards run **outside** that path.
