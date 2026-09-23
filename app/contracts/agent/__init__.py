"""Canonical agent-facing domain contracts (Ω11)."""

from __future__ import annotations

from app.contracts.agent.analysis import CanonicalAnalysis
from app.contracts.agent.bundles import BundleSearchResult
from app.contracts.agent.context import AgentContext
from app.contracts.agent.errors import ToolError, ToolErrorCode
from app.contracts.agent.evidence import ScientificEvidence, ScientificFact
from app.contracts.agent.evidence_profile import EvidenceProfile, EvidenceRecord, EvidenceSeries
from app.contracts.agent.evidence_report import (
    EvidenceDelta,
    EvidenceReport,
    EvidenceReportSeries,
    EvidenceTimelinePoint,
)
from app.contracts.agent.health import HealthAnalysisResult
from app.contracts.agent.input import CanonicalDogInput, FieldValue, InputState
from app.contracts.agent.nutrition import NutritionAnalysisResult
from app.contracts.agent.observations import Observation
from app.contracts.agent.products import BusinessConfiguration, ProductRecord
from app.contracts.agent.survey import ProfessionalSurveyAnswer, ProfessionalSurveyResponse
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.registry import FUTURE_TOOL_REGISTRY, ToolRegistryEntry
from app.contracts.agent.report import ReportProjection
from app.contracts.agent.versions import AGENT_CONTRACT_SCHEMA_VERSION, VersionStamp

__all__ = [
    "AGENT_CONTRACT_SCHEMA_VERSION",
    "AgentContext",
    "BusinessConfiguration",
    "BundleSearchResult",
    "CanonicalAnalysis",
    "CanonicalDogInput",
    "EvidenceDelta",
    "EvidenceProfile",
    "EvidenceRecord",
    "EvidenceReport",
    "EvidenceReportSeries",
    "EvidenceSeries",
    "EvidenceTimelinePoint",
    "FUTURE_TOOL_REGISTRY",
    "FieldValue",
    "HealthAnalysisResult",
    "InputState",
    "NutritionAnalysisResult",
    "Observation",
    "ProductRecord",
    "ProfessionalSurveyAnswer",
    "ProfessionalSurveyResponse",
    "ProvenanceRecord",
    "ReportProjection",
    "ScientificEvidence",
    "ScientificFact",
    "ToolError",
    "ToolErrorCode",
    "ToolRegistryEntry",
    "VersionStamp",
]
