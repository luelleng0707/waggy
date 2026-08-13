# Warehouse — science-only scientific database

```
warehouse/science/{domain}/*.csv
        ↓
Repository (in-memory formula views + domain repositories)
        ↓
FormulaGraph → AssessmentResult → API
```

All scientific CSVs live under `science/`. FormulaGraph never opens files.

## Domains

| Domain | Role |
|--------|------|
| `breed/` | Breeds, breed↔condition, traits↔condition, environment, activity, mixed-breed |
| `condition/` | Conditions, protocols, timelines, grooming |
| `ingredient/` | Ingredients, condition↔ingredient, mechanisms, evidence, aliases |
| `nutrition/` | Foods, nutrients, sources, priorities, life stages |
| `product/` | `PRODUCT_CATALOG`, `PRODUCT_COMPONENTS`, `PRODUCT_FUNCTIONS`, `PRODUCT_FEEDING_RULES`, `PRODUCT_PRICING`, `TREAT_BAKERY` |
| `physiology/` | Traits, trait science, benefits |
| `evidence/` | Papers, clinical evidence |
| `runtime/` | aliases, parameters, units |

Package tier discounts and product defaults are Repository policy constants (not CSVs).
