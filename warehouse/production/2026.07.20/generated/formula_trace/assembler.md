# Response assembler formula trace

**Source:** `app/agent/response_assembler.py`

## Call chain

```
assemble_analyze_response / equivalent
->
biological profile (from bio stage)
->
risk ranking (from health_risk)
->
nutrition targets (from ingredient_engine)
->
packages (from package_optimizer)
->
enrich with:
  NUTRIENT_PRIORITIES
  NATURAL_FOOD_SOURCES
  INGREDIENT_MECHANISMS / EVIDENCE
  CONDITION_ACTIVITIES
  report tables (timeline, trait explanations, ...) when clinical report path
->
returns API JSON consumed by demo UI + Validation Console
```

## Note

Assembler **assembles**; it does not recompute RISK_V2_1 math.

## Do not change

No edits to `response_assembler.py` in Phase 1.
