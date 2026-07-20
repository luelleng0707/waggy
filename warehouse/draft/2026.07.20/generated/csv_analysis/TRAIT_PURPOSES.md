# TRAIT_PURPOSES.csv

**Source path:** `data/breed_analysis/2_evolutionary_profiles/TRAIT_PURPOSES.csv`

## Purpose

Trait purpose narratives for biological stage

## Columns

| # | Column |
|---|--------|
| 1 | `trait_category` |
| 2 | `trait_value` |
| 3 | `biological_purpose` |
| 4 | `advantage_summary` |
| 5 | `source_name` |
| 6 | `source_quote` |
| 7 | `source_url` |

## Meaning

Rows: **5**. Column count: **7**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/stages/biological.py`
- `app/agent/variable_map.py`
- `app/data/clinical_report_builder.py`
- `app/data/engine_trace.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `run_biological_stage`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
TRAIT_PURPOSES.csv
->
repository / report_generator
->
clinical_report_builder (if report path)
->
response_assembler (if wired)
->
Validation Console
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `runtime/lookup_maps.csv`
- Transform: map_type=trait_purpose

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
