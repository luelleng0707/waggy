# EVIDENCEGRAPH_CONTRACT

## Minimum canonical scientific graph contract
- Node identity must be deterministic for same condition/evidence input.
- Edge identity must link evidence source node to condition node.
- Citations must preserve: `scientific_quote`, `paper_name`, `paper_link`, `fact_id`.
- Graph must preserve condition/evidence relationship type (`observed`, `trait`, `environment`, `interaction`, `life_stage`, `activity`, `ingredient`).

## Provenance preservation requirements
Migration must not discard:
- scientific quote
- paper name
- paper link
- source/fact id
- evidence relationship

## Missing evidence behavior
- Empty evidence collection yields empty nodes/edges/citations without exception.

## Duplicate handling
- Duplicate evidence rows may generate multiple edges; behavior must remain deterministic and traceable.

## Deterministic ordering
- For identical input collection order, graph output order and IDs must remain stable.
