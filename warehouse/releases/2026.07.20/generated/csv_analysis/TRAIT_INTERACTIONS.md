# TRAIT_INTERACTIONS.csv

**Source path:** `data/breed_analysis/3_management_considerations/TRAIT_INTERACTIONS.csv`

## Purpose

Multiplicative trait pair risk modifiers

## Columns

| # | Column |
|---|--------|
| 1 | `trait_a` |
| 2 | `trait_b` |
| 3 | `condition` |
| 4 | `interaction` |
| 5 | `factor` |
| 6 | `reason` |
| 7 | `source` |

## Meaning

Rows: **10**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/stages/epidemiology.py`
- `app/agent/stages/health_risk.py`
- `app/agent/variable_map.py`
- `app/data/clinical_assessment.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `apply_trait_interactions -> compute_risk`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
TRAIT_INTERACTIONS.csv
->
health_risk modifiers
->
compute_risk
->
downstream nutrition + packages
->
response_assembler
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/mixed_trait_interactions.csv`
- Transform: rename; keep multipliers

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/mixed_trait_interactions.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
