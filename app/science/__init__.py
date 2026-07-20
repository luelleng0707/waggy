"""Phase 4 scientific knowledge graph & explainability — deterministic only."""

from __future__ import annotations

from app.science.audit import ScientificAudit, write_scientific_audit
from app.science.builder import KnowledgeGraphBuilder
from app.science.confidence import (
    CoverageConfidence,
    EvidenceConfidence,
    ExecutionConfidence,
    RecommendationConfidence,
    StudyQuality,
    build_confidence_bundle,
)
from app.science.coverage import KnowledgeCoverageReport
from app.science.diff_engine import ScientificDiffEngine
from app.science.explanations import (
    DeveloperExplanation,
    ScientificExplanation,
    build_formula_explanations,
    build_recommendation_chain,
)
from app.science.graph import KnowledgeGraph
from app.science.models import EvidenceObject
from app.science.repository import GraphRepository
from app.science.validator import DataValidator
from app.science.versioning import VersionedScience

__all__ = [
    "KnowledgeGraph",
    "KnowledgeGraphBuilder",
    "GraphRepository",
    "EvidenceObject",
    "ScientificExplanation",
    "DeveloperExplanation",
    "ExecutionConfidence",
    "EvidenceConfidence",
    "CoverageConfidence",
    "StudyQuality",
    "RecommendationConfidence",
    "build_confidence_bundle",
    "build_formula_explanations",
    "build_recommendation_chain",
    "ScientificAudit",
    "write_scientific_audit",
    "KnowledgeCoverageReport",
    "VersionedScience",
    "DataValidator",
    "ScientificDiffEngine",
]
