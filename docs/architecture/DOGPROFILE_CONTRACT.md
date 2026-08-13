# DOGPROFILE_CONTRACT

## CURRENT CONTRACTS
- App contract: `app/agent/state.py::DogProfileInput` (Pydantic API DTO with validation constraints).
- Repository contract: `repository/models/runtime.py::DogProfile` (immutable domain dataclass).
- Adapter-like mapping lives in `app/api/payload_adapter.py::profile_from_analyze_body`.

## CANONICAL PROPOSED CONTRACT
- Canonical domain owner: `repository/models/runtime.py::DogProfile`.
- App `DogProfileInput` remains transport/input DTO at API boundary.

## FIELD MAPPING
- `name` -> `name`
- `primary_breed` + `secondary_breed` -> `breeds` tuple
- `birthday` -> `date_of_birth`
- `weight_kg` -> `weight_kg`
- `current_environment` -> `environment`
- `observed_conditions` -> `observed_conditions`

## LOSSY CONVERSIONS
- `breed_split_pct` currently has no native field in repository `DogProfile`.
- `gender/sex` and `height_cm/bcs` are not represented in repository `DogProfile`.
- `current_environment` is a flattened string; city/country/climate/urbanicity may require later resolver enrichment.

## ADAPTER REQUIREMENTS
- Required adapter boundary: API DTO -> domain model with explicit mapping + loss accounting.
- Adapter must preserve mixed-breed ordering and observed conditions deterministically.

## MIGRATION RISKS
- Mixed-breed semantics drift if `breed_split_pct` is dropped without compensation.
- Validation behavior drift between Pydantic constraints and dataclass defaults.

## TEST REQUIREMENTS
- Validate app DTO constraints and deterministic field mapping to canonical domain model.
- Require explicit assertion of lossy fields during conversion.
