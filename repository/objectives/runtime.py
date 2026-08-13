"""Ω5.5 objective-network runtime: ConditionAssessment[] -> IngredientSourcePlan[]."""

from __future__ import annotations

from dataclasses import dataclass
import time
import uuid

from repository.mechanisms.models import MechanismPlan
from repository.reasoning.models import ConditionAssessment
from repository.sources.interfaces import BioavailabilityAnalyzer, IngredientSourceResolver, SourcePlanner
from repository.sources.runtime import (
    DeterministicBioavailabilityAnalyzer,
    WarehouseBackedIngredientSourceResolver,
    WarehouseBackedSourcePlanner,
)
from repository.warehouse import WarehouseInterface

from .formulas import as_float
from .interfaces import ObjectiveNetwork, ObjectivePlanner, ObjectiveResolver, ObjectiveTraceBuilder
from .models import (
    ObjectiveConditionLink,
    ObjectiveNetworkSummary,
    ObjectivePlan,
    ObjectiveRuntimeResult,
    ObjectiveRuntimeTrace,
    ObjectiveStageTrace,
)


class DeterministicObjectiveTraceBuilder:
    def build(
        self,
        stage_name: str,
        execution_time_ms: float,
        formula_ids: tuple[str, ...],
        warehouse_rows_used: tuple[str, ...],
        input_summary: str,
        output_summary: str,
    ) -> ObjectiveStageTrace:
        return ObjectiveStageTrace(
            stage_name=stage_name,
            execution_time_ms=execution_time_ms,
            formula_ids=tuple(sorted(set(formula_ids))),
            warehouse_rows_used=tuple(sorted(set(warehouse_rows_used))),
            input_summary=input_summary,
            output_summary=output_summary,
        )


class WarehouseBackedObjectiveResolver:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, assessments: tuple[ConditionAssessment, ...]) -> tuple[ObjectivePlan, ...]:
        objectives_table = self.warehouse.load_dataset("objectives.objectives")
        condition_objectives = self.warehouse.load_dataset("objectives.condition_objectives")

        objective_rows = {
            str(row.get("objective_id", "")).strip(): {k: str(v) for k, v in row.items()}
            for _, row in objectives_table.iterrows()
            if str(row.get("objective_id", "")).strip()
        }
        condition_map: dict[str, list[dict[str, str]]] = {}
        for _, row in condition_objectives.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            condition_id = row_data.get("condition_id", "").strip()
            if condition_id:
                condition_map.setdefault(condition_id, []).append(row_data)

        grouped: dict[str, dict[str, object]] = {}
        for assessment in sorted(assessments, key=lambda value: value.condition_id):
            for row in condition_map.get(assessment.condition_id, []):
                objective_id = row.get("objective_id", "").strip()
                if not objective_id:
                    continue
                objective_meta = objective_rows.get(objective_id, {})
                importance = as_float(row.get("importance", 0))
                contribution = assessment.estimated_prevalence * importance

                bucket = grouped.setdefault(
                    objective_id,
                    {
                        "name": objective_meta.get("objective_name", objective_id),
                        "description": objective_meta.get("objective_description", ""),
                        "priority": 0.0,
                        "conditions": [],
                        "papers": set(),
                        "quotes": [],
                        "rows": set(),
                    },
                )
                bucket["priority"] = float(bucket["priority"]) + contribution
                bucket["conditions"].append(
                    ObjectiveConditionLink(
                        condition_id=assessment.condition_id,
                        condition_name=assessment.condition_name,
                        condition_prevalence=assessment.estimated_prevalence,
                        importance=importance,
                        scientific_quote=row.get("scientific_quote", "").strip(),
                        paper_name=row.get("paper_name", "").strip(),
                        paper_link=row.get("paper_link", "").strip(),
                    )
                )
                if row.get("paper_name", "").strip():
                    bucket["papers"].add(row["paper_name"].strip())
                if row.get("scientific_quote", "").strip():
                    bucket["quotes"].append(row["scientific_quote"].strip())
                if objective_meta.get("paper_name", "").strip():
                    bucket["papers"].add(str(objective_meta["paper_name"]).strip())
                if objective_meta.get("scientific_quote", "").strip():
                    bucket["quotes"].append(str(objective_meta["scientific_quote"]).strip())
                bucket["rows"].add(f"objectives.condition_objectives:{assessment.condition_id}:{objective_id}")
                bucket["rows"].add(f"objectives.objectives:{objective_id}")

        plans: list[ObjectivePlan] = []
        for objective_id in sorted(grouped):
            bucket = grouped[objective_id]
            plans.append(
                ObjectivePlan(
                    objective_id=objective_id,
                    objective_name=str(bucket["name"]),
                    objective_description=str(bucket["description"]),
                    supporting_conditions=tuple(
                        sorted(bucket["conditions"], key=lambda item: (item.condition_id, -item.importance))
                    ),
                    objective_priority=round(float(bucket["priority"]), 6),
                    supporting_papers=tuple(sorted(bucket["papers"])),
                    supporting_quotes=tuple(dict.fromkeys(bucket["quotes"])),
                    formula_ids_used=("OBJ-501",),
                    warehouse_rows_used=tuple(sorted(bucket["rows"])),
                )
            )
        return tuple(plans)


