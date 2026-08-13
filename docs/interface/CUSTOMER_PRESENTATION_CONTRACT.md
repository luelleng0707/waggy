# CUSTOMER_PRESENTATION_CONTRACT

## Allowed content

- Dog profile
- Wellness analysis summary
- Priority health areas
- Runtime-backed evidence-backed concerns
- Recommended products
- Care package recommendation
- Package pricing/recurring plan where emitted
- Plain-language recommendation explanation

## Prohibited content

Customer surface must not expose:

- Source code references
- Internal formula IDs
- Warehouse row IDs
- Debugger internals
- Engineering provenance status tables
- Replay/sensitivity internals
- Unsupported scientific claims

## Missing-value behavior

If fields are absent in runtime payload, render:

`NOT AVAILABLE`

No synthetic evidence/citations may be generated.
