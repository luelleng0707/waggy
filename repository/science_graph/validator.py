"""Graph consistency, FK integrity, and duplicate detection for Ω7."""

from __future__ import annotations

import re

from .models import GraphStatistics, GraphValidation, GraphValidationIssue, KnowledgeGraph


class WarehouseScientificGraphValidator:
    def validate(self, graph: KnowledgeGraph) -> GraphValidation:
        issues: list[GraphValidationIssue] = []
        node_ids = [row.node_id for row in graph.nodes]
        edge_ids = [row.edge_id for row in graph.edges]
        node_set = set(node_ids)

        _add_duplicate_id_issues(node_ids, "node", issues)
        _add_duplicate_id_issues(edge_ids, "edge", issues)
        _add_duplicate_edge_issues(graph, issues)
        _add_fk_issues(graph, node_set, issues)
        _add_missing_evidence_issues(graph, issues)
        _add_orphan_node_issues(graph, issues)
        _add_cycle_issues(graph, issues)

        duplicates = _duplicate_concepts(graph)
        for left, right in duplicates:
            issues.append(
                GraphValidationIssue(
                    issue_code="DUPLICATE_CONCEPT",
                    severity="warning",
                    detail=f"{left} ~ {right}",
                    warehouse_row_id="graph:concepts",
                )
            )

        stats = _graph_statistics(graph, duplicates)
        ok = not any(row.severity == "error" for row in issues)
        return GraphValidation(
            ok=ok,
            issues=tuple(issues),
            duplicate_concepts=tuple(duplicates),
            statistics=stats,
            formula_ids=("GRF-803", "GRF-805"),
        )


def _add_duplicate_id_issues(values: list[str], kind: str, issues: list[GraphValidationIssue]) -> None:
    seen: set[str] = set()
    dupes: set[str] = set()
    for value in values:
        if value in seen:
            dupes.add(value)
        seen.add(value)
    for duplicate in sorted(dupes):
        issues.append(
            GraphValidationIssue(
                issue_code=f"DUPLICATE_{kind.upper()}_ID",
                severity="error",
                detail=f"Duplicate {kind}_id={duplicate}",
                warehouse_row_id=f"graph:{kind}s",
            )
        )


def _add_duplicate_edge_issues(graph: KnowledgeGraph, issues: list[GraphValidationIssue]) -> None:
    seen: set[tuple[str, str, str]] = set()
    dupes: set[tuple[str, str, str]] = set()
    for edge in graph.edges:
        key = (edge.source_node_id, edge.target_node_id, edge.relationship_type)
        if key in seen:
            dupes.add(key)
        seen.add(key)
    for source, target, rel in sorted(dupes):
        issues.append(
            GraphValidationIssue(
                issue_code="DUPLICATE_EDGE",
                severity="error",
                detail=f"Duplicate edge {source}->{target} ({rel})",
                warehouse_row_id="graph:edges",
            )
        )


def _add_fk_issues(graph: KnowledgeGraph, node_set: set[str], issues: list[GraphValidationIssue]) -> None:
    for edge in graph.edges:
        if edge.source_node_id not in node_set:
            issues.append(
                GraphValidationIssue(
                    issue_code="BROKEN_SOURCE_FK",
                    severity="error",
                    detail=f"Missing source node {edge.source_node_id}",
                    warehouse_row_id=edge.warehouse_row_id,
                )
            )
        if edge.target_node_id not in node_set:
            issues.append(
                GraphValidationIssue(
                    issue_code="BROKEN_TARGET_FK",
                    severity="error",
                    detail=f"Missing target node {edge.target_node_id}",
                    warehouse_row_id=edge.warehouse_row_id,
                )
            )


def _add_missing_evidence_issues(graph: KnowledgeGraph, issues: list[GraphValidationIssue]) -> None:
    for edge in graph.edges:
        if not edge.scientific_quote.strip() or not edge.paper_name.strip() or not edge.paper_link.strip():
            issues.append(
                GraphValidationIssue(
                    issue_code="MISSING_EVIDENCE",
                    severity="error",
                    detail=f"Incomplete evidence on edge {edge.edge_id}",
                    warehouse_row_id=edge.warehouse_row_id,
                )
            )


