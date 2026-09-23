# Phase K — Professional Survey Contracts

## Purpose

Add the smallest contract envelope for structured **groomer** and **veterinarian** observation submissions.

This phase does not fuse evidence, project current state, rank observers, recommend products, or infer breed.

## Reused contracts

| Need | Reuse |
|------|--------|
| Individual observation | `Observation` |
| Presence / unknown | `InputState` + `FieldValue` (`PROVIDED`, `UNKNOWN`, `NOT_PROVIDED`, `NOT_APPLICABLE`) |
| Role | `ObserverRole.GROOMER`, `ObserverRole.VETERINARIAN` |
| Physical types | `PHYSICAL_OBSERVATION_TYPES` |
| Breed-trait rejection | `BREED_DERIVED_TRAIT_NAMES` |
| Persist | `record_physical_observation` → `ProfileEvent` / `events` |
| Errors | `DogStateError` / pydantic `ValidationError` |

No `ProfessionalPetProfile`, `GroomerProfile`, `VeterinarianProfile`, or second event log.

## New contracts

| Type | Role |
|------|------|
| `ProfessionalSurveyAnswer` | One survey answer: established `observation_type` + `FieldValue[str]` presence + optional `unit` / `observed_at` |
| `ProfessionalSurveyResponse` | Envelope: `dog_id`, professional `observer_role`, `answers[]`, optional `source_session_id` |

New persist adapter (not a new store):

| Function | Role |
|----------|------|
| `record_professional_survey` | Writes **PROVIDED** answers only via `record_physical_observation` |

## Allowed roles

`GROOMER` and `VETERINARIAN` only.

`CUSTOMER` and `SYSTEM` are rejected on this envelope. Owner observations remain Phase J `Observation` / event paths.

No hierarchy. Role is provenance only.

## Established observation types

Same Phase J allowlist:

`weight_kg`, `height_cm`, `bcs`, `activity_level`, `coat_density`, `skin_appearance`

Values remain free-text strings. No `SHORT`/`MEDIUM`/`LONG`, no BCS 1–9 validation, no diagnosis mapping.

Warehouse `TRAIT_NAMES` remain forbidden as `observation_type`.

## Unknown / not-assessed semantics actually implemented

| Intended meaning | Implemented as | Persisted? |
|------------------|----------------|------------|
| Observed | `InputState.PROVIDED` + value → `Observation` | Yes, via existing observation persist |
| Unknown / not known | `InputState.UNKNOWN`, no value | No (would require inventing an Observation value) |
| Not assessed | **Not a new enum.** Existing `InputState.NOT_PROVIDED`, no value | No |
| Not applicable | Existing `InputState.NOT_APPLICABLE` (already on `FieldValue`) | No |

`NOT_ASSESSED` is **not** added. Ω12 `UNRESOLVED` / `AMBIGUOUS` / `MIXED` are not used.

Empty string is not treated as UNKNOWN or NOT_PROVIDED. `FieldValue` already forbids a value on UNKNOWN / NOT_PROVIDED / NOT_APPLICABLE.

## Persistence path

```
ProfessionalSurveyResponse
    → observations()          # PROVIDED only
    → record_physical_observation()
    → ProfileEvent / events
```

`PersistentDog` scalars are not updated.

UNKNOWN / NOT_PROVIDED answers stay on the contract only. They are not written as observations.

## Temporal semantics

- `ProfessionalSurveyAnswer.observed_at` is when that answer was observed, if supplied.
- Non-PROVIDED answers must not carry `observed_at`.
- `recorded_at` is set by the existing store when a PROVIDED observation is written.
- Missing `observed_at` remains `None`. It is not copied from `timestamp`.

## API behavior

No new routes.

`POST /api/v1/dogs/{dog_id}/events` is unchanged.

Veterinarian HTTP source remains unsupported (Phase J / H allowlist). Veterinarian surveys persist at store level via `record_professional_survey`.

## Breed independence

A dog with `breed_input_state=UNKNOWN` and `primary_breed=None` can receive a professional survey. No breed is required or fabricated.

## Explicit non-goals

- No questionnaire UI / frontend
- No evidence fusion or current-state projection
- No conflict resolution or authority ranking
- No recommendation, nutrition, or product matching
- No Core / Ω12 / FormulaGraph / BreedNode / scientific_care changes
- No new physical-trait ontology
- No diagnosis ontology
- No second event log or survey table
- No veterinarian HTTP enablement
- No LLM extraction

## Remaining gaps

| Gap | Status |
|-----|--------|
| Dedicated `NOT_ASSESSED` enum member | NOT ESTABLISHED; `NOT_PROVIDED` is the stand-in |
| Persisting UNKNOWN / NOT_PROVIDED survey answers | NOT ESTABLISHED; Observation requires a value |
| HTTP veterinarian survey submission | Explicitly left disabled |
| Survey-level `recorded_at` distinct from per-observation store time | Not added; store `recorded_at` already exists on events |
| Groomer/vet questionnaire field catalogs beyond Phase J types | NOT ESTABLISHED |
| Current evidence profile / as-of projection | Later phase |

## Next gated phase

Phase L — Canonical Evidence Profile / Evidence Normalization.

Do not start Phase L from this document.
