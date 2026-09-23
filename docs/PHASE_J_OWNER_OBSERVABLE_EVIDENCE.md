# Phase J — Owner-Observable Physical Trait Evidence

## Purpose

Establish the smallest reusable infrastructure for **individual-pet physical observations**, separate from **breed-derived warehouse traits**.

This phase does not recommend food, calculate nutrition, infer breed, or project a current physical profile.

## Reused contracts

| Need | Reuse | File |
|------|--------|------|
| Individual observation | `Observation` | `app/contracts/agent/observations.py` |
| Observer role | `ObserverRole` (`customer` / `groomer` / `veterinarian` / `system`) | `app/contracts/agent/enums.py` |
| Durable log | `ProfileEvent` + `events` table | `app/ai/models.py`, `app/state/db.py` |
| Persist write | `record_event` | `app/state/store.py` |
| Time | `observed_at`, `recorded_at` (Phase H) | Observation + ProfileEvent |
| Errors | `DogStateError` / `INVALID_EVENT_PAYLOAD` | `app/state/errors.py` |
| Unknown breed | `PersistentDog.breed_input_state` | Phase H/I |
| HTTP events | `POST /api/v1/dogs/{dog_id}/events` | existing |

No `ObservedTrait`, `ProfessionalObservation`, `PetEvidenceProfile`, or second event log.

## New code

| File | Role |
|------|------|
| `app/contracts/agent/observations.py` | Allowlist `PHYSICAL_OBSERVATION_TYPES`; copy of warehouse `TRAIT_NAMES` as `BREED_DERIVED_TRAIT_NAMES`; `Observation.to_event_payload()` |
| `app/state/observations.py` | `record_physical_observation`, `observation_from_event`, `physical_observations_for` |
| `app/state/store.py` | Reject payload `observation_type` that is a breed-derived trait name |
| `app/state/models.py` / `app/api/main.py` | Optional `DogEventRequest.observed_at` passed through to `record_event` |

## Observation semantics

An individual physical observation is one `Observation`:

- one pet (`dog_id`)
- one `observer_role`
- one `observation_type`
- one string `value`
- optional `unit`
- optional `observed_at`
- `recorded_at` set only when persisted

Values remain caller-supplied strings. This phase does **not** introduce `SHORT` / `MEDIUM` / `LONG`, `LEAN` / `MUSCULAR`, or other invented categorical enums.

### Established physical `observation_type` values

Only types already present as persist scalars or existing Observation examples:

| Type | Grounding |
|------|-----------|
| `weight_kg` | `PersistentDog` / Phase H observations / unit `kg` in tests |
| `height_cm` | `PersistentDog` / `DogProfileInput` |
| `bcs` | `PersistentDog` / `DogProfileInput` (UI range 0–9 is CSTC only; not enforced here) |
| `activity_level` | `PersistentDog` / `DogProfileInput` |
| `coat_density` | Ω11 Observation examples (`"dense coat"` is free text) |
| `skin_appearance` | Phase H groomer observation |

Unestablished prompt examples (`coat_length`, `undercoat_present`, `body_build`, muzzle/ear/head categories, skin oiliness, etc.) are **rejected** by `record_physical_observation` and listed as gaps.

### Breed-derived names (not observations)

Warehouse `TRAIT_NAMES` / `BreedTraitFact`:

`size`, `body_type`, `coat_type`, `energy`, `skull_type`, `climate`, `lifespan`, `weakness_group`, `function_group`

Recording any of these as `observation_type` raises `INVALID_EVENT_PAYLOAD`. They remain population knowledge, not individual evidence.

## Provenance

`record_physical_observation` writes one `ProfileEvent` with:

| Field | Source |
|-------|--------|
| `dog_id` | Observation |
| `source` | `CUSTOMER→USER`, `GROOMER→GROOMER`, `VETERINARIAN→VETERINARIAN`, `SYSTEM→SYSTEM` |
| `event_type` | existing mapping (`USER_STATEMENT`, `GROOMER_OBSERVATION`, `VETERINARIAN_OBSERVATION`) |
| `payload.observation_type` | Observation |
| `payload.observer_role` | Observation |
| `payload.unit` | Observation, if supplied |
| `value` | Observation value |
| `observed_at` | caller-supplied or `None` |
| `recorded_at` | store clock at insert |
| `event_id` | generated; used as reconstructed `observation_id` |

`observation_from_event` rebuilds `Observation` from that row. Existing event `model_dump` / SQLite load continues to carry payload + timestamps.

## Temporal semantics

