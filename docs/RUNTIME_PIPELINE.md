# RUNTIME_PIPELINE.md

End-to-end execution path for a clinical assessment.

```
User Input (DogProfile)
        ↓
Validation (Pydantic / API schema)
        ↓
Normalization (aliases, units, breed names)
        ↓
Breed Resolution (Repository)
        ↓
Scientific Repository (entities + relationships + in-memory views)
        ↓
FormulaGraph (ordered FormulaNodes)
        ↓
AssessmentResult
        ↓
Serializer (analyze / clinical-report JSON)
        ↓
API Response
        ↓
Frontend (demo UI or Wagtopia client)
```

## FormulaGraph order (conceptual)

1. Profile  
2. Breed / Biology  
3. Risk  
4. Epidemiology  
5. Activity  
6. Nutrition  
7. Ingredient  
8. Product  
9. Package  
10. Assessment / Report / Validation / Trace  
11. Export (legacy JSON shape)

## Invariants

- One warehouse root (`resolve_clinical_root()` → `warehouse/`).
- One repository layer for retrieval.
- No disk formula projections (`_formula_ops` removed).
- Deterministic outputs for the same profile + warehouse hash.
