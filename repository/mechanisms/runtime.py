"""Ω5 deterministic biological mechanism runtime."""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.reasoning.models import ConditionAssessment
from repository.warehouse import WarehouseInterface

from .formulas import as_float
from .interfaces import DosePlanner, InteractionAnalyzer, MechanismPlanner, MechanismResolver, MechanismTraceBuilder
from .models import (
    BiologicalObjective,
    DoseTarget,
    InteractionFinding,
    InteractionReport,
    MechanismConditionLink,
    MechanismNeed,
    MechanismPlan,
    MechanismRuntimeResult,
    MechanismRuntimeTrace,
    StageMechanismTrace,
)


class DeterministicMechanismTraceBuilder:
    def build(
        self,
        stage_name: str,
        execution_time_ms: float,
        formula_ids: tuple[str, ...],
        warehouse_rows_used: tuple[str, ...],
        input_summary: str,
        output_summary: str,
        warnings: tuple[str, ...] = (),
    ) -> StageMechanismTrace:
        return StageMechanismTrace(
            stage_name=stage_name,
            execution_time_ms=execution_time_ms,
            formula_ids=tuple(sorted(set(formula_ids))),
            warehouse_rows_used=tuple(sorted(set(warehouse_rows_used))),
            input_summary=input_summary,
            output_summary=output_summary,
            warnings=warnings,
        )


class WarehouseBackedMechanismResolver:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[MechanismNeed, ...]:
        mechanisms = self.warehouse.load_dataset("mechanisms.mechanisms")
        condition_map = self.warehouse.load_dataset("mechanisms.condition_mechanisms")

        mechanism_rows = {
            str(row["mechanism_id"]).strip(): row
            for _, row in mechanisms.iterrows()
            if str(row.get("mechanism_id", "")).strip()
        }
        by_condition: dict[str, list[dict[str, str]]] = {}
        for _, row in condition_map.iterrows():
            condition_id = str(row.get("condition_id", "")).strip()
            if not condition_id:
                continue
            by_condition.setdefault(condition_id, []).append({k: str(v) for k, v in row.items()})

        needs: list[MechanismNeed] = []
        for assessment in sorted(assessments, key=lambda item: item.condition_id):
            relation_rows = by_condition.get(assessment.condition_id, [])
            for row in sorted(relation_rows, key=lambda item: str(item.get("mechanism_id", ""))):
                mechanism_id = str(row.get("mechanism_id", "")).strip()
                mechanism_row = mechanism_rows.get(mechanism_id, {})
                mechanism_name = str(mechanism_row.get("mechanism_name", mechanism_id)).strip() or mechanism_id
                description = str(mechanism_row.get("description", "")).strip()
                weight = as_float(row.get("importance_weight", 0))
                contribution = (assessment.estimated_prevalence * weight) / 100.0
                objective = BiologicalObjective(
                    objective_id=f"OBJ_{mechanism_id}",
                    objective_name=f"Support {mechanism_name.lower()}",
                    rationale="Objective deterministically derived from mechanism catalog row.",
                )
                needs.append(
                    MechanismNeed(
                        mechanism_id=mechanism_id,
                        mechanism_name=mechanism_name,
                        description=description,
                        objective=objective,
                        supporting_conditions=(
                            MechanismConditionLink(
                                condition_id=assessment.condition_id,
                                condition_name=assessment.condition_name,
                                importance_weight=weight,
                                scientific_quote=str(row.get("scientific_quote", "")).strip(),
                                paper_name=str(row.get("paper_name", "")).strip(),
                                paper_link=str(row.get("paper_link", "")).strip(),
                            ),
                        ),
                        aggregate_importance=contribution,
                        formula_ids_used=("OBJ-001", "MEC-201"),
                        warehouse_rows_used=(
                            f"mechanisms.condition_mechanisms:{assessment.condition_id}:{mechanism_id}",
                            f"mechanisms.mechanisms:{mechanism_id}",
                        ),
                    )
                )
        return tuple(needs)


