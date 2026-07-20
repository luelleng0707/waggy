# CONDITION_PROTOCOLS.csv

**Source path:** `data/preventative_ingredients/CONDITION_PROTOCOLS.csv`

## Purpose

Condition protocols (unused by engine)

## Columns

| # | Column |
|---|--------|
| 1 | `condition` |
| 2 | `ingredient_name` |
| 3 | `recommended_daily_dose` |
| 4 | `dose_unit` |
| 5 | `priority_rank` |
| 6 | `source_name` |
| 7 | `source_quote` |
| 8 | `source_url` |
| 9 | `year` |
| 10 | `evidence_type` |

## Meaning

Rows: **12**. Column count: **10**.

Status: **unused**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/repository.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
CONDITION_PROTOCOLS.csv
->
(loaded by repository if manifested)
->
(no engine formula)
->
Validation Console browser only
```

## Safe to migrate?

Schema/mapping only in Phase 1. **Do not swap engine paths yet.**

- Warehouse target: `science/prevention_effectiveness.csv`
- Transform: unused today

## Unused columns

- `year` (all empty in source)

## Possible normalization

1. Map to `science/prevention_effectiveness.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
