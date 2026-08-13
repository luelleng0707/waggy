# DATA_PIPELINE.md

Conceptual data flow — no implementation detail.

```
Input: Dog profile
        ↓
Validation
        ↓
Standardization (names, life stage, environment)
        ↓
Entity Resolution (breed → traits; aliases)
        ↓
Relationship Retrieval (breed↔condition, trait↔condition, ingredient links)
        ↓
Formula Calculation (prevalence, interactions, benefits)
        ↓
Risk Aggregation
        ↓
Nutrition targets
        ↓
Product Selection
        ↓
Package Selection
        ↓
Assessment Objects
        ↓
Serializer
        ↓
Frontend JSON
```

## Data ownership

| Concern | Where it lives |
|---------|----------------|
| What a breed/condition/ingredient **is** | `warehouse/reference/` |
| How entities **relate** (evidence, prevalence) | `warehouse/science/` |
| Runtime knobs (aliases, parameters, units) | `warehouse/runtime/` |
| How formulas **see** joined tables | Repository in-memory views |
| How numbers are **computed** | FormulaGraph / stages |

## Rule

Science changes happen in the warehouse (and pass validation).  
Engine changes happen in formulas (and pass parity tests).  
Never mix the two in the same edit without an explicit version bump.
