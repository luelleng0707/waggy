# DEVELOPER_PRESENTATION_CONTRACT

Developer surface is an execution-provenance explorer over actual runtime outputs.

## Required fields per execution record

- execution tree / stage flow
- formula id + version (when emitted)
- source file / function / line range (or source unavailable)
- actual computation metadata from runtime trace
- formal equation only when documented
- input variables / parameters / intermediates / outputs
- warehouse references (real lookups only)
- evidence references (real references only)
- replay status
- sensitivity status
- publication status

## Explicit status semantics

- Missing source: `NOT AVAILABLE`
- Missing formal equation: `NOT DOCUMENTED`
- Replay unsupported: `NOT IMPLEMENTED`
- Sensitivity unsupported: `NOT IMPLEMENTED`

Never infer synthetic equations, evidence, warehouse rows, replay values, or sensitivity values.

## Security

- Read-only projection endpoints only.
- No mutation/debug command execution from developer UI.
