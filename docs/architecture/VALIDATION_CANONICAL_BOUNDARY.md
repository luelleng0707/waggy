# VALIDATION_CANONICAL_BOUNDARY

## Validation taxonomy
A. Dog/profile validation: input transport and graph completeness checks (`app/agent/state.py`, `app/agent/nodes/validation_node.py`).
B. Warehouse schema validation: structural/FK checks (`repository/warehouse/warehouse_interface.py`, `repository/warehouse_qa/*`).
C. Scientific evidence validation: citation/ontology/coverage checks (`repository/warehouse_qa/citations.py`, `coverage.py`, `ontology.py`).
D. Runtime state validation: stage/runtime safety checks (`repository/pipeline` validator protocol and app graph checks).
E. Mathematical/formula validation: registry integrity + constant/provenance validation (`repository/formulas/validator.py`, `repository/math_debugger/formula_validator.py`).
F. Optimization constraint validation: optimization runtime constraints and conflict/synergy enforcement (`repository/optimization/constraints.py` + runtime).

## Separation rule
- These validations should remain separated by semantics.
- Shared reporting interfaces are acceptable; logic unification is not required.

## Mutation rule
- Validation systems must not mutate scientific warehouse facts or silently rewrite formulas/runtime inputs.
