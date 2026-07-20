# Risk engine formula trace

**Source of truth (production):** `app/agent/stages/health_risk.py`  
**Status:** Phase 1 documentation only - formulas unchanged; still reads `data/`.

## Entry

`compute_risks(repo, profile)` / RISK_V2_1 - `app/agent/stages/health_risk.py`

## Call chain (actual functions)

```
compute_risks()
->
_breed_records() <- BREEDS.csv (+ normalize via BREED_ALIASES.csv)
->
collect_trait_risks()
  ->
  for each trait category on breed records:
    repository trait_*_conditions tables
    SIZE | BODYTYPE | COATTYPE | ENERGY | SKULLTYPE |
    FUNCTIONGROUP | WEAKNESSGROUP | CLIMATE | LIFESPAN
    ->
    reads prevalence / observed percent
->
compute_evidence_scores()
  <- BREED_CONDITIONS.csv
  <- TRAIT_INTERACTIONS.csv (multipliers; clamp 0.80-1.20)
->
apply_benefit_reductions() <- TRAIT_BENEFITS.csv
->
apply_mixed_breed_nudge() <- MIXED_BREED_MATRIX.csv (if mixed)
->
apply_significance_logic()
->
returns ranked risks with risk_percent (+ formula_execution debug)
```

## Columns that matter

- Prevalence / observed percent on condition tables
- Multiplier on TRAIT_INTERACTIONS
- Benefit magnitude on TRAIT_BENEFITS
- Mixed matrix factor on MIXED_BREED_MATRIX

## Warehouse target

- `science/breed_condition_risk.csv`
- `science/trait_condition_risk.csv` (all 9 trait tables collapsed)
- `science/mixed_trait_interactions.csv`
- `science/prevention_effectiveness.csv` (benefits)
- `reference/papers.csv` via `paper_id`

## Do not change

No edits to `health_risk.py` in Phase 1.