- `observed_at`: when the fact was observed. Not fabricated.
- `recorded_at`: when Waggy stored the event.
- `timestamp` / `created_at`: legacy store stamps; not treated as `observed_at`.

`current_projection()` is unchanged. It is still latest-event-per-kind plus the dog snapshot, not an as-of physical-trait projection. That remains a later policy phase.

## Owner / groomer / veterinarian

All three roles use the same `Observation` class.

| Role | Persist source | Event type | HTTP `POST /events` |
|------|----------------|------------|---------------------|
| CUSTOMER | `USER` | `USER_STATEMENT` | allowed |
| GROOMER | `GROOMER` | `GROOMER_OBSERVATION` | allowed |
| VETERINARIAN | `VETERINARIAN` | `VETERINARIAN_OBSERVATION` | still store-level only (Phase H allowlist unchanged) |

No authority ranking. Customer and groomer `coat_density` rows both remain.

## UNKNOWN breed compatibility

A dog created with `breed_input_state=UNKNOWN` and `primary_breed=None` can receive physical observations. No breed is invented. Breed-dependent Core analysis remains fail-closed (Phase I).

## Breed-derived vs individually observed

```
BreedTraitFact / TRAIT_NAMES     population knowledge on a breed row
        ≠
Observation                      one observer, one type, one value, one time
        ≠
PersistentDog scalars            cache updated only by authorized PROFILE_UPDATE
```

Example that must stay separate:

- Breed knowledge: German Shepherd → warehouse `coat_type` = Double Coat
- Individual: groomer Observation `coat_density` = dense

## Conflict behavior

No averaging, majority vote, latest-wins, or role ranking.

Customer `weight_kg=20` and groomer `weight_kg=22` both remain in `events` / `physical_observations_for`.

## Persistence behavior

- Same `events` table. No second log.
- `record_physical_observation` does not mutate `PersistentDog.weight_kg`, `height_cm`, `bcs`, or `activity_level`.
- Existing `_apply_event_to_current` rules are unchanged: unconfirmed `USER_STATEMENT` still does not overwrite weight; `GROOMER_OBSERVATION` still only appends `payload.observed_condition` tokens.

## API behavior

No new routes.

Additive only: `DogEventRequest.observed_at` is optional and forwarded to `record_event`.

Owner/groomer physical observations can be posted as:

```json
{
  "event_type": "USER_STATEMENT",
  "source": "USER",
  "value": "32",
  "observed_at": "2026-09-19T12:00:00+00:00",
  "payload": {
    "observation_type": "weight_kg",
    "unit": "kg",
    "observer_role": "customer"
  }
}
```

`observation_type: "coat_type"` (a warehouse trait name) is rejected.

Veterinarian HTTP source remains unsupported; store `record_physical_observation` supports `ObserverRole.VETERINARIAN`.

## Explicit non-goals

- No questionnaire / groomer UI / vet UI
- No coat_length / body_build / muzzle ontology
- No derived interpretation (“needs shedding management”)
- No as-of current-state replay
- No conflict resolution
- No Core / Ω12 / FormulaGraph / BreedNode / scientific_care changes
- No papers, AAFCO/FEDIAF, nutrition, packages, or product matching
- No LLM classification
- No Mongo
- No second evidence API (`POST /physical-traits`, etc.)

## Remaining gaps

| Gap | Status |
|-----|--------|
| `coat_length`, `undercoat_present`, `coat_texture`, `shedding_level` | NOT ESTABLISHED IN CURRENT REPOSITORY |
| `body_build`, `body_length_cm`, `chest_depth`, chest/body proportion categories | NOT ESTABLISHED |
| `muzzle_length_category`, `ear_shape`, `ear_carriage`, `head_shape`, `leg_length_category` | NOT ESTABLISHED |
| Skin tokens beyond existing `skin_appearance` free text | NOT ESTABLISHED |
| Constrained categorical enums (`SHORT`/`MEDIUM`/`LONG`, BCS 1–9 validation) | NOT ESTABLISHED as observation vocabulary |
| `body_condition_score` as a name | Existing field is `bcs`, not this alias |
| HTTP `VETERINARIAN` event source | Still allowlisted off (Phase H) |
| `current_projection()` including physical observations | Would require a later projection policy |
| Multi-species `species` field | Not added; `Observation` / events are not dog-named types |
| Joining breed-derived traits with individual observations | Later evidence-fusion phase |

## Next gated phase

Phase K — professional survey **contracts** only (groomer/veterinarian questionnaire fields), still without Core migration, authority ranking, or recommendation logic.

Do not start Phase K from this document.