def _add_orphan_node_issues(graph: KnowledgeGraph, issues: list[GraphValidationIssue]) -> None:
    connected: set[str] = set()
    for edge in graph.edges:
        connected.add(edge.source_node_id)
        connected.add(edge.target_node_id)
    for node in graph.nodes:
        if node.node_id not in connected:
            issues.append(
                GraphValidationIssue(
                    issue_code="ORPHAN_NODE",
                    severity="warning",
                    detail=f"Node has no edges: {node.node_id}",
                    warehouse_row_id=node.warehouse_row_id,
                )
            )


def _add_cycle_issues(graph: KnowledgeGraph, issues: list[GraphValidationIssue]) -> None:
    adjacency: dict[str, list[str]] = {}
    for edge in graph.edges:
        if edge.relationship_type == "alias_of":
            continue
        adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)
    for key in adjacency:
        adjacency[key] = sorted(set(adjacency[key]))

    visited: set[str] = set()
    stack: set[str] = set()

    def dfs(node_id: str) -> bool:
        visited.add(node_id)
        stack.add(node_id)
        for neighbor in adjacency.get(node_id, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in stack:
                return True
        stack.remove(node_id)
        return False

    for node in sorted(adjacency):
        if node not in visited and dfs(node):
            issues.append(
                GraphValidationIssue(
                    issue_code="CYCLE_DETECTED",
                    severity="error",
                    detail=f"Circular dependency detected near node {node}",
                    warehouse_row_id="graph:edges",
                )
            )
            break


def _duplicate_concepts(graph: KnowledgeGraph) -> list[tuple[str, str]]:
    def normalize(text: str) -> tuple[str, ...]:
        cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
        tokens = tuple(sorted(set([token for token in cleaned.split() if token not in {"and", "or", "the"}])))
        return tokens

    candidates = [node for node in graph.nodes if node.node_type in {"objective", "mechanism", "condition"}]
    duplicates: list[tuple[str, str]] = []
    for idx, left in enumerate(candidates):
        left_tokens = normalize(left.node_name)
        if not left_tokens:
            continue
        for right in candidates[idx + 1 :]:
            if left.node_type != right.node_type:
                continue
            right_tokens = normalize(right.node_name)
            if not right_tokens:
                continue
            intersection = len(set(left_tokens) & set(right_tokens))
            union = len(set(left_tokens) | set(right_tokens))
            jaccard = (intersection / union) if union else 0.0
            if jaccard >= 0.75:
                duplicates.append((left.node_id, right.node_id))
    return sorted(set(duplicates))


def _graph_statistics(graph: KnowledgeGraph, duplicates: list[tuple[str, str]]) -> GraphStatistics:
    node_types = [row.node_type for row in graph.nodes]
    missing_evidence = sum(
        1
        for edge in graph.edges
        if not edge.scientific_quote.strip() or not edge.paper_name.strip() or not edge.paper_link.strip()
    )
    average_evidence = (len(graph.evidence_edges) / float(len(graph.edges))) if graph.edges else 0.0
    disconnected = _count_components(graph)
    return GraphStatistics(
        total_nodes=len(graph.nodes),
        total_edges=len(graph.edges),
        conditions=node_types.count("condition"),
        objectives=node_types.count("objective"),
        mechanisms=node_types.count("mechanism"),
        ingredients=node_types.count("ingredient"),
        sources=node_types.count("source"),
        recipes=node_types.count("recipe"),
        products=node_types.count("product"),
        average_evidence_per_edge=round(average_evidence, 6),
        missing_evidence_edges=missing_evidence,
        duplicate_concepts=len(duplicates),
        disconnected_components=disconnected,
    )


def _count_components(graph: KnowledgeGraph) -> int:
    adjacency: dict[str, set[str]] = {row.node_id: set() for row in graph.nodes}
    for edge in graph.edges:
        adjacency.setdefault(edge.source_node_id, set()).add(edge.target_node_id)
        adjacency.setdefault(edge.target_node_id, set()).add(edge.source_node_id)
    seen: set[str] = set()
    components = 0
    for node_id in sorted(adjacency):
        if node_id in seen:
            continue
        components += 1
        stack = [node_id]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(sorted(adjacency.get(current, set()) - seen))
    return components