class DeterministicMechanismPlanner:
    def plan(self, needs: tuple[MechanismNeed, ...]) -> tuple[MechanismPlan, ...]:
        grouped: dict[str, list[MechanismNeed]] = {}
        for need in needs:
            grouped.setdefault(need.mechanism_id, []).append(need)

        plans: list[MechanismPlan] = []
        for mechanism_id in sorted(grouped):
            group = grouped[mechanism_id]
            importance = sum(item.aggregate_importance for item in group)
            papers: set[str] = set()
            quotes: list[str] = []
            conditions: list[str] = []
            formula_ids: set[str] = {"MEC-202"}
            for item in group:
                formula_ids.update(item.formula_ids_used)
                for link in item.supporting_conditions:
                    conditions.append(link.condition_name)
                    if link.paper_name:
                        papers.add(link.paper_name)
                    if link.scientific_quote:
                        quotes.append(link.scientific_quote)
            plans.append(
                MechanismPlan(
                    mechanism_id=mechanism_id,
                    mechanism=group[0].mechanism_name,
                    objective=group[0].objective.objective_name,
                    supporting_conditions=tuple(sorted(set(conditions))),
                    importance=round(importance, 6),
                    supporting_papers=tuple(sorted(papers)),
                    supporting_quotes=tuple(dict.fromkeys(quotes)),
                    formula_ids_used=tuple(sorted(formula_ids)),
                    dose_formula_ids=("DOS-301", "DOS-302"),
                )
            )
        plans.sort(key=lambda item: (-item.importance, item.mechanism_id))
        return tuple(plans)


class DeterministicDosePlanner:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def plan(
        self,
        mechanism_plan: tuple[MechanismPlan, ...],
        assessments: tuple[ConditionAssessment, ...],
        profile_context: dict[str, str | float] | None = None,
    ) -> tuple[DoseTarget, ...]:
        profile_context = profile_context or {}
        ingredient_mechanisms = self.warehouse.load_dataset("mechanisms.ingredient_mechanisms")
        dose_response = self.warehouse.load_dataset("mechanisms.dose_response")

        mechanism_importance = {item.mechanism_id: item.importance for item in mechanism_plan}
        if not mechanism_importance:
            return tuple()

        avg_prevalence = 0.0
        if assessments:
            avg_prevalence = sum(item.estimated_prevalence for item in assessments) / float(len(assessments))
        condition_scalar = 1.0 + min(0.25, avg_prevalence / 400.0)
        weight_kg = as_float(profile_context.get("weight_kg", 10.0))
        if weight_kg <= 0.0:
            weight_kg = 10.0
        life_stage = str(profile_context.get("life_stage", "")).strip().lower()
        activity = str(profile_context.get("activity", "")).strip().lower()
        climate = str(profile_context.get("climate", "")).strip().lower()

        life_stage_factor = {"puppy": 1.1, "adult": 1.0, "senior": 0.95}.get(life_stage, 1.0)
        activity_factor = {"low": 0.95, "medium": 1.0, "high": 1.08}.get(activity, 1.0)
        environment_factor = 1.05 if climate in {"cold", "very_cold", "hot", "very_hot"} else 1.0
        context_scalar = life_stage_factor * activity_factor * environment_factor * condition_scalar

        dose_rows_by_ingredient: dict[str, dict[str, str]] = {}
        for _, row in dose_response.iterrows():
            ingredient_id = str(row.get("ingredient", "")).strip()
            if not ingredient_id:
                continue
            if ingredient_id not in dose_rows_by_ingredient:
                dose_rows_by_ingredient[ingredient_id] = {k: str(v) for k, v in row.items()}

        ingredient_rollup: dict[str, dict[str, object]] = {}
        for _, row in ingredient_mechanisms.iterrows():
            mechanism_id = str(row.get("mechanism_id", "")).strip()
            ingredient_id = str(row.get("ingredient_id", "")).strip()
            if not ingredient_id or mechanism_id not in mechanism_importance:
                continue
            effect_size = as_float(row.get("effect_size", 0))
            demand = mechanism_importance[mechanism_id] * (effect_size / 100.0)
            bucket = ingredient_rollup.setdefault(
                ingredient_id,
                {
                    "demand": 0.0,
                    "papers": set(),
                    "quotes": [],
                    "mechanisms": set(),
                },
            )
            bucket["demand"] = float(bucket["demand"]) + demand
            if str(row.get("paper_name", "")).strip():
                bucket["papers"].add(str(row.get("paper_name", "")).strip())
            if str(row.get("scientific_quote", "")).strip():
                bucket["quotes"].append(str(row.get("scientific_quote", "")).strip())
            bucket["mechanisms"].add(mechanism_id)

        targets: list[DoseTarget] = []
        for ingredient_id in sorted(ingredient_rollup):
            response_row = dose_rows_by_ingredient.get(ingredient_id)
            if response_row is None:
                continue
            response_dose = as_float(response_row.get("dose", 0))
            response_unit = str(response_row.get("unit", "")).strip() or "per_day"

            baseline_amount = response_dose * weight_kg if response_unit.endswith("mg_per_kg_day") else response_dose
            demand = float(ingredient_rollup[ingredient_id]["demand"])
            mechanism_scalar = max(0.5, min(2.0, 1.0 + demand / 10.0))
            desired_amount = baseline_amount * mechanism_scalar * context_scalar

            papers = set(ingredient_rollup[ingredient_id]["papers"])
            quotes = list(ingredient_rollup[ingredient_id]["quotes"])
            if str(response_row.get("paper", "")).strip():
                papers.add(str(response_row.get("paper", "")).strip())
            if str(response_row.get("quote", "")).strip():
                quotes.append(str(response_row.get("quote", "")).strip())

            targets.append(
                DoseTarget(
                    ingredient_id=ingredient_id,
                    ingredient_name=ingredient_id,
                    desired_amount=round(desired_amount, 6),
                    unit=response_unit.replace("_per_kg_day", "_per_day"),
                    formula_id="DOS-302",
                    reasoning=(
                        "Target dose uses dose_response baseline (DOS-301), "
                        "then scales by mechanism demand and profile factors (DOS-302)."
                    ),
                    papers=tuple(sorted(papers)),
                    quotes=tuple(dict.fromkeys(quotes)),
                    mechanisms_supported=tuple(sorted(ingredient_rollup[ingredient_id]["mechanisms"])),
                )
            )
        return tuple(targets)


