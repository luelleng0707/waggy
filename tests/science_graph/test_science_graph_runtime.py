from __future__ import annotations

from repository.science_graph import (
    DeterministicScientificExplainability,
    DeterministicScientificTraversalEngine,
    KnowledgeGraph,
    ScientificEdge,
    ScientificNode,
    ScientificGraphRuntime,
    WarehouseScientificGraphBuilder,
    WarehouseScientificGraphValidator,
)
from repository.warehouse import WarehouseInterface


def test_graph_construction_is_deterministic():
    builder = WarehouseScientificGraphBuilder(WarehouseInterface())
    first = builder.build()
    second = builder.build()
    assert first == second
    assert first.nodes
    assert first.edges


def test_graph_validation_and_fk_integrity():
    runtime = ScientificGraphRuntime(WarehouseInterface())
    result = runtime.run()
    assert result.validation.statistics.total_nodes > 0
    assert result.validation.statistics.total_edges > 0
    assert all(
        issue.issue_code not in {"BROKEN_SOURCE_FK", "BROKEN_TARGET_FK"}
        for issue in result.validation.issues
    )


def test_condition_to_product_traversal_and_citation_aggregation():
    runtime = ScientificGraphRuntime(WarehouseInterface())
    graph = runtime.run().graph
    traversal = runtime.traverse(graph, "Hip Dysplasia", "product")
    assert traversal.path_node_ids
    assert traversal.path_edge_ids
    assert traversal.scientific_quotes
    assert traversal.paper_names
    assert traversal.paper_links
    assert "GRF-802" in traversal.formula_ids


def test_ingredient_to_condition_traversal_is_deterministic():
    runtime = ScientificGraphRuntime(WarehouseInterface())
    graph = runtime.run().graph
    first = runtime.traverse(graph, "EPA", "condition")
    second = runtime.traverse(graph, "EPA", "condition")
    assert first == second


def test_duplicate_detection_flags_similar_concepts():
    validator = WarehouseScientificGraphValidator()
    graph = KnowledgeGraph(
        nodes=(
            ScientificNode("OBJ_A", "objective", "Joint Inflammation Reduction", "x:1"),
            ScientificNode("OBJ_B", "objective", "Reduction Joint Inflammation", "x:2"),
        ),
        edges=(
            ScientificEdge(
                edge_id="E1",
                source_node_id="OBJ_A",
                target_node_id="OBJ_B",
                relationship_type="related",
                warehouse_row_id="x:e1",
                scientific_quote="Quote",
                paper_name="Paper",
                paper_link="https://example.org",
                formula_ids=("GRF-803",),
            ),
        ),
        evidence_nodes=tuple(),
        evidence_edges=tuple(),
    )
    validation = validator.validate(graph)
    assert validation.duplicate_concepts


def test_traversal_engine_and_explainability_modules_directly():
    runtime = ScientificGraphRuntime(WarehouseInterface())
    graph = runtime.run().graph
    traversal = DeterministicScientificTraversalEngine().traverse(graph, "SRC_003", "condition")
    explained = DeterministicScientificExplainability().explain(graph, traversal)
    assert explained.path_node_ids
    assert explained.paper_names
