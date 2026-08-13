# BATCH_A_REGRESSION

## Pre-archive result
- `pytest tests/mathematics -q` -> 13 passed
- `pytest tests/formulas -q` -> 3 passed
- `pytest tests/math_debugger -q` -> 20 passed
- `pytest tests/optimization -q` -> 6 passed
- `pytest tests/science_graph -q` -> 6 passed
- `pytest tests/warehouse_qa -q` -> 6 passed
- Total: 54 passed, 0 failed

## Post-archive result
- `pytest tests/mathematics -q` -> 13 passed
- `pytest tests/formulas -q` -> 3 passed
- `pytest tests/math_debugger -q` -> 20 passed
- `pytest tests/optimization -q` -> 6 passed
- `pytest tests/science_graph -q` -> 6 passed
- `pytest tests/warehouse_qa -q` -> 6 passed
- Total: 54 passed, 0 failed

## Warehouse validation
- `py -3 scripts/validate_warehouse.py` -> FAIL
- Total issues: 8
- Issue set unchanged (known `mechanisms.condition_mechanisms` and `mechanisms.food_mechanisms` broken references).

## Comparison
- No new test failures introduced.
- No regression count delta.
- Warehouse validation status unchanged from known baseline.