class WarehouseBackedObjectivePlanner:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def plan(self, objectives: tuple[ObjectivePlan, ...]) -> tuple[ObjectivePlan, ...]:
        priorities = self.warehouse.load_dataset("objectives.objective_priorities")
        multipliers: dict[str, list[float]] = {}
        for _, row in priorities.iterrows():
            objective_id = str(row.get("objective_id", "")).strip()
            if not objective_id:
                continue
            multipliers.setdefault(objective_id, []).append(as_float(row.get("priority_multiplier", 1.0)))

        planned: list[ObjectivePlan] = []
        for objective in objectives:
            factors = multipliers.get(objective.objective_id, [1.0])
            multiplier = sum(factors) / float(len(factors))
            planned.append(
                ObjectivePlan(
                    objective_id=objective.objective_id,
                    objective_name=objective.objective_name,
                    objective_description=objective.objective_description,
                    supporting_conditions=objective.supporting_conditions,
                    objective_priority=round(objective.objective_priority * multiplier, 6),
                    supporting_papers=objective.supporting_papers,
                    supporting_quotes=objective.supporting_quotes,
                    formula_ids_used=tuple(sorted(set(objective.formula_ids_used + ("OBJ-504",)))),
                    warehouse_rows_used=objective.warehouse_rows_used
                    + (f"objectives.objective_priorities:{objective.objective_id}",),
                )
            )
        planned.sort(key=lambda item: (-item.objective_priority, item.objective_id))
        return tuple(planned)


class WarehouseBackedObjectiveNetwork:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def map(self, objectives: tuple[ObjectivePlan, ...]) -> ObjectiveNetworkSummary:
        objective_ids = {item.objective_id for item in objectives}
        synergies_table = self.warehouse.load_dataset("objectives.objective_synergies")
        conflicts_table = self.warehouse.load_dataset("objectives.objective_conflicts")

        synergies: list[str] = []
        conflicts: list[str] = []
        rows: set[str] = set()

        for _, row in synergies_table.iterrows():
            objective_a = str(row.get("objective_A", "")).strip()
            objective_b = str(row.get("objective_B", "")).strip()
            if objective_a in objective_ids and objective_b in objective_ids:
                effect = as_float(row.get("effect", 0))
                synergies.append(f"{objective_a}+{objective_b}: +{round(effect, 4)}")
                rows.add(f"objectives.objective_synergies:{objective_a}:{objective_b}")

        for _, row in conflicts_table.iterrows():
            objective_a = str(row.get("objective_A", "")).strip()
            objective_b = str(row.get("objective_B", "")).strip()
            if objective_a in objective_ids and objective_b in objective_ids:
                effect = as_float(row.get("effect", 0))
                conflicts.append(f"{objective_a}+{objective_b}: -{round(effect, 4)}")
                rows.add(f"objectives.objective_conflicts:{objective_a}:{objective_b}")

        return ObjectiveNetworkSummary(
            synergies=tuple(sorted(synergies)),
            conflicts=tuple(sorted(conflicts)),
            formula_ids_used=("OBJ-502", "OBJ-503"),
            warehouse_rows_used=tuple(sorted(rows)),
        )


