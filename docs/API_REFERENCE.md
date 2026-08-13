# API_REFERENCE.md

Auth: header `x-api-key` (default demo: `wagtopia-demo-key`).

## Clinical

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/ppie/assess` | Full assessment |
| POST | `/api/v1/clinical-report` | Clinical report |
| POST | `/api/v1/analyze` | Analyze / legacy shape |
| POST | `/api/v2/wellness/evaluate` | Wellness evaluate |
| POST | `/api/v1/ppie/trace` | Execution trace |
| POST | `/api/v1/ppie/validation-console` | Validation console JSON |

## Catalog

| Method | Path |
|--------|------|
| GET | `/api/v1/catalog` |
| GET | `/api/v1/store` |
| GET | `/api/v1/store/{product_id}` |
| GET | `/api/breeds` |

## Science graph (read-only)

| Method | Path |
|--------|------|
| GET | `/api/v1/graph/summary` |
| GET | `/api/v1/graph/condition/{id}` |
| GET | `/api/v1/science/audit` |
| GET | `/api/v1/science/coverage` |

## Authoring (staging)

| Method | Path |
|--------|------|
| GET/POST | `/api/v1/authoring/*` |
| GET | `/api/v1/research/*` |

## Health / demo

| Method | Path |
|--------|------|
| GET | `/health` |
| GET | `/` | Demo UI |

Contract: **DogProfile in → ClinicalAssessment JSON out**.
