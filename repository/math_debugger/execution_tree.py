"""Build execution tree for condition-level formula chains."""

from __future__ import annotations

from .models import ExecutionTree, ExecutionTreeNode, FormulaTrace


def build_execution_tree(formula_traces: tuple[FormulaTrace, ...]) -> ExecutionTree:
    if not formula_traces:
        root = ExecutionTreeNode(node_id="root", title="Execution", value="NO_EVIDENCE", children=tuple())
        return ExecutionTree(root_node_id="root", nodes=(root,))

    nodes: list[ExecutionTreeNode] = []
    root_children = []
    grouped: dict[str, list[FormulaTrace]] = {}
    for trace in formula_traces:
        condition_id = trace.trace_id.split(":")[0]
        grouped.setdefault(condition_id, []).append(trace)

    for condition_id in sorted(grouped):
        condition_node_id = f"condition:{condition_id}"
        child_ids = []
        for item in grouped[condition_id]:
            formula_node_id = f"formula:{item.trace_id}"
            child_ids.append(formula_node_id)
            nodes.append(
                ExecutionTreeNode(
                    node_id=formula_node_id,
                    title=f"{item.formula_id}:{item.formula_version}",
                    value=f"{item.output_variable}={item.output_value}",
                    children=tuple(),
                )
            )
        nodes.append(
            ExecutionTreeNode(
                node_id=condition_node_id,
                title=f"Condition:{condition_id}",
                value="FORMULA_CHAIN",
                children=tuple(child_ids),
            )
        )
        root_children.append(condition_node_id)

    root = ExecutionTreeNode(node_id="root", title="Execution", value="FORMULA_PIPELINE", children=tuple(root_children))
    return ExecutionTree(root_node_id="root", nodes=tuple([root] + sorted(nodes, key=lambda row: row.node_id)))
