# MIXED_BREED_MODEL

## CURRENT IMPLEMENTATION

- Multiple runtime paths still collapse mixed-breed behavior toward `profile.breeds[0]`.
- Mixed-breed interactions exist in datasets, but not all stages execute explicit weighted blend logic.
- Evidence overlap between breed A and breed B is not consistently represented as weighted contributions in production outputs.

Current status: PARTIAL.

## PROPOSED FUTURE MODEL (not implemented in this phase)

Target contribution model:

`breed_A_contribution + breed_B_contribution + phenotype_contribution + environment_contribution`

with explicit normalized weights:

- `w_breed_A`
- `w_breed_B`
- `w_phenotype`
- `w_environment`

and traceable intermediate values per condition.

## Requirements before implementation

- Canonical mixed-breed contract across app and repository layers
- Explicit formula provenance and coefficient governance
- Validation datasets for mixed-breed calibration
- Debug trace support for contribution breakdown
