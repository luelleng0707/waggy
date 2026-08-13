# TARGET_INTERFACE_ARCHITECTURE

## Recommended single target architecture

CSTC-style Presentation Shell
-> Wagtopia Presentation Adapter
-> Wagtopia Agent/API Boundary
-> Existing Wagtopia Runtime (app production path now; repository canonicalization later)
-> Warehouse + scientific datasets

## Component responsibilities

### Frontend (presentation)
- UI shell, navigation, forms, cards, tables, modals, user workflows.
- No scientific logic.

### Adapter
- Translate UI requests -> canonical analysis request.
- Translate agent responses -> UI view models.
- Normalize errors/loading/provenance/trace envelopes.

### Agent/API
- Accept canonical request.
- Execute existing pipeline.
- Return structured result + trace/provenance metadata.

### Runtime
- Scientific, recommendation, and optimization logic remains in Wagtopia runtime modules.

### Repository and warehouse
- Warehouse/scientific/fact pipelines remain canonical data foundation.

## Request flow
1. User triggers analysis from presentation shell.
2. Adapter builds analysis request model.
3. Adapter calls Wagtopia API endpoint.
4. Agent executes runtime pipeline.
5. Response returned to adapter.
6. Adapter emits UI view model.

## Response flow
- Agent structured output -> adapter mapping -> presentation components.

## Provenance flow
- Runtime traces/evidence metadata -> adapter provenance model -> inspectable UI sections.

## Error flow
- API/agent errors -> adapter error model -> UI error surfaces with retry guidance.
