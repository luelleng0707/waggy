# TRAIT_ATTRIBUTE_EXPLANATIONS.csv

**Source path:** `data/breed_analysis/2_evolutionary_profiles/TRAIT_ATTRIBUTE_EXPLANATIONS.csv`

## Purpose

Trait attribute copy for reports

## Columns

| # | Column |
|---|--------|
| 1 | `trait_category` |
| 2 | `trait_value` |
| 3 | `card_title` |
| 4 | `explanation` |
| 5 | `related_conditions` |
| 6 | `evidence_level` |
| 7 | `evidence_id` |
| 8 | `source_csv` |
| 9 | `source_name` |
| 10 | `source_url` |

## Meaning

Rows: **10**. Column count: **10**.

Status: **partially_required**.

## Who reads it

### Python files

- `app/data/clinical_report_builder.py`
- `app/data/report_generator.py`
- `app/data/repository.py`
- `app/inference/formula_registry.py`

## Formula

- `(none / report-only / unused)`

## Output

- Consumed into analyze/assess/clinical JSON and/or Validation Console.

## Dependency graph

```
TRAIT_ATTRIBUTE_EXPLANATIONS.csv
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
- Transform: map_type=trait_explain

## Unused columns

- None detected as all-empty. See `unused_columns.json` for unreferenced names.

## Possible normalization

1. Map to `runtime/lookup_maps.csv`.
2. Extract citation fields into `reference/papers.csv` + `paper_id`.
3. Convert numeric units via `runtime/unit_conversion.csv`.
