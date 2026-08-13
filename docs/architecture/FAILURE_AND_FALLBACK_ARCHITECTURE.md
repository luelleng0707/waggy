# FAILURE_AND_FALLBACK_ARCHITECTURE

Explicit failure behavior in current architecture.

| Scenario | Current behavior | Status/marker |
|---|---|---|
| Missing breed | validation/profile mapping may fail or produce sparse downstream outputs | 400 or partial runtime output |
| Mixed breed | current logic emphasizes `profile.breeds[0]` in several paths | PARTIAL (documented limitation) |
| Missing evidence | output fields remain sparse; no synthetic citations | `EVIDENCE INCOMPLETE` / unavailable states |
| Missing formula metadata | developer trace keeps explicit documentation status fields | `NOT DOCUMENTED` |
| Missing warehouse row | validation and debugger report unavailable row status | `NOT AVAILABLE` / blocker surfaced |
| Invalid product reference | candidate/product details omitted or filtered | graceful partial output |
| Conflicting ingredients | package scoring applies penalties/constraint filters | lower harmony / rejection |
| Calorie overflow | constraint logic penalizes or filters package candidates | penalty/constraint effect |
| Insufficient evidence | confidence/priority-like fields remain derived but limited | partial confidence semantics |
| Unavailable trace | customer/business unaffected; developer trace may be empty unless debug enabled | `NOT AVAILABLE` |
| Unavailable replay | debug output marks replay not available/implemented | `NOT IMPLEMENTED` or unavailable state |
| Invalid financial input | package/plan financial fields may be absent | `NOT AVAILABLE` |
| API internal failure | FastAPI returns 500 with logged exception | explicit error response |

## Global rule

- No silent substitution of synthetic scientific values.
- Missing data is explicitly carried as unavailable rather than fabricated.
