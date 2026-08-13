# WAGTOPIA_CANONICAL_BOUNDARIES

## Protected canonical runtime/data boundaries (do not alter in integration phase)
- `repository/mathematics/`
- `repository/formulas/`
- `repository/math_debugger/`
- `repository/optimization/`
- `repository/science_graph/`
- `repository/warehouse_qa/`
- `warehouse/`
- Existing scientific datasets and evidence rows

## Preserve O9.5 formula dispositions
- MAT-1001 REVISE
- MAT-1002 REPLACE
- MAT-1003 REPLACE
- MAT-1004 KEEP
- MAT-1005 REVISE
- MAT-1006 REPLACE
- MAT-1007 REPLACE
- MAT-1008 REPLACE

## Preserve O9.6C architectural decisions
- DogProfile -> adapter required
- EvidenceGraph -> adapter/consolidation later
- FormulaRegistry -> repository canonical candidate
- WarehouseInterface -> not yet migration-ready
- Validation -> keep separate by purpose
- Trace -> layered typed trace architecture

## Integration rule
- CSTC contributes presentation shell patterns.
- Wagtopia remains canonical intelligence/scientific runtime.
