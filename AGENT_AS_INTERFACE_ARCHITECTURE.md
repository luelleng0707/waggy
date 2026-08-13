# AGENT_AS_INTERFACE_ARCHITECTURE

## 1) Can CSTC frontend call Wagtopia directly?
- Not directly today (CSTC is desktop Qt with no built-in Wagtopia HTTP client abstraction), but it can via a small API adapter layer.

## 2) Should Wagtopia expose a unified agent endpoint?
- Yes. Prefer one canonical analysis endpoint surface for presentation clients.

## 3) Should existing CSTC backend APIs remain?
- CSTC has no backend API surface; CSTC local DB APIs are in-process ORM calls.

## 4) Should CSTC API calls be replaced?
- N/A (no HTTP API calls currently). Data retrieval should be redirected from local ORM to Wagtopia adapter calls.

## 5) Should we create a Wagtopia adapter?
- Yes.

## 6) Where should the adapter live?
- Presentation-side adapter layer (for CSTC shell) and/or thin orchestration module in Wagtopia API layer.

## 7) Canonical request object
- Dog analysis request aligned with `DogProfileInput` semantics:
  - dog identity/name
  - breeds / optional split
  - age or birthday
  - weight
  - environment/activity
  - observed_conditions

## 8) Canonical response object
- Structured analysis envelope including:
  - health/risk priorities
  - evidence/provenance
  - product recommendations
  - packages + financial breakdown
  - trace metadata references

## 9) Provenance representation
- Include citation and source/fact identifiers where available.

## 10) Error representation
- Standardized envelope with error code, message, context path, recoverable flag.

## 11) Calculation trace representation
- Typed trace references (runtime, formula, calculation trace summaries) with optional expanded debug payload.

## 12) Long-running analysis representation
- Request/response mode with optional async status model if needed later (not required for initial vertical slice).

## 13) Can current agent satisfy this without changing scientific logic?
- Yes for initial integration, provided adapter transforms CSTC profile inputs and maps Wagtopia structured outputs to UI view models.