class WarehouseBackedMechanismProjection:
    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def project(
        self,
        objectives: tuple[ObjectivePlan, ...],
        network_summary: ObjectiveNetworkSummary,
    ) -> tuple[MechanismPlan, ...]:
        objective_mechanisms = self.warehouse.load_dataset("objectives.objective_mechanisms")
        mechanisms = self.warehouse.load_dataset("mechanisms.mechanisms")

        objective_index = {item.objective_id: item for item in objectives}
        mechanism_meta = {
            str(row.get("mechanism_id", "")).strip(): {k: str(v) for k, v in row.items()}
            for _, row in mechanisms.iterrows()
            if str(row.get("mechanism_id", "")).strip()
        }

        by_mechanism: dict[str, dict[str, object]] = {}
        for _, row in objective_mechanisms.iterrows():
            row_data = {k: str(v) for k, v in row.items()}
            objective_id = row_data.get("objective_id", "").strip()
            mechanism_id = row_data.get("mechanism_id", "").strip()
            if objective_id not in objective_index or not mechanism_id:
                continue
            importance = as_float(row_data.get("importance", 0))
            objective = objective_index[objective_id]
            contribution = objective.objective_priority * importance

            bucket = by_mechanism.setdefault(
                mechanism_id,
                {
                    "importance": 0.0,
                    "objectives": set(),
                    "conditions": set(),
                    "papers": set(),
                    "quotes": [],
                    "formula_ids": {"MEC-505"},
                    "rows": set(),
                },
            )
            bucket["importance"] = float(bucket["importance"]) + contribution
            bucket["objectives"].add(objective.objective_name)
            bucket["papers"].update(objective.supporting_papers)
            bucket["quotes"].extend(objective.supporting_quotes)
            for condition in objective.supporting_conditions:
                bucket["conditions"].add(condition.condition_name)
            if row_data.get("paper", "").strip():
                bucket["papers"].add(row_data["paper"].strip())
            if row_data.get("quote", "").strip():
                bucket["quotes"].append(row_data["quote"].strip())
            bucket["formula_ids"].update(objective.formula_ids_used)
            bucket["rows"].update(objective.warehouse_rows_used)
            bucket["rows"].add(f"objectives.objective_mechanisms:{objective_id}:{mechanism_id}")
            bucket["rows"].add(f"mechanisms.mechanisms:{mechanism_id}")

        plans: list[MechanismPlan] = []
        notes = list(network_summary.synergies) + list(network_summary.conflicts)
        for mechanism_id in sorted(by_mechanism):
            bucket = by_mechanism[mechanism_id]
            meta = mechanism_meta.get(mechanism_id, {})
            mechanism_name = meta.get("mechanism_name", mechanism_id)
            plans.append(
                MechanismPlan(
                    mechanism_id=mechanism_id,
                    mechanism=mechanism_name,
                    objective=" | ".join(sorted(bucket["objectives"])),
                    supporting_conditions=tuple(sorted(bucket["conditions"])),
                    importance=round(float(bucket["importance"]), 6),
                    supporting_papers=tuple(sorted(bucket["papers"])),
                    supporting_quotes=tuple(dict.fromkeys(bucket["quotes"])),
                    formula_ids_used=tuple(sorted(bucket["formula_ids"])),
                    dose_formula_ids=("ING-506", "SRC-601", "SRC-602"),
                    interaction_notes=tuple(notes),
                )
            )
        plans.sort(key=lambda item: (-item.importance, item.mechanism_id))
        return tuple(plans)


