# BUSINESS_PRESENTATION_CONTRACT

## Allowed content

- Portfolio analytics from runtime payloads
- Breed/dog scope from analyzed profile(s)
- Health opportunity rows using runtime `healthInsights`
- Observed/estimated prevalence only when emitted by runtime
- Product and package opportunities from runtime recommendations
- Cost/pricing/discount/savings fields only when emitted
- Recurring economics only when emitted

## Required missing-value behavior

If a business metric is not emitted by runtime, display:

`NOT AVAILABLE`

No synthetic financial/scientific values may be inferred.

## Prohibited

- Implementing recommendation logic in UI
- Implementing scientific calculations in UI
- Inventing market/science evidence
- Exposing developer-only execution internals unless explicitly routed to developer surface
