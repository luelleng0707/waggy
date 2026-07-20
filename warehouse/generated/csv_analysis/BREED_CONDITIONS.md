# BREED_CONDITIONS.csv

**Source path:** `data/breed_analysis/3_management_considerations/BREED_CONDITIONS.csv`

## Purpose

Breed -> condition prevalence + citations

## Columns

| # | Column |
|---|--------|
| 1 | `breed` |
| 2 | `condition` |
| 3 | `prevalence` |
| 4 | `sample_population` |
| 5 | `sample_size` |
| 6 | `source_name` |
| 7 | `source_quote` |
| 8 | `source_url` |
| 9 | `year` |
| 10 | `confidence_level` |

## Meaning

Rows: **16**. Column count: **10**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/calculation_trace.py`
- `app/agent/pipeline_trace.py`
- `app/agent/stages/epidemiology.py`
- `app/agent/stages/health_risk.py`
- `app/agent/variable_map.py`
- `app/api/evidence.py`
- `app/data/clinical_report_builder.py`
- `app/data/console_inspectors.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `compute_risk`
- `epidemiology stage`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
BREED_CONDITIONS.csv
->
repository.trait_condition_tables / breed_conditions
->
health_risk.compute_risk (RISK_V2_1)
->
epidemiology stage
->
ingredient_engine.map_ingredients
->
package_optimizer.build_packages
->
response_assembler
->
Clinical Assessment / analyze JSON
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/breed_condition_risk.csv`
- Transform: citation -> paper_id

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `science/breed_condition_risk.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
