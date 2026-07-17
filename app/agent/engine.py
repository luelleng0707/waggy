"""Master PPIE wellness agent orchestrator (Stages 1-8)."""

from __future__ import annotations

import logging
from typing import Any

from app.agent.state import (
    AgentPipelineState,
    DogProfileInput,
    PipelineTraceEntry,
)
from app.agent.stages import (
    run_biological_stage,
    run_epidemiology_stage,
    run_nutrition_stage,
    run_optimization_stage,
)
from app.agent.stages.health_risk import compute_risks
from app.agent.response_assembler import assemble_frontend_response
from app.agent.utils import DataRepository

logger = logging.getLogger(__name__)


class PPIEWellnessAgent:
    """
    Deterministic agent pipeline:
    Biology -> Health Risk -> Management -> Nutrition -> Products -> Feeding Plan
    """

    def __init__(self, data_dir: str = "data"):
        self.repo = DataRepository(data_dir)

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
        state = AgentPipelineState(profile=profile)

        # Stage 1-2: Biological trait resolution
        biology, t1 = run_biological_stage(self.repo, profile)
        state.biology = biology
        state.trace.append(t1)

        # Stage 2b: JS-parity health risk ranking (confidence, mixed-breed, groomer)
        health_risk = compute_risks(self.repo, profile)
        state.trace.append(
            PipelineTraceEntry(
                stage="health_risk",
                message="Computed trait/overlap/benefit/significance risks (JS parity)",
                record_count=len(health_risk.get("risks") or []),
                metadata=health_risk.get("meta") or {},
            )
        )

        # Stage 3-4: Epidemiology CSV multipliers (legacy path; risks drive insights)
        epidemiology, t2 = run_epidemiology_stage(self.repo, profile, biology)
        # Prefer risk-ranked priorities for downstream lifestyle / nutrition ranking
        if health_risk.get("risks"):
            epidemiology = {
                **epidemiology,
                "priority_conditions": [
                    {
                        "condition": r.get("condition_name"),
                        "condition_key": r.get("condition_key"),
                        "prevalence": float(
                            r.get("risk_decimal")
                            or (float(r.get("risk_percent") or 0) / 100.0)
                        ),
                        "weighted_priority_score": float(
                            r.get("risk_decimal")
                            or (float(r.get("risk_percent") or 0) / 100.0)
                        ),
                        "risk_percent": r.get("risk_percent"),
                        "confidence_percent": r.get("confidence_percent"),
                    }
                    for r in health_risk["risks"]
                ],
            }
        state.epidemiology = epidemiology
        state.trace.append(t2)

        # Stage 5: Management / lifestyle mapping
        management, t3 = self._run_management_stage(epidemiology)
        state.management = management
        state.trace.append(t3)

        # Stage 6: Nutrition synthesis
        nutrition, t4 = run_nutrition_stage(self.repo, profile, epidemiology)
        state.nutrition = nutrition
        state.trace.append(t4)

        # Stage 7-8: Product optimization + feeding plan
        products, reports, t5 = run_optimization_stage(self.repo, profile, nutrition)
        state.products = products
        state.feeding_plan = products.get("feeding_plan", {})
        state.trace.append(t5)

        logger.info(
            "PPIE pipeline complete for %s | reports=%s risks=%s trace_steps=%s",
            profile.name,
            len(reports),
            len(health_risk.get("risks") or []),
            len(state.trace),
        )

        return assemble_frontend_response(
            profile=profile,
            biology=state.biology,
            epidemiology=state.epidemiology,
            nutrition=state.nutrition,
            reports=reports,
            feeding_plan=state.feeding_plan,
            management=state.management,
            pipeline_trace=[entry.model_dump() for entry in state.trace],
            repo=self.repo,
            health_risk=health_risk,
        )

    def _run_management_stage(self, epidemiology: dict[str, Any]) -> tuple[dict[str, Any], PipelineTraceEntry]:
        activities_df = self.repo.condition_activities()
        priorities = epidemiology.get("priority_conditions", [])
        lifestyle = []

        if not activities_df.empty and priorities:
            top_conditions = [p["condition"] for p in priorities[:10]]
            cond_col = "condition" if "condition" in activities_df.columns else "condition_name"
            hits = activities_df[activities_df[cond_col].isin(top_conditions)]
            lifestyle = hits.to_dict(orient="records")

        payload = {"lifestyle_requirements": lifestyle}
        trace = PipelineTraceEntry(
            stage="management",
            message="Mapped lifestyle interventions for ranked conditions",
            record_count=len(lifestyle),
        )
        logger.info("[Stage 5] management lifestyle rows=%s", len(lifestyle))
        return payload, trace
