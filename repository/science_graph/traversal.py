"""Deterministic scientific graph traversal engine."""

from __future__ import annotations

from collections import deque

from .models import GraphTraversal, KnowledgeGraph


class DeterministicScientificTraversalEngine:
    def traverse(self, graph: KnowledgeGraph, query: str, target_node_type: str) -> GraphTraversal:
        node_by_id = {node.node_id: node for node in graph.nodes}
        node_by_name: dict[str, list[str]] = {}
        for node in graph.nodes:
            key = node.node_name.strip().lower()
            if key:
                node_by_name.setdefault(key, []).append(node.node_id)
        for key in node_by_name:
            node_by_name[key] = sorted(set(node_by_name[key]))

        query_text = query.strip()
        if query_text in node_by_id:
            start_id = query_text
        else:
            matches = node_by_name.get(query_text.lower(), [])
            if not matches:
                raise ValueError(f"Unknown query node: {query}")
            start_id = matches[0]

        path_edge_ids, path_node_ids = _shortest_path(graph, start_id, target_node_type)
        evidence = _collect_evidence(graph, path_edge_ids)
        return GraphTraversal(
            query=query,
            start_node_id=start_id,
            path_node_ids=path_node_ids,
            path_edge_ids=path_edge_ids,
            scientific_quotes=evidence["quotes"],
            paper_names=evidence["papers"],
            paper_links=evidence["links"],
            formula_ids=("GRF-801", "GRF-804"),
        )


def _shortest_path(
    graph: KnowledgeGraph,
    start_id: str,
    target_node_type: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    node_by_id = {node.node_id: node for node in graph.nodes}
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for edge in graph.edges:
        adjacency.setdefault(edge.source_node_id, []).append((edge.target_node_id, edge.edge_id))
        adjacency.setdefault(edge.target_node_id, []).append((edge.source_node_id, edge.edge_id))
    for node_id in adjacency:
        adjacency[node_id] = sorted(adjacency[node_id], key=lambda pair: (pair[0], pair[1]))

    queue = deque([(start_id, tuple([start_id]), tuple())])
    visited: set[str] = {start_id}
    while queue:
        current, path_nodes, path_edges = queue.popleft()
        node = node_by_id.get(current)
        if node is not None and node.node_type == target_node_type and current != start_id:
            return path_edges, path_nodes
        for neighbor, edge_id in adjacency.get(current, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append((neighbor, path_nodes + (neighbor,), path_edges + (edge_id,)))
    raise ValueError(f"No traversal path found from {start_id} to node_type={target_node_type}")


def _collect_evidence(graph: KnowledgeGraph, edge_ids: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    edge_by_id = {edge.edge_id: edge for edge in graph.edges}
    quotes: list[str] = []
    papers: list[str] = []
    links: list[str] = []
    for edge_id in edge_ids:
        edge = edge_by_id.get(edge_id)
        if edge is None:
            continue
        if edge.scientific_quote:
            quotes.append(edge.scientific_quote)
        if edge.paper_name:
            papers.append(edge.paper_name)
        if edge.paper_link:
            links.append(edge.paper_link)
    return {
        "quotes": tuple(dict.fromkeys(quotes)),
        "papers": tuple(dict.fromkeys(papers)),
        "links": tuple(dict.fromkeys(links)),
    }
