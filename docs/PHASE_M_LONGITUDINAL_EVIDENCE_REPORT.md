# Phase M — Longitudinal Evidence Reporting & Temporal Comparison

## Purpose

Provide a **read-only InBody-style report** over Phase L evidence:

- complete longitudinal history
- provenance on every point
- Phase L canonical observation reused
- numeric change from the previous comparable point
- strict as-of / replay

This layer does not store evidence, diagnose, infer breed, or recommend products.

## Source of truth

`ProfileEvent` / `events` remain the source of truth.

Pipeline:

```
Observation
    → ProfileEvent / events
    → Phase L EvidenceRecord
    → Phase L EvidenceSeries / EvidenceProfile
    → Phase M EvidenceReport
```

No report table, history table, or second event log.

## Policy review (canonical)

Phase L policy is reused unchanged:

1. Source precedence: `SYSTEM` < `CUSTOMER` < `GROOMER` < `VETERINARIAN`
2. Known `observed_at` beats missing `observed_at`
3. Later `observed_at`
4. Later `recorded_at`
5. `event_id`

Canonical is **not** “latest measurement” and is **not** a scientific truth claim.

A newer owner value does not override an older veterinarian value.

Phase M does not introduce a second selector.

## Normalized report representation

In-memory only:

| Type | Role |
|------|------|
| `EvidenceRecord` | Reused Phase L observation + provenance |
| `EvidenceDelta` | Numeric comparison between two points |
| `EvidenceTimelinePoint` | Observation + optional `delta_from_previous` |
| `EvidenceReportSeries` | One type: history, canonical, timeline |
| `EvidenceReport` | `dog_id`, `generated_at`, `as_of`, `series` |

`EvidenceMeasurement` is **not** added. `EvidenceRecord` already holds the required fields.

`generated_at` is report-generation time. It is never copied into `observed_at` or `recorded_at`.

## Established observation types

Phase J allowlist only:

`weight_kg`, `height_cm`, `bcs`, `activity_level`, `coat_density`, `skin_appearance`

Breed-derived `TRAIT_NAMES` (`coat_type`, …) are excluded.

## Provenance

Every history and timeline point retains:

`observation_id`, `dog_id`, `observation_type`, `value`, `unit`, `observer_role`, `source`, `observed_at`, `recorded_at`, `source_session_id`, `event_id`

`observer_role` and `source` stay distinct (`customer` vs `USER`).

No confidence, accuracy, or evidence scores.

## As-of / replay

`build_evidence_report(dog_id, observation_type=None, as_of=None)`

If `as_of` is omitted: full Phase L history.

If `as_of` is supplied (strict replay):

| Row | Eligible? |
|-----|-----------|
| `observed_at` known and `<= as_of` | Yes |
| `observed_at` known and after `as_of` | No |
| `observed_at` missing | No |

Missing observation time is **not** known to have occurred before `as_of`.

`recorded_at` is never used as `observed_at`.

Canonical selection then runs on the filtered history only.

## Temporal ordering

Same as Phase L:

1. known `observed_at` ascending
2. missing `observed_at` after dated rows
3. `recorded_at` ascending
4. `event_id`

## Numeric deltas

Consecutive timeline points only. First point has `delta_from_previous = None`.

Numeric comparison is allowed only for types that already exist as numeric persist scalars:

`weight_kg`, `height_cm`, `bcs`

Not calculated for:

`coat_density`, `skin_appearance`, `activity_level`

No categorical ordering (`LOW` → `HIGH` is not a number).

Values must parse as finite numbers with no extra text (`"20 kg"` is not a number).

### Units

No conversion ontology (no kg ↔ lb).

If stored units differ after casefold: `delta_from_previous = None`.

If both units are absent, the type name supplies the established unit:

| Type | Implied unit when omitted |
|------|---------------------------|
| `weight_kg` | `kg` |
| `height_cm` | `cm` |
| `bcs` | none (dimensionless) |

Deltas follow **timeline order**. For undated rows (only present when `as_of` is omitted) that means report order, not a claimed observation-time sequence.

## Conflict behavior

All observations remain visible. No average, majority vote, or deletion.

Canonical may flag one representative. History still lists every event.

## PersistentDog separation

Report construction does not write `PersistentDog` scalars.

`current_projection()` remains latest-event-per-kind plus dog snapshot. It is not this report.

## UNKNOWN-breed behavior

`breed_input_state=UNKNOWN` and `primary_breed=None` still produce a full report. No `resolve_breed()`.

## Unknown / not-provided

Phase K `UNKNOWN` / `NOT_PROVIDED` / `NOT_APPLICABLE` answers that were never persisted do not appear.

No placeholder “unknown measurement” rows.

## InBody-style JSON

`evidence_report_payload(report)` → `EvidenceReport.model_dump(mode="json")`

Types with no observations after filtering are omitted.

## Explicit non-goals

No diagnosis, recommendation, nutrition, breed inference, evidence fusion, scores, UI, HTTP routes, Mongo, new tables, Ω12, or Core.

## Tests

`tests/state/test_phase_m_longitudinal_evidence.py`

`tests/architecture/test_phase_m_evidence_isolation.py`

## Remaining gaps

| Gap | Status |
|-----|--------|
| HTTP evidence report route | Phase N |
| First-to-last span delta as a first-class field | Consecutive deltas only |
| Unit conversion | Explicitly out of scope |
| Evidence fusion / interpretation | Later phase |
| Writing report values back to `PersistentDog` | Forbidden |

## Next gated phase

Only after review and explicit approval.

Do not start the next phase from this document.
