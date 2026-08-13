"""Pipeline orchestrator for the permanent biological runtime flow."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from repository.models.runtime import (
    DogProfile,
    EvidenceCollection,
    EvidenceGraph,
    LifeStage,
    ResolvedDog,
    ResolvedEnvironment,
    ResolvedTraits,
    ValidationResult,
)
from repository.models.trace import RuntimeTrace, StageTrace
from .interfaces import (
    DogResolver,
    EvidenceCollector,
    EvidenceGraphBuilder,
    EnvironmentResolver,
    LifeStageResolver,
    ObservationResolver,
    ResolvedDogValidator,
    TraitResolver,
)
from .stage_order import PIPELINE_STAGE_ORDER


@dataclass(frozen=True)
class PipelineResult:
    resolved_dog: ResolvedDog
    life_stage: LifeStage
    environment: ResolvedEnvironment
    resolved_traits: ResolvedTraits
    evidence_collection: EvidenceCollection
    evidence_graph: EvidenceGraph
    validation: ValidationResult
    trace: RuntimeTrace


class PipelineOrchestrator:
    def __init__(
        self,
        dog_resolver: DogResolver,
        life_stage_resolver: LifeStageResolver,
        environment_resolver: EnvironmentResolver,
        trait_resolver: TraitResolver,
        observation_resolver: ObservationResolver,
        resolved_dog_validator: ResolvedDogValidator,
        evidence_collector: EvidenceCollector,
        evidence_graph_builder: EvidenceGraphBuilder,
    ):
        self.dog_resolver = dog_resolver
        self.life_stage_resolver = life_stage_resolver
        self.environment_resolver = environment_resolver
        self.trait_resolver = trait_resolver
        self.observation_resolver = observation_resolver
        self.resolved_dog_validator = resolved_dog_validator
        self.evidence_collector = evidence_collector
        self.evidence_graph_builder = evidence_graph_builder

    def run(self, profile: DogProfile) -> PipelineResult:
        traces: list[StageTrace] = []
        run_id = uuid.uuid4().hex

        def _stage(name: str, fn, input_value):
            start = time.perf_counter()
            warnings: tuple[str, ...] = ()
            errors: tuple[str, ...] = ()
            try:
                out = fn(input_value)
            except Exception as exc:  # noqa: BLE001
                out = None
                errors = (f"{type(exc).__name__}: {exc}",)
                raise
            finally:
                runtime_ms = (time.perf_counter() - start) * 1000.0
                traces.append(
                    StageTrace(
                        stage_name=name,
                        input_summary=type(input_value).__name__,
                        output_summary=type(out).__name__ if out is not None else "None",
                        runtime_ms=runtime_ms,
                        warnings=warnings,
                        errors=errors,
                        evidence_collected_count=getattr(out, "collection_metadata", {}).get(
                            "evidence_row_count", ""
                        )
                        if out is not None
                        else "",
                    )
                )
            return out

        resolved_dog = _stage(PIPELINE_STAGE_ORDER[0], self.dog_resolver.resolve, profile)
        life_stage = _stage(PIPELINE_STAGE_ORDER[1], self.life_stage_resolver.resolve, resolved_dog)
        environment = _stage(PIPELINE_STAGE_ORDER[2], self.environment_resolver.resolve, profile)
        resolved_traits = _stage(PIPELINE_STAGE_ORDER[3], self.trait_resolver.resolve, resolved_dog)
        resolved_traits = _stage(
            PIPELINE_STAGE_ORDER[4],
            lambda traits: self.observation_resolver.merge(profile, traits),
            resolved_traits,
        )
        validation = _stage(
            PIPELINE_STAGE_ORDER[5],
            lambda traits: self.resolved_dog_validator.validate(resolved_dog, environment, traits),
            resolved_traits,
        )
        if not validation.ok:
            raise ValueError(
                "ResolvedDog validation failed: "
                + "; ".join(f"{e.field}:{e.code}" for e in validation.errors)
            )
        evidence_collection = _stage(
            PIPELINE_STAGE_ORDER[6],
            lambda traits: self.evidence_collector.collect(resolved_dog, life_stage, environment, traits),
            resolved_traits,
        )
        evidence_graph = _stage(
            PIPELINE_STAGE_ORDER[7], self.evidence_graph_builder.build, evidence_collection
        )

        return PipelineResult(
            resolved_dog=resolved_dog,
            life_stage=life_stage,
            environment=environment,
            resolved_traits=resolved_traits,
            evidence_collection=evidence_collection,
            evidence_graph=evidence_graph,
            validation=validation,
            trace=RuntimeTrace(run_id=run_id, stages=tuple(traces)),
        )
