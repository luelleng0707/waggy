# SCIENCE_MODEL.md

Science-only warehouse.

## Layout

```
warehouse/science/
  breed/          breeds, conditions links, environment, activity, mixed-breed
  condition/      conditions, protocols, timelines, grooming
  ingredient/     ingredients, condition links, mechanisms, evidence, aliases
  nutrition/      foods, nutrients, sources, priorities, life stages
  product/        PRODUCT_CATALOG, COMPONENTS, FUNCTIONS, FEEDING_RULES, PRICING, TREAT_BAKERY
  physiology/     traits, trait science, benefits
  evidence/       papers, clinical evidence
  runtime/        aliases, parameters, units
```

`reference/` and top-level `runtime/` no longer exist. All CSVs live under `science/`.

## Rules

- One scientific concept → one table when practical
- Repository is the only layer that knows CSV paths
- FormulaGraph only consumes in-memory views / repository APIs
- Package tier discounts and product defaults are Repository policy constants (not CSVs)
- Empty `SUPPLEMENTS.csv` is omitted until supplements exist
