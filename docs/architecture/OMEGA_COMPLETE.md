# Phase Ω definition of complete

Every question below is answered by generated artifacts / APIs:

| Question | Where |
|----------|--------|
| Why this recommendation? | Knowledge graph + `/api/v1/graph/why` + FormulaGraph trace |
| Which formulas? | `GET /api/v1/platform/formulas` + FORMULA_OBSERVATORY |
| Which papers? | SCIENCE_OBSERVATORY + graph |
| Which CSV rows? | `_csv_row` + repository browser + dependency observatory |
| What if paper disappears? | ScientificImpactAnalyzer + dependency graph |
| What changed between releases? | science_pipeline + snapshots + RELEASE_HISTORY |
| Rollback? | `py -3 -m ppie_platform.omega --rollback VERSION` |
| Performance? | PERFORMANCE_OBSERVATORY + BENCHMARK_REPORT |
| Security? | SECURITY_AUDIT.md |

Core engine: frozen. Extend via datasets, nodes, plugins, dashboards, reports.
