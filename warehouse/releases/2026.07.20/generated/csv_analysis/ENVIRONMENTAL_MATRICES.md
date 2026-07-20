# ENVIRONMENTAL_MATRICES.csv

**Source path:** `data/breed_analysis/2_evolutionary_profiles/ENVIRONMENTAL_MATRICES.csv`

## Purpose

Environment x trait guidance matrices

## Columns

| # | Column |
|---|--------|
| 1 | `trait_category` |
| 2 | `trait_value` |
| 3 | `trait` |
| 4 | `climate_context` |
| 5 | `dimension` |
| 6 | `compatibility_score` |
| 7 | `management_note` |
| 8 | `source_name` |
| 9 | `source_quote` |
| 10 | `source_url` |

## Meaning

Rows: **6**. Column count: **10**.

Status: **required**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/stages/biological.py`
- `app/agent/variable_map.py`
- `app/data/clinical_report_builder.py`
- `app/data/report_generator.py`
- `app/data/repository.py`

## Formula

- `run_biological_stage`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
ENVIRONMENTAL_MATRICES.csv
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
- Transform: map_type=environment

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
