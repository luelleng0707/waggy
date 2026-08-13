# THREE_SURFACE_PRESENTATION_ARCHITECTURE

## Core principle

One runtime execution feeds three presentation projections.

`app.main -> app.api.main -> PPIEWellnessAgent -> analyze payload -> app.presentation.adapter -> customer/business/developer`

## Surface architecture

### Customer (`/`)

Prioritizes:

- dog profile
- key health/risk insights
- observed and estimated values where available
- recommended package and explanation
- pricing and recurring plan outputs
- user-facing evidence summary

Must not expose developer internals (formula IDs/source lines/warehouse row IDs).

### Business (`/business`)

Prioritizes:

- portfolio opportunity framing from runtime-backed outputs
- condition/prevalence opportunity context
- package economics and recurring outputs
- product and package coverage snapshots
- explicit `NOT AVAILABLE` for missing business KPIs

Must not fabricate market growth/revenue forecasts.

### Developer (`/developer`)

Prioritizes:

- runtime stage flow
- formula execution records
- source/equation/provenance status fields
- warehouse/evidence/replay/sensitivity/publication risk status
- trace and correlation artifacts

Read-only by design.

## Shared identity proof

- `analysis_signature`: stable hash over selected analyze payload fields
- `presentation_correlation_id`: request-level correlation marker for three-surface projection

## Route/security contract

- `/` public
- `/business` optional key gate (`WAGTOPIA_BUSINESS_ACCESS_KEY`)
- `/developer` optional key gate (`WAGTOPIA_DEVELOPER_ACCESS_KEY`)
- `/debug/calculation` compatibility/internal endpoint (non-canonical)
