"""Graph nodes — wrap existing stage/engine functions (no math changes)."""

from __future__ import annotations

from app.agent.nodes.activity_node import ActivityNode
from app.agent.nodes.assessment_node import AssessmentNode
from app.agent.nodes.biology_node import BiologyNode
from app.agent.nodes.breed_node import BreedNode
from app.agent.nodes.confidence_node import ConfidenceNode
from app.agent.nodes.epidemiology_node import EpidemiologyNode
from app.agent.nodes.evidence_node import EvidenceNode
from app.agent.nodes.export_node import ExportNode
from app.agent.nodes.grooming_node import GroomingNode
from app.agent.nodes.ingredient_node import IngredientNode
from app.agent.nodes.nutrition_node import NutritionNode
from app.agent.nodes.package_node import PackageNode
from app.agent.nodes.product_node import ProductNode
from app.agent.nodes.profile_node import ProfileNode
from app.agent.nodes.report_node import ReportNode
from app.agent.nodes.risk_node import RiskNode
from app.agent.nodes.trace_node import TraceNode
from app.agent.nodes.validation_node import ValidationNode

__all__ = [
    "ProfileNode",
    "BreedNode",
    "BiologyNode",
    "RiskNode",
    "EpidemiologyNode",
    "ActivityNode",
    "GroomingNode",
    "NutritionNode",
    "IngredientNode",
    "ProductNode",
    "PackageNode",
    "AssessmentNode",
    "ReportNode",
    "ConfidenceNode",
    "EvidenceNode",
    "ValidationNode",
    "TraceNode",
    "ExportNode",
]


def default_nodes():
    """Canonical Phase 3 graph membership (dependency order enforced by FormulaGraph)."""
    return [
        ProfileNode(),
        BreedNode(),
        BiologyNode(),
        RiskNode(),
        EpidemiologyNode(),
        ActivityNode(),
        GroomingNode(),
        NutritionNode(),
        IngredientNode(),
        ProductNode(),
        PackageNode(),
        AssessmentNode(),
        ReportNode(),
        ConfidenceNode(),
        EvidenceNode(),
        ValidationNode(),
        TraceNode(),
        ExportNode(),
    ]
