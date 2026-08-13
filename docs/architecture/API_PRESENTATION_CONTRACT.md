# API_PRESENTATION_CONTRACT

## Endpoints in scope

### `GET /`

- Request: none
- Response: customer HTML (`legacy/index.html`)
- Runtime owner: `app.api.main.index_page`
- Authentication: public
- Trace/correlation: none in body
- Error behavior: 404 if static asset missing
- Production status: IMPLEMENTED

### `GET /business`

- Request: optional surface access key
- Response: business HTML (`legacy/business.html`)
- Runtime owner: `app.api.main.business_page`
- Authentication: optional `WAGTOPIA_BUSINESS_ACCESS_KEY`
- Trace/correlation: none in HTML
- Error behavior: 401 when gate configured and key missing/invalid
- Production status: IMPLEMENTED

### `GET /developer`

- Request: optional surface access key
- Response: developer HTML (`legacy/debug/calculation.html`)
- Runtime owner: `app.api.main.developer_page`
- Authentication: optional `WAGTOPIA_DEVELOPER_ACCESS_KEY`
- Trace/correlation: developer JS may request debug APIs that include execution IDs
- Error behavior: 401 when gate configured and key missing/invalid
- Production status: IMPLEMENTED

### `GET /health`

- Request: none
- Response: JSON health status and data metadata
- Runtime owner: `app.api.main.health`
- Authentication: public
- Trace/correlation: response headers include timing/version data
- Error behavior: degraded status when data issues detected
- Production status: IMPLEMENTED

### `POST /api/v1/analyze`

- Request: dog profile payload
- Response: legacy analyze JSON from app runtime
- Runtime owner: `app.api.main.analyze_v1` -> `PPIEWellnessAgent`
- Authentication: optional `API_KEYS` gate
- Trace/correlation: timing/version headers; debug block may include formula execution records
- Error behavior: 400 validation, 500 runtime failure
- Production status: IMPLEMENTED

### `POST /api/v1/presentation/three-surfaces`

- Request: dog profile payload (+ optional `debug=1`)
- Response: `three_surface_presentation.v1` envelope
- Runtime owner: `app.api.main.presentation_three_surfaces` + `app.presentation.adapter`
- Authentication:
  - optional `API_KEYS`
  - optional business access key gate
  - optional developer key gate when debug path is requested
- Trace/correlation:
  - `analysis_signature`
  - `presentation_correlation_id`
- Error behavior: 400 validation, 401 gated access failure, 500 runtime failure
- Production status: IMPLEMENTED
