# ACTIVITY_EVIDENCE.csv

**Source path:** `data/breed_analysis/4_preventative_interventions/ACTIVITY_EVIDENCE.csv`

## Purpose

Activity evidence citations (unused by engine)

## Columns

| # | Column |
|---|--------|
| 1 | `activity_name` |
| 2 | `source_name` |
| 3 | `source_quote` |
| 4 | `source_url` |
| 5 | `year` |

## Meaning

Rows: **10**. Column count: **5**.

Status: **unused**.

## Who reads it

### Python files

- `app/agent/pipeline_trace.py`
- `app/agent/variable_map.py`
- `app/data/repository.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
ACTIVITY_EVIDENCE.csv
->
(loaded by repository if manifested)
->
(no engine formula)
->
Validation Console browser only
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `reference/papers.csv (+ prevention)`
- Transform: unused today

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `reference/papers.csv (+ prevention)`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
