"""
Master PPIE wellness agent orchestrator.

Phase 3: delegates to AssessmentAgent / FormulaGraph.
Legacy stage orchestration removed from the hot path; formulas remain wrapped
inside nodes (health_risk, ingredient_engine, package path via assembler).
"""

from __future__ import annotations

import logging
from typing import Any

from app.agent.assessment_agent import AssessmentAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, bootstrap

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
        data_dir: str = "data",
        *,
        backend: str = "legacy",
        warehouse_root: str | None = None,
        repo: DataRepository | None = None,
    ):
        """
        backend: "legacy" (default) reads data/ via DataPlatform.
                 "warehouse" reads via WarehouseRepository adapters (Phase 2).
        repo: optional pre-built repository (tests). Formulas unchanged either way.
        """
        if repo is not None:
            self.repo = repo
        elif backend == "warehouse":
            from app.data.warehouse import WarehouseRepository

            self.repo = WarehouseRepository(
                data_dir, warehouse_root=warehouse_root, strict=True
            )
        else:
            bootstrap(data_dir, strict=True)
            self.repo = DataRepository(data_dir)
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
