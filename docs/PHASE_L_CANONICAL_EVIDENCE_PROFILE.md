# Phase L — Canonical Evidence Profile / Evidence Normalization

## Purpose

Provide a **read/derivation** layer over existing individual physical observations so they can be used as a coherent evidence profile.

This layer does not store evidence, interpret health, infer breed, or recommend products.

## Source of truth

`ProfileEvent` rows in the existing `events` table remain the source of truth.

`Observation` remains the semantic contract for a single observation.

Phase L reconstructs, orders, and selects. It does not replace persistence.

## Normalized evidence representation

In-memory read contracts (not tables):

| Type | Role |
|------|------|
| `EvidenceRecord` | One observation with provenance |
| `EvidenceSeries` | Full history + optional canonical row for one type |
| `EvidenceProfile` | All series that have evidence for one `dog_id` |

`EvidenceRecord` retains:

`observation_id`, `dog_id`, `observation_type`, `value`, `unit`, `observer_role`, `source`, `observed_at`, `recorded_at`, `source_session_id`, `event_id`

`observer_role` and `source` are both kept (`customer` vs `USER`, etc.). They are not collapsed.

## Established observation types

Phase J allowlist only:

`weight_kg`, `height_cm`, `bcs`, `activity_level`, `coat_density`, `skin_appearance`

Requests for warehouse `TRAIT_NAMES` (`coat_type`, …) return empty history and no canonical row.

## Provenance

Every history point and every canonical row can answer:

- what the value is
- who supplied it (`observer_role` + `source`)
- when it was observed (`observed_at`, or `None`)
- when Waggy stored it (`recorded_at`)
- which event produced it (`event_id`)

No confidence, authority, or evidence scores are generated.

## observed_at vs recorded_at

| Field | Meaning |
|-------|---------|
| `observed_at` | When the fact was observed. `None` if unknown. |
| `recorded_at` | When Waggy stored the event. |

Legacy `timestamp` / `created_at` are not used as `observed_at`. `recorded_at` is never copied into `observed_at`.

## Longitudinal history

`get_evidence_history(dog_id, observation_type=None)` returns every matching physical observation.

Ordering:

1. Rows with known `observed_at`, chronological ascending
2. Rows with missing `observed_at` after dated rows
3. Tie-break: `recorded_at` ascending (missing last), then `event_id`

Same-day rows remain distinct. No dedupe by date.

## Canonical / current selection

Canonical means: **the observation selected by a deterministic read policy when one representative is needed.** History is still the complete record.

`get_canonical_observation(dog_id, observation_type)` does not mutate events or `PersistentDog`.

## Source precedence

Read-policy order only:

`SYSTEM` < `CUSTOMER` < `GROOMER` < `VETERINARIAN`

This is not a stored rank, not a probability, and not a diagnostic score.

## Temporal policy

Recency is separate from source precedence.

Lexicographic **max** for canonical selection:

1. Higher source precedence
2. Known `observed_at` beats missing `observed_at` (without fabricating a date)
3. Later `observed_at`
4. Later `recorded_at` (missing last)
5. `event_id`

Therefore:

- Newer owner `23 kg` does **not** override older veterinarian `22 kg`
- Newer veterinarian `23 kg` **does** override older veterinarian `22 kg`

## Missing timestamps

Missing `observed_at` stays `None`.

A dated groomer row does not donate its date to an undated owner row.

Undated rows still participate in history. For canonical selection they lose the recency comparison to dated rows of the **same** role; they can still win on higher source precedence.

## Conflict behavior

Conflicts are not resolved in storage.

Customer 20 / groomer 21 / veterinarian 22 all remain in history. Canonical may be 22. Nothing is deleted.

No averaging. No majority vote.

## PersistentDog separation

`PersistentDog.weight_kg` (and other scalars) are an unrelated snapshot/cache.

Phase L does not write them.

`current_projection()` is unchanged (latest-event-per-kind plus dog snapshot). It is not this policy.

## UNKNOWN-breed behavior

Dogs with `breed_input_state=UNKNOWN` and `primary_breed=None` get the same history and canonical selection. No `resolve_breed()` call.

## Unknown / not-provided semantics

Phase K `UNKNOWN` / `NOT_PROVIDED` / `NOT_APPLICABLE` answers that were never persisted do not appear here.

Ω12 `UNRESOLVED` / `AMBIGUOUS` / `MIXED` are not used.

## Breed-derived trait separation

`BreedTraitFact` / `coat_type` is not merged into `coat_density` history.

## InBody-style report contract

`build_evidence_profile(dog_id)` → `EvidenceProfile`

`evidence_profile_payload(profile)` → JSON-ready:

```json
{
  "dog_id": "...",
  "physical_evidence": [
    {
      "observation_type": "weight_kg",
      "canonical": { "value": "22", "observer_role": "veterinarian", "event_id": "...", "observed_at": "...", "recorded_at": "..." },
      "history": [ { "...provenance..." } ]
    }
  ]
}
```

Types with no observations are omitted. No empty invented rows. No chart UI.

## Explicit non-goals

No recommendation, nutrition, diagnosis, breed inference, evidence fusion, scores, new ontology, UI, Mongo, new tables, HTTP evidence API, veterinarian HTTP enablement, Ω12, or Core.

## Tests

`tests/state/test_phase_l_canonical_evidence.py`

`tests/architecture/test_phase_l_evidence_isolation.py`

## Remaining gaps

| Gap | Status |
|-----|--------|
| As-of / replay (`observed_at ≤ as_of`) | NOT IMPLEMENTED |
| HTTP evidence report route | Not added |
| Numeric conversion / `weight_delta` | Not added |
| Fusion with breed knowledge | Later phase |
| Writing canonical values back to `PersistentDog` | Explicitly forbidden here |

## Next gated phase

Phase M — only after review and explicit approval.

Do not start Phase M from this document.
