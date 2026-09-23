# Phase O — Cross-Phase Evidence Conformance

## Purpose

Prove that the existing J → K → L → M → N evidence pipeline stays consistent across phase boundaries.

This phase adds tests only. It does not change selection, replay, deltas, persistence, or the HTTP contract.

## Path verified

```
Phase J / K write
    record_physical_observation
    record_professional_survey
        → ProfileEvent / events
Phase L
    get_evidence_history
    select_canonical_observation
    get_canonical_observation
Phase M
    build_evidence_report
Phase N
    GET /api/v1/dogs/{dog_id}/evidence-report
```

`EvidenceProfile` is not on the HTTP path. The report uses Phase L history and the same selector.

## Test scope

`tests/integration/test_phase_o_cross_phase_conformance.py`

| Test | What it proves |
|------|----------------|
| Professional survey → N | A `PROVIDED` veterinarian `weight_kg` appears. `UNKNOWN`, `NOT_PROVIDED`, and `NOT_APPLICABLE` answers do not become rows. |
| Canonical precedence | Older veterinarian `22` stays canonical beside newer customer `23`. The HTTP canonical `event_id` matches `get_canonical_observation()`. Both rows stay in history. |
| Incompatible units | `20 kg` and `44 lb` both remain. The consecutive delta is `None`. |
| Categorical deltas | `activity_level` and `skin_appearance` consecutive deltas are `None`. |
| Omitted units | Absent stored units stay absent. Comparison delta is `1.0` kg, `2.0` cm, and `1.0` for dimensionless `bcs`. |
| Generic event | `POST /api/v1/dogs/{dog_id}/events` can store `coat_length`. That type is absent from the report. |
| As-of canonical | `as_of=2026-09-01` keeps the earlier customer row, drops the later veterinarian row and the undated groomer row, and selects canonical from that filtered history. `get_canonical_observation()` remains the unfiltered veterinarian row. |
| Provenance | Report rows keep `observation_id`, `dog_id`, `observation_type`, `value`, `unit`, `observer_role`, `source`, `observed_at`, `recorded_at`, `source_session_id`, and `event_id`. Customer is `customer` / `USER`. Veterinarian is `veterinarian` / `VETERINARIAN`. `observed_at` is not `recorded_at`. |
| Read-only | Two GETs leave event ids and `PersistentDog` `weight_kg`, `height_cm`, `bcs`, and `activity_level` unchanged. |
| Unknown / breed-derived query | `coat_type` and `not_a_physical_observation` return HTTP 200 and `series: []`. |

## Existing state-layer coverage, not newly added here

Phase L and Phase M tests already cover source precedence, unit mismatch, `coat_density` deltas, missing `observed_at`, and as-of filtering in the state layer. Phase O adds the HTTP and survey-to-HTTP crossings above. `coat_density` itself is not retested in Phase O.

## Explicit non-goals

No canonical-policy change, no `as_of` added to `get_canonical_observation()`, no unit conversion, no fusion, no scores, no diagnosis, no recommendations, no new tables, no PersistentDog writes, no HTTP contract change, no frontend, no rename of the two `evidence_report_payload` functions, and no change to `generated_at` or the generic event route.

## Files

Created:

- `tests/integration/test_phase_o_cross_phase_conformance.py`
- `docs/PHASE_O_CROSS_PHASE_EVIDENCE_CONFORMANCE.md`

Production files changed: none.

Persistence / schema changes: none.

## Architectural isolation

Unchanged. `app/api/evidence_report.py` still imports only `app.state.evidence_report`.

Existing Phase M and Phase N isolation tests were re-run and passed. Phase O did not add production imports of Ω12, FormulaGraph, Core nodes, normalization, `scientific_care`, package search, package optimizer, or formulas.

## Results

Phase O:

```
py -3 -m pytest tests/integration/test_phase_o_cross_phase_conformance.py -q --tb=short
```

9 passed, 1 warning in 18.72s

Focused:

```
py -3 -m pytest tests/api/test_phase_n_evidence_report.py tests/architecture/test_phase_n_evidence_api_isolation.py tests/architecture/test_phase_m_evidence_isolation.py tests/state/test_phase_m_longitudinal_evidence.py tests/state/test_phase_l_canonical_evidence.py -q --tb=short
```

35 passed, 1 warning in 9.71s

Regression:

```
py -3 -m pytest tests/state tests/api tests/architecture tests/contracts tests/data/test_breed_node_baseline.py tests/data/test_breed_knowledge_contract.py -q --tb=line
```

294 passed, 1 warning in 1136.45s

That regression command does not include `tests/integration`. Phase O was run as its own command. The warning is the existing pydantic `schema` field warning on `WorkbenchPresentationResponse`.

## Remaining gaps

- The two `evidence_report_payload` functions still return different JSON shapes. Not renamed here.
- `generated_at` remains a public query parameter. Not changed here.
- The generic event route still accepts types outside the physical allowlist. The report continues to omit them.
- Veterinarian writes through `POST /api/v1/dogs/{dog_id}/events` remain unsupported. Survey and `record_physical_observation` remain the veterinarian write path.
- `confirmation_status`, `confidence`, and event `timestamp` are still not evidence-report fields. Not covered by a new Phase O assertion beyond the established provenance list.

## Next gated phase

Phase P — Evidence API Contract Hardening, only after review and explicit approval.

Do not start Phase P from this document.
