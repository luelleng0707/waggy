# DOSE_TARGET

## Formula identity
- IDs: `DOS-301`, `DOS-302`, `ING-506`
- Modules: `repository/mechanisms/runtime.py`, `repository/sources/runtime.py`

## Purpose
Converts dose-response baselines into ingredient targets scaled by mechanism demand and profile factors.

## Equations
- `DOS-301`: `BaselineAmount = DosePerKg * WeightKg` (for per-kg units)
- `DOS-302`: `TargetAmount = BaselineAmount * MechanismScalar * ContextScalar`
- `ING-506`: `IngredientTarget = sum(MechanismImportance * EffectSizePercent)`

## Parameter provenance
- Baseline doses from `warehouse/mechanisms/dose_response.csv`
- Effect sizes from `warehouse/mechanisms/ingredient_mechanisms.csv`

## ILLUSTRATIVE MATHEMATICAL EXAMPLE
- Dose `60 mg/kg/day`, weight `24 kg` -> baseline `1440 mg/day`
- Mechanism scalar `1.22`, context scalar `1.05`
- Target `1844.64 mg/day`