class DeterministicInteractionAnalyzer:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def analyze(self, dose_targets: tuple[DoseTarget, ...]) -> InteractionReport:
        if not dose_targets:
            return InteractionReport()

        interactions = self.warehouse.load_dataset("mechanisms.mechanism_interactions")
        synergies = self.warehouse.load_dataset("mechanisms.mechanism_synergies")
        conflicts = self.warehouse.load_dataset("mechanisms.mechanism_conflicts")
        absorption = self.warehouse.load_dataset("mechanisms.absorption_factors")

        ingredient_ids = {item.ingredient_id for item in dose_targets}

        def _row_to_finding(row: dict[str, str], finding_type: str) -> InteractionFinding:
            return InteractionFinding(
                finding_type=finding_type,
                ingredient_a=str(row.get("ingredient_A", "")).strip() or str(row.get("ingredient_id", "")).strip(),
                ingredient_b=str(row.get("ingredient_B", "")).strip() or str(row.get("required_factor", "")).strip(),
                effect_strength=as_float(row.get("effect_strength", row.get("effect_size", 0))),
                scientific_quote=str(row.get("scientific_quote", row.get("quote", ""))).strip(),
                paper_name=str(row.get("paper_name", row.get("paper", ""))).strip(),
                paper_link=str(row.get("paper_link", row.get("link", ""))).strip(),
            )

        positive: list[InteractionFinding] = []
        negatives: list[InteractionFinding] = []
        enhancers: list[InteractionFinding] = []
        inhibitors: list[InteractionFinding] = []

        for frame, default_type in (
            (synergies, "positive_synergy"),
            (conflicts, "negative_interaction"),
            (interactions, ""),
        ):
            for _, row in frame.iterrows():
                row_data = {k: str(v) for k, v in row.items()}
                a = str(row_data.get("ingredient_A", "")).strip()
                b = str(row_data.get("ingredient_B", "")).strip()
                interaction_type = str(row_data.get("interaction_type", default_type)).strip().lower()
                if a not in ingredient_ids or b not in ingredient_ids:
                    continue
                finding = _row_to_finding(row_data, interaction_type)
                if interaction_type in {"positive_synergy", "positive", "synergy"}:
                    positive.append(finding)
                elif interaction_type in {"absorption_enhancer", "enhanced_by"}:
                    enhancers.append(finding)
                elif interaction_type in {"absorption_inhibitor", "inhibited_by"}:
                    inhibitors.append(finding)
                else:
                    negatives.append(finding)

        missing_cofactors: list[str] = []
        for _, row in absorption.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            ingredient_id = str(row_data.get("ingredient_id", "")).strip()
            required_factor = str(row_data.get("required_factor", "")).strip()
            interaction_type = str(row_data.get("interaction_type", "")).strip().lower()
            if ingredient_id not in ingredient_ids or not required_factor:
                continue

            if required_factor.startswith("ING_") and required_factor in ingredient_ids:
                if interaction_type in {"enhanced_by", "requires"}:
                    enhancers.append(_row_to_finding(row_data, "absorption_enhancer"))
                elif interaction_type in {"inhibited_by", "competes_with"}:
                    inhibitors.append(_row_to_finding(row_data, "absorption_inhibitor"))
                continue

            if interaction_type in {"requires", "enhanced_by"}:
                missing_cofactors.append(
                    f"{ingredient_id} requires {required_factor} ({interaction_type})"
                )

        return InteractionReport(
            positive_synergies=tuple(sorted(positive, key=lambda item: (item.ingredient_a, item.ingredient_b))),
            negative_interactions=tuple(sorted(negatives, key=lambda item: (item.ingredient_a, item.ingredient_b))),
            missing_cofactors=tuple(sorted(set(missing_cofactors))),
            absorption_enhancers=tuple(sorted(enhancers, key=lambda item: (item.ingredient_a, item.ingredient_b))),
            absorption_inhibitors=tuple(sorted(inhibitors, key=lambda item: (item.ingredient_a, item.ingredient_b))),
        )


