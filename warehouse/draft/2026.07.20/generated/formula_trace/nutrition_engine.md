# Nutrition stage formula trace

**Source:** `app/agent/stages/nutrition.py` -> delegates to `ingredient_engine`

## Call chain

```
run_nutrition_stage(...)
->
ingredient_engine.map_ingredients
->
CONDITION_INGREDIENTS (+ evidence/mechanisms as attached)
->
passes targets to optimization stage
```

See `ingredient_engine.md` for CSV detail.

## Do not change

No edits in Phase 1.
