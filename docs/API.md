# API

HTTP contracts for PPIE. Preferred integration path first; legacy endpoints listed for migration.

---

## Preferred contract

```text
POST /api/v1/ppie/assess
Header: x-api-key
Body:   DogProfile-compatible JSON
Out:    ClinicalAssessment
Optional query: ?module=<id>  → single module + meta
```

Wagtopia and partners should consume **ClinicalAssessment modules**, not prose blobs or mega-report HTML.

PPIE does **not** persist dogs. Persist DogProfile in Wagtopia; re-call assess for live care.

---

## Authentication

| Item | Value |
|------|--------|
| Header | `x-api-key` |
| Default demo key | `wagtopia-demo-key` |
| Config | `API_KEYS` (comma-separated) |

Replace demo keys before any public deployment. Some routes historically omit the key check (`/health`, static assets, certain groomer/breeds helpers) — do not assume every path is locked.

---

## Version headers

Responses may include:

| Header | Meaning |
|--------|---------|
| `X-PPIE-Algorithm-Version` | Formula / ranking version |
| `X-PPIE-Data-Version` | Manifest data version |
| `X-PPIE-Content-Hash` | CSV content hash |
| `X-PPIE-Elapsed-Ms` | Request timing |

Three axes — algorithm, data, presentation — must not be conflated. See [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md).

---

## DogProfile (input)

Required in practice: primary breed; birthday **or** age; `weight_kg` for feeding/costing.

Stable shape (nested or flat adapters both accepted via payload adapter):

```json
{
  "identity": { "external_id": "…", "display_name": "Dolly" },
  "breed": {
    "primary": "Golden Retriever",
    "secondary": "Labrador Retriever",
    "split_pct": { "primary": 50, "secondary": 50 }
  },
  "demographics": {
    "birthday": "2021-03-15",
    "sex": "female",
    "weight_kg": 30.0,
    "body_condition_score": 5
  },
  "lifestyle": {
    "activity_level": "high",
    "environment": "Shanghai Summer"
  },
  "clinical": { "known_conditions": [] },
  "goals": { "owner_goals": [] }
}
```

Demo bodies often use flat fields (`name`, `breeds[]`, `birthday`, `weight`, `activity_level`, `current_environment`) — the adapter normalizes these.

| Field | Rules |
|-------|--------|
| `breed.primary` | Required; alias-normalized |
| `breed.secondary` | Optional mixed-breed |
| `split_pct` | Optional; default 50/50 when secondary present |
| birthday xor age | At least one |
| `weight_kg` | Required for feeding / package cost |

---

## ClinicalAssessment (output)

Modules (projection of frozen analyze — **no recompute**):

`meta` · `profile` · `breed` · `traits` · `behavior` · `environment` · `health` · `nutrition` · `activity` · `grooming` · `packages` · `products` · `evidence` · `validation` · `confidence`

**Out of contract for production clients:** HTML, CSV filenames, formula traces, pipeline internals, checkout/session state.

---

## Endpoint catalog

### Core

| Method | Path | Role |
|--------|------|------|
| `GET` | `/health` | Readiness + versions + hash |
| `POST` | `/api/v1/ppie/assess` | **Preferred** DogProfile → ClinicalAssessment |
| `POST` | `/api/v2/wellness/evaluate` | Typed profile → analyze envelope |
| `POST` | `/api/v1/analyze` | Loose JSON → analyze (legacy) |
| `POST` | `/api/v1/clinical-report` | Analyze + assessment + demo report blobs |

### Catalog / store

| Method | Path | Role |
|--------|------|------|
| `GET` | `/api/v1/catalog` | Catalog listing |
| `GET` | `/api/v1/store` | Storefront listing |
| `GET` | `/api/v1/store/{product_id}` | Product detail |
| `GET` | `/api/v1/products/{condition}` | Products by condition |
| `GET` | `/api/v1/evidence/{condition}` | Evidence by condition |

### Groomer / misc

| Method | Path | Role |
|--------|------|------|
| `POST` | `/api/v1/groomer/update` | Groomer observations |
| `GET` | `/api/v1/groomer/session/{pet_id}` | Session |
| `POST` | `/api/groomer/submit` | Submit |
| `POST` | `/api/recommendations` | Recommendations helper |
| `GET` | `/api/breeds` | Breed list |

### Debug (gated)

| Method | Path | Role |
|--------|------|------|
| `GET` | `/debug/calculation` | Validation Console HTML |
| `POST` | `/api/v1/ppie/trace` | EngineTrace |
| `POST` | `/api/v1/ppie/validation-console` | Console JSON |
| `POST` | `/api/v1/ppie/validation-console/markdown` | Markdown export |
| `POST` | `/api/v1/ppie/validation-console/compare` | Side-by-side compare |
| `GET` | `/api/v1/ppie/debug/status` | Boot / live status |
| `GET` | `/api/v1/ppie/debug/presets` | Dog presets |
| `GET` | `/api/v1/ppie/debug/repository` | Table catalog |
| `GET` | `/api/v1/ppie/debug/repository/{table}` | Row preview |

Gate: `PPIE_DEBUG=1` or `?debug=1`. See [DEBUGGING.md](DEBUGGING.md).

---

## Errors (assess)

| Code | Meaning |
|------|---------|
| 400 | Invalid invalid |
| 403 | Debug gate / auth failure |
| 422 | Breed unresolved / unprocessable |
| 503 | Data unavailable |
| 409 | Optional algorithm frozen (policy) |

Prefer additive fields on ClinicalAssessment. Breaking Layer A numbers → algorithm version bump.

---

## Evidence & validation objects

- Never invent citations.  
- Evidence levels: `high` | `moderate` | `emerging` | `guideline` | `pending`.  
- Validation: benchmark or `{ unavailable, reason }`.  
- Traces are not Validation.

---

## Security for production clients

Do **not** expose by default:

- `goal_id` internals, pipeline_trace, calculationTrace  
- Formula internals / variable maps  
- Dual megadict demo payloads  
- Validation Console / EngineTrace  

Public default = assess ClinicalAssessment only. Commerce uses product IDs against Wagtopia’s catalog.

---

## Wagtopia integration loop

1. Map platform dog → DogProfile  
2. `POST /api/v1/ppie/assess`  
3. Render modules (health, nutrition, packages, …)  
4. Drive shop from `product_ids` in Wagtopia catalog  
5. Re-assess when profile changes  

Legacy analyze / clinical-report remain for the demo shell during migration.
