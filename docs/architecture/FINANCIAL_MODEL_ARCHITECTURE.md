# FINANCIAL_MODEL_ARCHITECTURE

## Financial flow (current)

`product cost -> serving consumption -> monthly consumption -> package cost -> package price -> discount -> recurring economics -> yearly economics`

## Runtime owners

- Production: `app.agent.bundle_engine` + `app.agent.response_assembler`
- Projection: `app.presentation.adapter` business/customer surfaces

## Data classes by semantics

| Type | Examples | Status |
|---|---|---|
| Observed product prices | list price fields from product/pricing datasets | IMPLEMENTED |
| Configured assumptions | serving-size assumptions, package rule assumptions | PARTIAL |
| Calculated outputs | monthly totals, yearly totals, equivalent recurring values | IMPLEMENTED/PARTIAL depending on profile and package availability |

## Known partial fields

- Business projection currently marks several fields as `NOT AVAILABLE` when runtime does not provide them (e.g., margin/product gaps).
- Discount/savings depend on package/economics fields in runtime output and are not guaranteed for every response.

## Non-fabrication rule

- If runtime does not emit a financial metric, show `NOT AVAILABLE`.
- Do not infer market/revenue forecasts unless explicitly computed by runtime.
