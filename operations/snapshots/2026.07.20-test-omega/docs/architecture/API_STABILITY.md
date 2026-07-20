# API Stability

Generated: `2026-07-20T22:13:35.720220+00:00`
Algorithm: `2.1.0`

| Method | Path | Version | Deprecated | Compatibility | Consumers |
|---|---|---|---|---|---|
| GET | `/` | static | False | transitional | — |
| GET | `/api/breeds` | legacy | False | transitional | — |
| POST | `/api/groomer/submit` | legacy | False | transitional | — |
| POST | `/api/recommendations` | legacy | True | transitional | — |
| POST | `/api/v1/analyze` | v1 | False | stable | legacy clients |
| GET | `/api/v1/catalog` | v1 | False | stable | — |
| POST | `/api/v1/clinical-report` | v1 | False | stable | app.js, StandardReportRenderer |
| GET | `/api/v1/evidence/{condition}` | v1 | False | stable | — |
| GET | `/api/v1/graph/condition/{condition_id:path}` | v1 | False | stable | — |
| GET | `/api/v1/graph/explanation/{recommendation_id:path}` | v1 | False | stable | — |
| GET | `/api/v1/graph/ingredient/{ingredient_id:path}` | v1 | False | stable | — |
| GET | `/api/v1/graph/paper/{paper_id:path}` | v1 | False | stable | — |
| GET | `/api/v1/graph/product/{product_id:path}` | v1 | False | stable | — |
| GET | `/api/v1/graph/summary` | v1 | False | stable | — |
| GET | `/api/v1/graph/why` | v1 | False | stable | — |
| GET | `/api/v1/groomer/session/{pet_id}` | v1 | False | stable | — |
| POST | `/api/v1/groomer/update` | v1 | False | stable | — |
| GET | `/api/v1/platform/audit` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/coverage` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/dependencies` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/formulas` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/performance` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/release` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/runtime` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/science` | v1 | False | stable | ops, developers |
| GET | `/api/v1/platform/status` | v1 | False | stable | ops, developers |
| POST | `/api/v1/ppie/assess` | v1 | False | stable | integrations, Validation Console |
| GET | `/api/v1/ppie/debug/presets` | v1 | False | stable | — |
| GET | `/api/v1/ppie/debug/repository` | v1 | False | stable | — |
| GET | `/api/v1/ppie/debug/repository/{table}` | v1 | False | stable | — |
| GET | `/api/v1/ppie/debug/status` | v1 | False | stable | — |
| POST | `/api/v1/ppie/trace` | v1 | False | stable | — |
| POST | `/api/v1/ppie/validation-console` | v1 | False | stable | — |
| POST | `/api/v1/ppie/validation-console/compare` | v1 | False | stable | — |
| POST | `/api/v1/ppie/validation-console/markdown` | v1 | False | stable | — |
| GET | `/api/v1/products/{condition}` | v1 | False | stable | — |
| GET | `/api/v1/science/audit` | v1 | False | stable | — |
| GET | `/api/v1/science/coverage` | v1 | False | stable | — |
| GET | `/api/v1/science/versions` | v1 | False | stable | — |
| GET | `/api/v1/store` | v1 | False | stable | — |
| GET | `/api/v1/store/{product_id}` | v1 | False | stable | — |
| POST | `/api/v2/wellness/evaluate` | legacy | False | transitional | — |
| GET | `/app.js` | static | False | transitional | — |
| GET | `/catalog-service.js` | static | False | transitional | — |
| GET | `/debug/calculation` | static | False | transitional | — |
| GET,HEAD | `/docs` | static | False | transitional | — |
| GET,HEAD | `/docs/oauth2-redirect` | static | False | transitional | — |
| GET | `/health` | static | False | transitional | — |
| GET,HEAD | `/openapi.json` | static | False | transitional | — |
| GET | `/platform/dashboard` | static | False | transitional | ops, developers |
| GET | `/ppie-dev-menu.js` | static | False | transitional | — |
| GET | `/ppie-sheets.js` | static | False | transitional | — |
| GET | `/ppie-shell.js` | static | False | transitional | — |
| GET | `/ppie-trace.js` | static | False | transitional | — |
| GET | `/ppie-ui.js` | static | False | transitional | — |
| GET | `/ppie-validation-console.css` | static | False | transitional | — |
| GET | `/ppie-validation-console.js` | static | False | transitional | — |
| GET,HEAD | `/redoc` | static | False | transitional | — |
| GET | `/report-renderer.js` | static | False | transitional | — |
| GET | `/styles.css` | static | False | transitional | — |
| GET | `/theme.css` | static | False | transitional | — |
