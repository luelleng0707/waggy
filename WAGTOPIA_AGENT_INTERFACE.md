# WAGTOPIA_AGENT_INTERFACE

## Public entrypoint
- `app/agent/engine.py`:
  - `PPIEWellnessAgent.generate_reproducible_report(profile)` (async)
  - `PPIEWellnessAgent.generate_reproducible_report_sync(profile)`
  - `PPIEWellnessAgent.assess(profile)` (typed AssessmentResult)

## Input boundary
- `DogProfileInput` (Pydantic) in `app/agent/state.py`.
- Legacy request normalization via `app/api/payload_adapter.py::profile_from_analyze_body`.

## Output boundary
- Primary API output is structured dict (`legacy_json`) assembled by graph export node.
- Typed intermediate/final container: `AssessmentResult`.

## Streaming
- No streaming API contract observed for incremental token/event delivery.

## Intermediate states
- Yes, internal node-level and pipeline traces are captured.

## Provenance
- Yes, via trace/debug payload channels and evidence attachment logic.

## Calculation traces
- Yes:
  - `app/agent/calculation_trace.py`
  - `app/agent/pipeline_trace.py`
  - debug engine trace in `app/debug/clinical_execution_debug.py`

## Recommendations/products/packages/financial outputs
- Yes, included in structured analysis output and storefront/report endpoints.

## Error boundary
- Value errors surfaced as 400 in API routes.
- Runtime failures surfaced as 500 with logged exceptions.

## Session/conversation model
- No rich conversation model.
- Minimal in-memory groomer session dictionary in `app/api/main.py`.
