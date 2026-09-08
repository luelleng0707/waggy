"""Future generate_report output. Projection only — not a reasoner."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.agent.enums import DomainKind
from app.contracts.agent.versions import VersionStamp


class ReportProjection(BaseModel):
    """Placeholder for the existing presentation/report builders.

    Ω11 does not call ``build_clinical_report`` or workbench adapters.
    This model records that a report is a projection of a completed analysis.
    """

    model_config = ConfigDict(extra="forbid")

    domain: DomainKind = DomainKind.PROJECTION
    capability: str = "generate_report"
    analysis_id: str | None = None
    source_builders: list[str] = Field(
        default_factory=lambda: [
            "app.data.clinical_report_builder.build_clinical_report",
            "app.presentation.adapter.build_workbench_presentations",
        ]
    )
    versions: VersionStamp
    note: str = (
        "Projection of canonical analysis. Does not infer health, "
        "select products, or rank bundles."
    )
