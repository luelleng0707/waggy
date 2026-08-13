# Ω7 Formula Registry

## GRF-801 — Shortest Scientific Path
- Equation: shortest unweighted path across graph edges.
- Purpose: deterministic minimal-hop traversal.

## GRF-802 — Evidence Aggregation
- Equation: union of edge evidence encountered along traversal path.
- Purpose: preserve quote/paper provenance for explainability.

## GRF-803 — Relationship Validation
- Equation: `edge.source in nodes and edge.target in nodes and evidence_fields_complete`.
- Purpose: structural and foreign-key integrity checks.

## GRF-804 — Traversal
- Equation: breadth-first deterministic neighbor expansion sorted by node/edge id.
- Purpose: stable path selection independent of runtime ordering.

## GRF-805 — Evidence Completeness
- Equation: `missing_evidence_edges = count(edges with empty quote|paper|link)`.
- Purpose: strict scientific evidence completeness metric.
