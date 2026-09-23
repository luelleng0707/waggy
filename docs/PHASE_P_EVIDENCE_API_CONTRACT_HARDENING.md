# Phase P — Evidence API Contract Hardening

## Purpose

Make the Phase N HTTP contract explicit without changing evidence policy.

The public response remains the Phase M `EvidenceReport` JSON from:

`GET /api/v1/dogs/{dog_id}/evidence-report`

## Serializer distinction

Two internal serializers previously shared the name `evidence_report_payload`.

| Function | Module | Shape | HTTP |
|----------|--------|-------|------|
| `evidence_profile_payload` | `app/state/evidence.py` | `{dog_id, physical_evidence}` | No |
| `evidence_report_payload` | `app/state/evidence_report.py` | `{dog_id, generated_at, as_of, series}` | Yes |

Only the Phase L name changed, from `evidence_report_payload` to `evidence_profile_payload`. The JSON for an `EvidenceProfile` is unchanged. The HTTP route still calls `app.state.evidence_report.evidence_report_payload`.

`app/api/evidence_report.py` still imports only `app.state.evidence_report`.

No FastAPI `response_model` was added. The route also returns the existing `DogStateError` JSON body, and a response model would reject that 404.

## generated_at

`generated_at` stays a public query parameter.

It is a report-generation stamp only. It is not written to `observed_at` or `recorded_at`. It is not an input to canonical selection or as-of filtering. Repeating the GET does not persist it.

## Unchanged semantics

- `as_of` and `observation_type` are still passed through to Phase M.
- Unestablished and breed-derived types stay HTTP 200 with `series: []`.
- Unknown dogs stay HTTP 404, `error.code = DOG_NOT_FOUND`, `error.field = dog_id`.
- Canonical selection, deltas, replay, storage, and PersistentDog behavior are unchanged.

## Files

Changed:

- `app/state/evidence.py` (serializer rename only)
- `tests/state/test_phase_l_canonical_evidence.py`
- `tests/architecture/test_phase_n_evidence_api_isolation.py`
- `docs/PHASE_L_CANONICAL_EVIDENCE_PROFILE.md`
- `docs/PHASE_N_EVIDENCE_REPORT_API.md`

Created:

- `tests/api/test_phase_p_evidence_contract.py`
- `tests/architecture/test_phase_p_serializer_isolation.py`
- `docs/PHASE_P_EVIDENCE_API_CONTRACT_HARDENING.md`

Persistence, Core, Ω12, and scientific logic: unchanged.

## Results

Focused:

```
py -3 -m pytest tests/api/test_phase_p_evidence_contract.py tests/architecture/test_phase_p_serializer_isolation.py tests/architecture/test_phase_n_evidence_api_isolation.py tests/state/test_phase_l_canonical_evidence.py -q --tb=line
```

20 passed, 1 warning in 7.95s

Verification:

```
py -3 -m pytest tests/api tests/architecture tests/state/test_phase_l_canonical_evidence.py tests/state/test_phase_m_longitudinal_evidence.py tests/state/test_phase_k_professional_survey.py tests/integration/test_phase_o_cross_phase_conformance.py -q --tb=short
```

206 passed, 1 warning in 1521.10s

Regression:

```
py -3 -m pytest tests/state tests/api tests/architecture tests/contracts tests/data/test_breed_node_baseline.py tests/data/test_breed_knowledge_contract.py -q --tb=line
```

298 passed, 1 warning in 467.51s

The warning is the existing pydantic `schema` field warning on `WorkbenchPresentationResponse`.

## Remaining gaps

- `generated_at` is still caller-supplied. It is documented as a stamp, not validated as a timestamp.
- Malformed `as_of` is still passed through to Phase M.
- The generic event route still accepts types outside the physical allowlist. The report still omits them.

## Next gated phase

Only after review and explicit approval.
