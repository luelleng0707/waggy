# DUPLICATE_CONCEPTS

## DogProfile
- implementation_a: `app/ui/templates/components/dog_profile_card.html`
- implementation_b: `repository/models/runtime.py`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `app/ui/templates/components/dog_profile_card.html`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

## EvidenceGraph
- implementation_a: `app/agent/nodes/evidence_node.py`
- implementation_b: `app/api/evidence.py`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `app/agent/nodes/evidence_node.py`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

## FormulaRegistry
- implementation_a: `app/agent/formula_registry.py`
- implementation_b: `app/inference/formula_registry.py`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `app/agent/formula_registry.py`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

## WarehouseInterface
- implementation_a: `repository/warehouse/__init__.py`
- implementation_b: `repository/warehouse/warehouse_interface.py`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `repository/warehouse/__init__.py`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

## Validation
- implementation_a: `app/agent/nodes/validation_node.py`
- implementation_b: `docs/validation_report.md`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `app/agent/nodes/validation_node.py`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

## Trace
- implementation_a: `app/agent/calculation_trace.py`
- implementation_b: `app/agent/formula_trace.py`
- functional_difference: requires targeted review; parallel concept presence detected
- dependency_difference: differs by package imports and consumers
- canonical_candidate: `app/agent/calculation_trace.py`
- reason: concept appears in multiple package boundaries
- migration_risk: MEDIUM

