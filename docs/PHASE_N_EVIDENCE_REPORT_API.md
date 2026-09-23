# Phase N — Evidence Reporting Read API / Presentation Boundary

## Purpose

Expose the existing Phase M longitudinal evidence report through a read-only HTTP boundary.

The route does not rebuild evidence, select a canonical observation, or calculate deltas. Those stay in Phase L and Phase M.

## Endpoint

`GET /api/v1/dogs/{dog_id}/evidence-report`

Established dog routes already use the `/api/v1/dogs/{dog_id}/...` prefix. This route follows that prefix.

Query parameters, all optional, are passed through to `build_evidence_report()`:

| Parameter | Role |
|-----------|------|
| `observation_type` | Phase L filter. No second allowlist in the API. |
| `as_of` | Phase M strict replay cutoff. |
| `generated_at` | Report-generation stamp only. Not an observation time, not a canonical input, and not an as-of cutoff. |

Response is `app.state.evidence_report.evidence_report_payload(report)`: the Phase M `EvidenceReport` JSON. That function is not `app.state.evidence.evidence_profile_payload`, which serializes an `EvidenceProfile`.

```json
{
  "dog_id": "...",
  "generated_at": "...",
  "as_of": null,
  "series": [
    {
      "observation_type": "weight_kg",
      "units": ["kg"],
      "history": [],
      "canonical_observation": {},
      "timeline": [
        { "observation": {}, "delta_from_previous": null }
      ]
    }
  ]
}
```

## Canonical semantics

Canonical means the representative observation selected by the Phase L read policy. The API does not change that policy.

Order remains source precedence (`SYSTEM` < `CUSTOMER` < `GROOMER` < `VETERINARIAN`), then known `observed_at`, later `observed_at`, later `recorded_at`, then `event_id`.

This is not a diagnosis, a confidence score, or a claim that the value is medically correct.

## Temporal semantics

`as_of` is forwarded unchanged.

Phase M includes a dated row only when `observed_at <= as_of`. Later dated rows are excluded. Rows with missing `observed_at` are excluded. `recorded_at` is not used as `observed_at`.

The API does not parse or repair timestamps.

## Provenance

Every history and timeline observation keeps `observation_id`, `dog_id`, `observation_type`, `value`, `unit`, `observer_role`, `source`, `observed_at`, `recorded_at`, `source_session_id`, and `event_id`.

`observer_role` and `source` stay separate.

## Read-only behavior

The handler calls `read_evidence_report()` and returns the payload.

It does not insert, update, or delete events, and it does not write `PersistentDog`.

Repeating the GET does not change stored evidence.

## Error behavior

Unknown `dog_id` uses the existing state error: HTTP 404, body `error.code = DOG_NOT_FOUND`, `error.field = dog_id`. That comes from `require_dog()` inside Phase L, surfaced with the same `DogStateError` JSON used by other dog routes.

An unestablished or breed-derived `observation_type` is not a new API error. Phase L returns no rows, so the response is HTTP 200 with `series: []`.

A malformed `as_of` is not validated here. It is passed to Phase M.

A missing path `dog_id` is a normal FastAPI routing miss.

## Architectural boundary

`app/api/evidence_report.py` imports only `app.state.evidence_report`.

`app/api/main.py` registers the route and maps `DogStateError` to the existing JSON error response.

The adapter does not import Ω12, Core graph nodes, `scientific_care`, package search, package optimizer, or formulas. It does not call `resolve_breed()`.

## Explicit non-goals

No UI, charts, diagnosis, product or nutrition advice, breed inference, unit conversion, trend scores, averages, new tables, or writes.

## Tests

`tests/api/test_phase_n_evidence_report.py`

`tests/architecture/test_phase_n_evidence_api_isolation.py`

## Remaining gaps

| Gap | Status |
|-----|--------|
| Frontend rendering of the report | Not in this phase |
| Unit conversion | Still out of scope |
| Evidence fusion / clinical interpretation | Later phase |

## Next gated phase

Only after review and explicit approval.
