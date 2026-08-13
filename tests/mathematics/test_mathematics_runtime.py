from __future__ import annotations

from copy import deepcopy

from repository.mathematics.formulas import FORMULA_REGISTRY
from repository.mathematics.runtime import ScientificMathematicsRuntime
from repository.models.runtime import EvidenceGraph


def _graph() -> EvidenceGraph:
    nodes = (
        {"node_id": "COND_NODE_1", "node_type": "condition", "condition_id": "COND_HIP", "condition_name": "Hip Dysplasia"},
        {"node_id": "COND_NODE_2", "node_type": "condition", "condition_id": "COND_DIA", "condition_name": "Diabetes"},
        {"node_id": "SRC_1", "node_type": "trait"},
        {"node_id": "SRC_2", "node_type": "environment"},
        {"node_id": "SRC_3", "node_type": "observed"},
        {"node_id": "SRC_4", "node_type": "interaction"},
        {"node_id": "SRC_5", "node_type": "trait"},
        {"node_id": "SRC_6", "node_type": "observed"},
    )
    citations = (
        {"citation_id": "C1", "paper_name": "Hip Paper", "paper_link": "https://example.org/hip", "scientific_quote": "Observed hip prevalence quote."},
        {"citation_id": "C2", "paper_name": "Trait Paper", "paper_link": "https://example.org/trait", "scientific_quote": "Large trait association quote."},
        {"citation_id": "C3", "paper_name": "Env Paper", "paper_link": "https://example.org/env", "scientific_quote": "Cold climate association quote."},
        {"citation_id": "C4", "paper_name": "Interaction Paper", "paper_link": "https://example.org/int", "scientific_quote": "Interaction factor quote."},
    )
    edges = (
        {"edge_id": "E1", "from_node_id": "SRC_3", "to_node_id": "COND_NODE_1", "evidence_type": "observed", "value_number": "0.18", "observed_value": "0.18", "citation_id": "C1"},
        {"edge_id": "E2", "from_node_id": "SRC_1", "to_node_id": "COND_NODE_1", "evidence_type": "trait", "value_number": "0.06", "citation_id": "C2"},
        {"edge_id": "E3", "from_node_id": "SRC_2", "to_node_id": "COND_NODE_1", "evidence_type": "environment", "value_number": "0.05", "citation_id": "C3"},
        {"edge_id": "E4", "from_node_id": "SRC_4", "to_node_id": "COND_NODE_1", "evidence_type": "interaction", "value_number": "0.04", "factor": "1.15", "citation_id": "C4"},
        {"edge_id": "E5", "from_node_id": "SRC_6", "to_node_id": "COND_NODE_2", "evidence_type": "observed", "value_number": "0.05", "observed_value": "0.05", "citation_id": "C1"},
        {"edge_id": "E6", "from_node_id": "SRC_5", "to_node_id": "COND_NODE_2", "evidence_type": "trait", "value_number": "0.22", "citation_id": "C2"},
    )
    return EvidenceGraph(dog_id="DOG_MATH", nodes=nodes, edges=edges, citations=citations)


def test_mathematics_runtime_is_deterministic():
    runtime = ScientificMathematicsRuntime()
    graph = _graph()
    first = runtime.run(graph)
    second = runtime.run(graph)
    assert first.assessments == second.assessments
    assert len(first.assessments) > 0


def test_identical_input_does_not_mutate_graph():
    runtime = ScientificMathematicsRuntime()
    graph = _graph()
    before = deepcopy(graph)
    _ = runtime.run(graph)
    assert graph == before


def test_formula_registry_and_traces_are_versioned():
    runtime = ScientificMathematicsRuntime()
    result = runtime.run(_graph())
    formula_ids = {formula_id for assessment in result.assessments for formula_id in assessment.supporting_formulas}
    assert {"MAT-1001", "MAT-1002", "MAT-1003", "MAT-1004", "MAT-1005", "MAT-1006", "MAT-1007", "MAT-1008"}.issubset(formula_ids)
    for formula_id in formula_ids:
        assert formula_id in FORMULA_REGISTRY


def test_assessment_fields_have_confidence_uncertainty_novelty_priority():
    runtime = ScientificMathematicsRuntime()
    assessment = runtime.run(_graph()).assessments[0]
    assert assessment.estimated_prevalence >= 0.0
    assert 0.0 <= assessment.confidence <= 100.0
    assert 0.0 <= assessment.agreement <= 100.0
    assert assessment.upper_bound >= assessment.lower_bound
    assert assessment.priority >= 0.0
    assert assessment.novelty >= 0.0


def test_backward_compatibility_default_equals_v1_formula_config():
    graph = _graph()
    default_runtime = ScientificMathematicsRuntime()
    explicit_v1_runtime = ScientificMathematicsRuntime(formula_version_overrides={"MAT-1005": "v1.0"})
    default_output = default_runtime.run(graph).assessments
    explicit_output = explicit_v1_runtime.run(graph).assessments
    assert default_output == explicit_output
