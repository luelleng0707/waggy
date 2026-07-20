# Package optimizer formula trace

**Source:** `app/agent/package_optimizer.py` (+ `stages/optimization.py`)

## Call chain

```
build_optimized_packages(...)
->
load_candidate_products() <- PRODUCT_CATALOG + COMPONENTS + PRICING + FEEDING + FUNCTIONS + EXT_*
->
_targets_from_ingredients() <- nutrition targets from map_ingredients
->
coverage_matrix() + alias match via INGREDIENT_ALIASES
->
_pick_staple() <- PACKAGE_TIERS
->
_optimize_essential / _optimize_balanced / _optimize_optimal
->
_overall_score (coverage - surplus + clinical function)
->
returns package tiers / line items
```

## Warehouse target

- `science/product_composition.csv`
- `runtime/parameter_defaults.csv` (tiers, pricing)
- `runtime/lookup_maps.csv` (feeding, functions)
- `runtime/aliases.csv` (ingredient aliases)

## Do not change

No edits to `package_optimizer.py` in Phase 1.