@dataclass(frozen=True)
class ObjectiveNetworkRuntime:
    warehouse: WarehouseInterface
    objective_resolver: ObjectiveResolver | None = None
    objective_planner: ObjectivePlanner | None = None
    objective_network: ObjectiveNetwork | None = None
    source_resolver: IngredientSourceResolver | None = None
    source_planner: SourcePlanner | None = None
    bioavailability_analyzer: BioavailabilityAnalyzer | None = None
    trace_builder: ObjectiveTraceBuilder | None = None

    def __post_init__(self) -> None:
        if self.objective_resolver is None:
            object.__setattr__(self, "objective_resolver", WarehouseBackedObjectiveResolver(self.warehouse))
        if self.objective_planner is None:
            object.__setattr__(self, "objective_planner", WarehouseBackedObjectivePlanner(self.warehouse))
        if self.objective_network is None:
            object.__setattr__(self, "objective_network", WarehouseBackedObjectiveNetwork(self.warehouse))
        if self.source_resolver is None:
            object.__setattr__(self, "source_resolver", WarehouseBackedIngredientSourceResolver(self.warehouse))
        if self.source_planner is None:
            object.__setattr__(self, "source_planner", WarehouseBackedSourcePlanner(self.warehouse))
        if self.bioavailability_analyzer is None:
            object.__setattr__(self, "bioavailability_analyzer", DeterministicBioavailabilityAnalyzer())
        if self.trace_builder is None:
            object.__setattr__(self, "trace_builder", DeterministicObjectiveTraceBuilder())

    def run(self, assessments: tuple[ConditionAssessment, ...]) -> ObjectiveRuntimeResult:
        trace_items: list[ObjectiveStageTrace] = []
        run_id = uuid.uuid4().hex
        mechanism_projection = WarehouseBackedMechanismProjection(self.warehouse)

        def _trace(stage_name: str, started: float, result, formula_ids: tuple[str, ...], rows: tuple[str, ...]) -> None:
            elapsed = (time.perf_counter() - started) * 1000.0
            trace_items.append(
                self.trace_builder.build(  # type: ignore[union-attr]
                    stage_name=stage_name,
                    execution_time_ms=elapsed,
                    formula_ids=formula_ids,
                    warehouse_rows_used=rows,
                    input_summary="ConditionAssessment[]",
                    output_summary=type(result).__name__,
                )
            )

        started = time.perf_counter()
        objectives = self.objective_resolver.resolve(assessments)  # type: ignore[union-attr]
        _trace(
            "Objective Resolver",
            started,
            objectives,
            tuple(sorted({formula for item in objectives for formula in item.formula_ids_used})),
            tuple(sorted({row for item in objectives for row in item.warehouse_rows_used})),
        )

        started = time.perf_counter()
        objective_plan = self.objective_planner.plan(objectives)  # type: ignore[union-attr]
        _trace(
            "Objective Planner",
            started,
            objective_plan,
            tuple(sorted({formula for item in objective_plan for formula in item.formula_ids_used})),
            tuple(sorted({row for item in objective_plan for row in item.warehouse_rows_used})),
        )

        started = time.perf_counter()
        network_summary = self.objective_network.map(objective_plan)  # type: ignore[union-attr]
        _trace(
            "Objective Network",
            started,
            network_summary,
            network_summary.formula_ids_used,
            network_summary.warehouse_rows_used,
        )

        started = time.perf_counter()
        mechanism_plan = mechanism_projection.project(objective_plan, network_summary)
        _trace(
            "Mechanism Projection",
            started,
            mechanism_plan,
            tuple(sorted({formula for item in mechanism_plan for formula in item.formula_ids_used})),
            tuple(),
        )

        started = time.perf_counter()
        ingredient_plan = self.source_resolver.resolve(mechanism_plan)  # type: ignore[union-attr]
        _trace(
            "Ingredient Source Resolver",
            started,
            ingredient_plan,
            tuple(sorted({formula for item in ingredient_plan for formula in item.formula_ids_used})),
            tuple(sorted({row for item in ingredient_plan for row in item.warehouse_rows_used})),
        )

        started = time.perf_counter()
        source_plan = self.source_planner.plan(ingredient_plan)  # type: ignore[union-attr]
        _trace(
            "Source Planner",
            started,
            source_plan,
            tuple(sorted({formula for item in source_plan for formula in item.formula_ids_used})),
            tuple(sorted({row for item in source_plan for row in item.warehouse_rows_used})),
        )

        started = time.perf_counter()
        ingredient_source_plan = self.bioavailability_analyzer.analyze(source_plan)  # type: ignore[union-attr]
        _trace(
            "Bioavailability Analyzer",
            started,
            ingredient_source_plan,
            ("SRC-601", "SRC-602"),
            tuple(sorted({row for item in ingredient_source_plan for row in item.warehouse_rows_used})),
        )

        return ObjectiveRuntimeResult(
            objective_plan=objective_plan,
            mechanism_plan=mechanism_plan,
            ingredient_plan=ingredient_plan,
            ingredient_source_plan=ingredient_source_plan,
            network_summary=network_summary,
            trace=ObjectiveRuntimeTrace(run_id=run_id, stages=tuple(trace_items)),
        )
