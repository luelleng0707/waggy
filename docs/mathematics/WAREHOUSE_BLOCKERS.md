# WAREHOUSE_BLOCKERS

These blockers come from `scripts/validate_warehouse.py` current failures and are not modified in Omega 9.5.

| dataset | row | foreign_key | referenced_id | expected_dataset | problem | recommended_correction |
|---|---|---|---|---|---|---|
| mechanisms.condition_mechanisms | line 2 | condition_id | COND_HIP_DYSPLASIA | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs (e.g., Hip Dysplasia canonical condition_id) or add controlled alias mapping table. |
| mechanisms.condition_mechanisms | line 6 | condition_id | COND_ATOPIC_DERMATITIS | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs or add explicit alias normalization in warehouse curation. |
| mechanisms.condition_mechanisms | line 9 | condition_id | COND_OBESITY | biology.conditions.condition_id | Legacy condition_id not present in canonical conditions IDs. | Map legacy condition IDs to canonical IDs or re-key rows using canonical IDs. |
| mechanisms.food_mechanisms | line 2 | ingredient_id | ING_EPA | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 3 | ingredient_id | ING_DHA | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 4 | ingredient_id | ING_COLLAGEN | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 5 | ingredient_id | ING_VITAMIN_C | nutrition.ingredients.ingredient_id | Ingredient ID missing from canonical ingredient IDs. | Add canonical ingredient row or map legacy nutrient IDs to canonical ingredient IDs. |
| mechanisms.food_mechanisms | line 6 | ingredient_id | ING_ZINC | nutrition.ingredients.ingredient_id | Ingredient ID namespace mismatch (`ING_ZINC` vs canonical `ING_723DBC80`). | Introduce deterministic ID mapping or re-key to canonical ingredient IDs in curation migration. |

## Blocker status
- VALIDATION_STATUS: FAIL
- ERROR_COUNT: 8
- RESOLUTION_POLICY: separate controlled warehouse correction task (not performed in Omega 9.5)
