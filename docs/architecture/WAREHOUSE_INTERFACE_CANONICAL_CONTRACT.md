# WAREHOUSE_INTERFACE_CANONICAL_CONTRACT

## Canonical target candidate
- `repository/warehouse/warehouse_interface.py`

## Contract
- Dataset registration: canonical dataset map with stable dataset keys.
- Dataset identity: dataset keys map deterministically to warehouse file paths.
- Loading: `load_dataset(dataset_name)` returns DataFrame copy, string-typed columns.
- Read-only semantics: internal cache not exposed for mutation.
- Row identity: ID columns preserved as strings.
- Error handling: unknown dataset key must fail explicitly.
- Missing dataset behavior: explicit failure path, not silent empty success.
- FK validation boundary: structural checks in `validate()` and warehouse QA layers.
- Caching behavior: repeat loads return independent copies over cached source.

## Current violations to track (not fixed in O9.6C)
- App-side direct CSV readers and repository validation helper direct reader remain known boundary exceptions requiring later migration planning.
