# WAGTOPIA_PRESENTATION_ADAPTER_SPEC

## Scope
Translation-only boundary between presentation shell and Wagtopia agent/API.
No scientific logic duplication.

## REQUEST MODEL
- `AnalysisRequest`
  - `subject_id` (optional)
  - `name`
  - `primary_breed`
  - `secondary_breed` (optional)
  - `breed_split_pct` (optional)
  - `age_years` or `birthday`
  - `weight_kg`
  - `current_environment`
  - `activity_level` (optional)
  - `sex/gender` (optional)
  - `observed_conditions[]`

## RESPONSE MODEL
- `AnalysisResponse`
  - `summary`
  - `risk_priorities[]`
  - `evidence[]`
  - `recommendations[]`
  - `products[]`
  - `packages[]`
  - `financials`
  - `provenance`
  - `trace_ref`

## ERROR MODEL
- `AdapterError`
  - `code`
  - `message`
  - `source` (`ui|adapter|api|agent`)
  - `details`
  - `retryable`

## LOADING MODEL
- `AdapterRunState`
  - `status` (`idle|running|completed|failed`)
  - `started_at`
  - `finished_at`
  - `progress_message`

## PROVENANCE MODEL
- `ProvenanceEntry`
  - `fact_id`
  - `evidence_id`
  - `paper_name`
  - `paper_link`
  - `scientific_quote`

## TRACE MODEL
- `TraceSummary`
  - `run_id`
  - `pipeline_steps[]`
  - `formula_ids[]`
  - `warnings[]`
  - `errors[]`
  - optional `expanded_trace`

## SESSION MODEL
- `PresentationSession`
  - `session_id`
  - `subject_id`
  - `last_profile`
  - `last_result_ref`
  - `updated_at`

## PRODUCT MODEL
- `ProductViewModel`
  - `product_id`
  - `name`
  - `category`
  - `coverage`
  - `price`
  - `active_ingredients[]`

## PACKAGE MODEL
- `PackageViewModel`
  - `tier`
  - `items[]`
  - `monthly_cost`
  - `yearly_cost`
  - `savings`

## FINANCIAL MODEL
- `FinancialViewModel`
  - `currency`
  - `line_items[]`
  - `subtotal`
  - `discount`
  - `total`
