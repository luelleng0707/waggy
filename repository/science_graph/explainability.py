"""Evidence aggregation and explainability for traversed graph paths."""

from __future__ import annotations

from .models import GraphTraversal, KnowledgeGraph


class DeterministicScientificExplainability:
    def explain(self, graph: KnowledgeGraph, traversal: GraphTraversal) -> GraphTraversal:
        edge_by_id = {edge.edge_id: edge for edge in graph.edges}
        quotes: list[str] = list(traversal.scientific_quotes)
        papers: list[str] = list(traversal.paper_names)
        links: list[str] = list(traversal.paper_links)

        for edge_id in traversal.path_edge_ids:
            edge = edge_by_id.get(edge_id)
            if edge is None:
                continue
            if edge.scientific_quote:
                quotes.append(edge.scientific_quote)
            if edge.paper_name:
                papers.append(edge.paper_name)
            if edge.paper_link:
                links.append(edge.paper_link)

        formula_ids = tuple(sorted(set(traversal.formula_ids + ("GRF-802",))))
        return GraphTraversal(
            query=traversal.query,
            start_node_id=traversal.start_node_id,
            path_node_ids=traversal.path_node_ids,
            path_edge_ids=traversal.path_edge_ids,
            scientific_quotes=tuple(dict.fromkeys(quotes)),
            paper_names=tuple(dict.fromkeys(papers)),
            paper_links=tuple(dict.fromkeys(links)),
            formula_ids=formula_ids,
        )
