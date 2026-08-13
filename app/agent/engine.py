"""
Master PPIE wellness agent orchestrator.

Phase 3: delegates to AssessmentAgent / FormulaGraph.
Phase Σ: Repository loads the canonical warehouse only (no adapters).
"""

from __future__ import annotations

import logging
from typing import Any

from app.agent.assessment_agent import AssessmentAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, bootstrap
from app.core.paths import clinical_root_str

logger = logging.getLogger(__name__)


class PPIEWellnessAgent:
    """
    Deterministic agent pipeline via FormulaGraph:

    Profile → Breed → Biology → Risk → Epidemiology → Activity → Nutrition →
    Ingredient → Product → Package → Assessment → Report → Validation →
    Trace → Export (legacy JSON)
    """

    def __init__(
        self,
        data_dir: str | None = None,
        *,
        backend: str = "canonical",
        warehouse_root: str | None = None,
        repo: DataRepository | None = None,
    ):
        """
        data_dir: defaults to resolve_clinical_root() (Phase Σ warehouse).
        backend: ignored (kept for API compatibility). Always uses DataRepository.
        warehouse_root: unused (Phase Σ adapters removed).
        repo: optional pre-built repository (tests).
        """
        root = data_dir if data_dir is not None else clinical_root_str()
        if repo is not None:
            self.repo = repo
        else:
            bootstrap(root, strict=True)
            self.repo = DataRepository(root)
        self.assessment_agent = AssessmentAgent(self.repo)

    def generate_reproducible_report_sync(
        self,
        profile: DogProfileInput,
    ) -> dict[str, Any]:
        """Synchronous entrypoint for Streamlit and scripts."""
        import asyncio

        return asyncio.run(self.generate_reproducible_report(profile))

    async def generate_reproducible_report(
        self,
        profile: DogProfileInput,
    ) -> dict[str, Any]:
        result = self.assessment_agent.assess(profile)
        analyze = result.to_analyze_dict()
        logger.info(
            "PPIE FormulaGraph complete for %s | risks=%s nodes=%s",
            profile.name,
            len((result.health or {}).get("risks") or []),
            len((result.trace or {}).get("execution") or []),
        )
        return analyze

    def assess(self, profile: DogProfileInput):
        """Typed AssessmentResult (Phase 3). Prefer generate_reproducible_report for API."""
        return self.assessment_agent.assess(profile)