@dataclass(frozen=True)
class BiologicalMechanismRuntime:
    warehouse: WarehouseInterface
    mechanism_resolver: MechanismResolver | None = None
    mechanism_planner: MechanismPlanner | None = None
    dose_planner: DosePlanner | None = None
    interaction_analyzer: InteractionAnalyzer | None = None
    trace_builder: MechanismTraceBuilder | None = None

    def __post_init__(self) -> None:
        if self.mechanism_resolver is None:
            object.__setattr__(self, "mechanism_resolver", WarehouseBackedMechanismResolver(self.warehouse))
        if self.mechanism_planner is None:
            object.__setattr__(self, "mechanism_planner", DeterministicMechanismPlanner())
        if self.dose_planner is None:
            object.__setattr__(self, "dose_planner", DeterministicDosePlanner(self.warehouse))
        if self.interaction_analyzer is None:
            object.__setattr__(self, "interaction_analyzer", DeterministicInteractionAnalyzer(self.warehouse))
        if self.trace_builder is None:
            object.__setattr__(self, "trace_builder", DeterministicMechanismTraceBuilder())

    def run(
        self,
        assessments: tuple[ConditionAssessment, ...],
        profile_context: dict[str, str | float] | None = None,
    ) -> MechanismRuntimeResult:
        trace_items: list[StageMechanismTrace] = []
        run_id = uuid.uuid4().hex

        def _run(stage_name: str, fn, *args):
            started = time.perf_counter()
            result = fn(*args)
            elapsed = (time.perf_counter() - started) * 1000.0
            formula_ids: set[str] = set()
            warehouse_rows: set[str] = set()

            if isinstance(result, tuple):
                for item in result:
                    if hasattr(item, "formula_ids_used"):
                        formula_ids.update(getattr(item, "formula_ids_used"))
                    if hasattr(item, "formula_id"):
                        formula_ids.add(getattr(item, "formula_id"))
                    if hasattr(item, "warehouse_rows_used"):
                        warehouse_rows.update(getattr(item, "warehouse_rows_used"))
            if isinstance(result, InteractionReport):
                formula_ids.update({"INT-401", "INT-402"})

            trace_items.append(
                self.trace_builder.build(  # type: ignore[union-attr]
                    stage_name=stage_name,
                    execution_time_ms=elapsed,
                    formula_ids=tuple(formula_ids),
                    warehouse_rows_used=tuple(warehouse_rows),
                    input_summary=",".join(type(arg).__name__ for arg in args),
                    output_summary=type(result).__name__,
                )
            )
            return result

        needs = _run("Mechanism Network", self.mechanism_resolver.resolve, assessments)  # type: ignore[union-attr]
        mechanism_plan = _run("Mechanism Planning", self.mechanism_planner.plan, needs)  # type: ignore[union-attr]
        dose_targets = _run(
            "Dose Planning",
            self.dose_planner.plan,  # type: ignore[union-attr]
            mechanism_plan,
            assessments,
            profile_context or {},
        )
        interaction_report = _run(
            "Interaction Analysis",
            self.interaction_analyzer.analyze,  # type: ignore[union-attr]
            dose_targets,
        )

        interaction_notes = []
        if interaction_report.positive_synergies:
            interaction_notes.append(f"positive_synergies={len(interaction_report.positive_synergies)}")
        if interaction_report.negative_interactions:
            interaction_notes.append(f"negative_interactions={len(interaction_report.negative_interactions)}")
        if interaction_report.missing_cofactors:
            interaction_notes.append(f"missing_cofactors={len(interaction_report.missing_cofactors)}")

        enriched_plan = tuple(
            MechanismPlan(
                mechanism_id=item.mechanism_id,
                mechanism=item.mechanism,
                objective=item.objective,
                supporting_conditions=item.supporting_conditions,
                importance=item.importance,
                supporting_papers=item.supporting_papers,
                supporting_quotes=item.supporting_quotes,
                formula_ids_used=item.formula_ids_used,
                dose_formula_ids=item.dose_formula_ids,
                interaction_notes=tuple(interaction_notes),
            )
            for item in mechanism_plan
        )

        return MechanismRuntimeResult(
            mechanism_plan=enriched_plan,
            dose_targets=dose_targets,
            interaction_report=interaction_report,
            trace=MechanismRuntimeTrace(run_id=run_id, stages=tuple(trace_items)),
        )
