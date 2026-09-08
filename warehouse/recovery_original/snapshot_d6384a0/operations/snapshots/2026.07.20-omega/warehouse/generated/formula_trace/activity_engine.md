# Activity / management formula trace

**Source:** management path + `CONDITION_ACTIVITIES.csv`; report rules in `ACTIVITY_PRESCRIPTION_RULES.csv`

## Call chain

```
management / assembler activity section
->
CONDITION_ACTIVITIES.csv (condition -> activity)
->
optional report enrichment <- ACTIVITY_PRESCRIPTION_RULES.csv
->
ACTIVITY_EVIDENCE.csv currently unused by engine formulas
->
returns activity recommendations in assembled response / reports
```

## Warehouse target

- `reference/activities.csv`
- `science/prevention_effectiveness.csv` (activity effectiveness)
- `runtime/lookup_maps.csv` (prescription rules)

## Do not change

No agent formula changes in Phase 1.
