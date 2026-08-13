# INTERVIEW_VERTICAL_SLICE

## Minimal vertical slice (design only)

### 1) Open application
- UI component: CSTC-style main shell
- Request: none
- Backend call: optional health check
- Existing implementation: Wagtopia `/health`
- Response: runtime status
- UI render: status indicator

### 2) Select synthetic dog
- UI component: profile selector/form
- Request: profile draft object
- Backend call: none yet
- Existing implementation: profile form handling + payload adapter expectations
- Response: local state update
- UI render: selected dog summary

### 3) Run analysis
- UI component: analyze action button
- Request: canonical analysis request
- Backend call: `POST /api/v1/analyze` or `/api/v1/ppie/assess`
- Existing implementation: `app/api/main.py` + `PPIEWellnessAgent`
- Response: structured analysis payload
- UI render: loading -> completed state

### 4) Agent processes request
- UI component: loading state panel
- Request: already sent
- Backend call: in-flight
- Existing implementation: agent formula graph execution
- Response: n/a until completion
- UI render: progress/loading text

### 5) Scientific results appear
- UI component: risk/assessment cards
- Request: none (render phase)
- Backend call: none
- Existing implementation: analysis payload fields
- Response: mapped view model
- UI render: priorities and condition insights

### 6) Evidence appears
- UI component: evidence panel/table
- Request: evidence segment or endpoint call
- Backend call: optional `/api/v1/evidence/{condition}` or from analysis payload
- Existing implementation: evidence helpers + payload assembly
- Response: evidence list with sources
- UI render: citations and rationale

### 7) Recommendation appears
- UI component: recommendation cards
- Request: none or mapped from payload
- Backend call: none
- Existing implementation: recommendation output in analyze response
- Response: recommendation entries
- UI render: recommendation section

### 8) Package appears
- UI component: package tier cards
- Request: none or from report payload
- Backend call: none
- Existing implementation: package assembly in app agent modules
- Response: monthly/yearly package options
- UI render: tier comparison

### 9) Financial result appears
- UI component: pricing summary
- Request: optionally `GET /api/v1/store`
- Backend call: storefront endpoint or payload-derived pricing
- Existing implementation: store/catalog endpoints and package economics fields
- Response: totals/cost breakdown
- UI render: financial summary widgets

### 10) Calculation trace inspect
- UI component: trace drawer/panel
- Request: debug trace route or embedded trace
- Backend call: `/api/v1/ppie/trace` (debug-enabled) or payload trace fields
- Existing implementation: engine/debug trace builders
- Response: trace/provenance payload
- UI render: inspectable step-by-step trace
