# BREEDS.csv

**Source path:** `data/breed_analysis/1_biological_traits/BREEDS.csv`

## Purpose

Canonical breed identity + biological trait defaults

## Columns

| # | Column |
|---|--------|
| 1 | `breed` |
| 2 | `size` |
| 3 | `body_type` |
| 4 | `coat_type` |
| 5 | `energy` |
| 6 | `weakness_group` |
| 7 | `skull_type` |
| 8 | `climate` |
| 9 | `lifespan` |
| 10 | `function_group` |

## Meaning

Rows: **48**. Column count: **10**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/calculation_trace.py`
- `app/agent/pipeline_trace.py`
- `app/agent/response_assembler.py`
- `app/agent/stages/biological.py`
- `app/agent/stages/epidemiology.py`
- `app/agent/stages/health_risk.py`
- `app/agent/utils.py`
- `app/agent/variable_map.py`
- `app/agent/wellness_map.py`
- `app/api/main.py`
- `app/api/payload_adapter.py`
- `app/data/assessment_diff.py`
- `app/data/clinical_assessment.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/debug_presets.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/breed.py`
- `app/inference/formula_registry.py`
- `app/ui/renderer/home.py`
- `app/ui/renderer/wellness.py`

## Formula

- `run_biological_stage`
- `compute_risk / RISK_V2_1`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
BREEDS.csv
->
run_biological_stage
->
traits on dog profile
->
compute_risk
->
ingredient_engine
->
package_optimizer
->
response_assembler
->
Clinical Assessment
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `reference/breeds.csv`
- Transform: identity + FK to trait dims

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `reference/breeds.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
