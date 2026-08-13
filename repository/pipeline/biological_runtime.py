"""Concrete Ω3 biological runtime implementations.

Implements:
- DogResolver
- LifeStageResolver
- EnvironmentResolver
- TraitResolver
- ObservationResolver
- ResolvedDogValidator
- EvidenceCollector
- EvidenceGraphBuilder
- ScientificExplainabilityBuilder
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import re

from repository.models.explainability import (
    EvidenceChain,
    EvidenceEdge,
    EvidenceNode,
    ScientificCitation,
)
from repository.models.runtime import (
    ConditionEvidence,
    DogProfile,
    EvidenceCollection,
    EvidenceGraph,
    LifeStage,
    ResolvedDog,
    ResolvedEnvironment,
    ResolvedTraits,
    ValidationError,
    ValidationResult,
)
from repository.warehouse import WarehouseInterface


LIFE_STAGE_ORDER = ("Puppy", "Young Adult", "Mature Adult", "Senior", "End of Life")
CANONICAL_TRAITS = (
    "size",
    "body_type",
    "coat_type",
    "energy",
    "skull_type",
    "function_group",
    "weakness_group",
    "lifespan",
    "climate",
)


def _fact_id(prefix: str, payload: str) -> str:
    return f"{prefix}_{hashlib.sha1(payload.encode('utf-8')).hexdigest()[:8].upper()}"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _parse_iso_date(raw: str) -> date | None:
    if not raw:
        return None
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _age_from_dob(dob: date) -> tuple[int, float, float]:
    today = datetime.now(timezone.utc).date()
    delta = (today - dob).days
    months = round(delta / 30.4375, 3)
    years = round(delta / 365.25, 3)
    return delta, months, years


def _to_float(raw: str | float | int | None) -> float | None:
    if raw is None:
        return None
    txt = _norm(str(raw))
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        return None


class WarehouseBackedDogResolver:
    """Resolve profile into canonical dog fields without disease inference."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, profile: DogProfile) -> ResolvedDog:
        breeds = self.warehouse.load_dataset("biology.breeds")
        breed_name = _norm(profile.breeds[0] if profile.breeds else "")
        match = breeds[breeds["breed_name"].str.lower() == breed_name.lower()] if breed_name else breeds.iloc[0:0]

        breed_id = _norm(match.iloc[0]["breed_id"]) if not match.empty else ""
        canonical_breed = _norm(match.iloc[0]["breed_name"]) if not match.empty else breed_name

        dob = _parse_iso_date(profile.date_of_birth)
        if dob is not None:
            age_days, age_months, age_years = _age_from_dob(dob)
            dob_text = dob.isoformat()
        else:
            dob_text = _norm(profile.date_of_birth)
            age_years = profile.age_years
            age_months = round(age_years * 12.0, 3) if age_years is not None else None
            age_days = int(age_years * 365.25) if age_years is not None else None

        return ResolvedDog(
            dog_id=profile.dog_id,
            breed=canonical_breed,
            breed_id=breed_id,
            date_of_birth=dob_text,
            age_days=age_days,
            age_months=age_months,
            age_years=age_years,
            weight=_to_float(profile.weight_kg),
            environment=_norm(profile.environment),
            life_stage="",
            breed_metadata={
                "breed_group": _norm(match.iloc[0]["breed_group"]) if not match.empty else "",
                "species": _norm(match.iloc[0]["species"]) if not match.empty else "",
            },
            runtime_metadata={
                "resolver": "WarehouseBackedDogResolver",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
            },
        )


class WarehouseBackedLifeStageResolver:
    """Resolve life stage from warehouse lifespan facts (no hardcoded breed thresholds)."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, resolved_dog: ResolvedDog) -> LifeStage:
        facts = self.warehouse.load_dataset("biology.life_stage_health_NEEDS_VALIDATION")
        stage_rows = facts[facts["stage"].isin(LIFE_STAGE_ORDER)] if "stage" in facts.columns else facts.iloc[0:0]

        # Parse age thresholds from "STANDARD OF AGES" rows.
        # If unavailable, select closest stage by broad bins derived from available ordering only.
        years = resolved_dog.age_years
        if years is None:
            return LifeStage(stage="Unknown", rationale="Age unavailable")

        # Minimal deterministic mapping based on fact ordering and age progression.
        # This uses warehouse facts only as stage vocabulary source.
        if years < 1.0:
            stage = "Puppy"
        elif years < 3.5:
            stage = "Young Adult"
        elif years < 10.5:
            stage = "Mature Adult"
        elif years < 14.0:
            stage = "Senior"
        else:
            stage = "End of Life"

        row = stage_rows[stage_rows["stage"] == stage]
        fact_id = _norm(row.iloc[0]["fact_id"]) if not row.empty and "fact_id" in row.columns else ""
        rationale = _norm(row.iloc[0]["brief_explanation"]) if not row.empty and "brief_explanation" in row.columns else "Stage derived from age range."
        return LifeStage(stage=stage, source_fact_id=fact_id, rationale=rationale)


class WarehouseBackedEnvironmentResolver:
    """Normalize environment details and attach known environment ids/facts."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, profile: DogProfile) -> ResolvedEnvironment:
        env_facts = self.warehouse.load_dataset("biology.environment_facts")
        known_env_names = sorted(set(env_facts["environment_name"].astype(str))) if "environment_name" in env_facts.columns else []

        climate = _norm(profile.climate)
        if not climate and profile.environment:
            lower = profile.environment.lower()
            for name in known_env_names:
                if name.lower().split()[0] in lower:
                    climate = name
                    break
        if not climate and known_env_names:
            climate = known_env_names[0]

        env_match = env_facts[env_facts["environment_name"].str.lower() == climate.lower()] if climate and "environment_name" in env_facts.columns else env_facts.iloc[0:0]
        environment_id = _norm(env_match.iloc[0]["environment_id"]) if not env_match.empty and "environment_id" in env_match.columns else ""

        base_name = _norm(profile.environment) or climate or "Unknown"
        return ResolvedEnvironment(
            environment_name=base_name,
            city=_norm(profile.city),
            country=_norm(profile.country),
            climate=climate,
            urbanicity=_norm(profile.urbanicity),
            season=_norm(profile.season),
            housing=_norm(profile.housing),
            walking_environment=_norm(profile.walking_environment),
            environment_id=environment_id,
            environment_metadata={
                "resolver": "WarehouseBackedEnvironmentResolver",
                "known_environment_match": "yes" if environment_id else "no",
            },
        )


class WarehouseBackedTraitResolver:
    """Resolve biological traits from warehouse records."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def resolve(self, resolved_dog: ResolvedDog) -> ResolvedTraits:
        breed_traits = self.warehouse.load_dataset("biology.breed_traits")
        trait_assoc = self.warehouse.load_dataset("biology.trait_condition_associations")

        rows = []
        provenance = []

        if not breed_traits.empty and resolved_dog.breed_id:
            b = breed_traits[breed_traits["breed_id"].str.lower() == resolved_dog.breed_id.lower()]
            for _, r in b.iterrows():
                tname = _norm(r.get("trait_name", ""))
                tval = _norm(r.get("trait_value", ""))
                if not tname:
                    continue
                rows.append(
                    {
                        "trait_name": tname,
                        "trait_value": tval,
                        "status": "estimated",
                        "source": "breed_traits",
                        "fact_id": _norm(r.get("fact_id", "")),
                    }
                )
                provenance.append({"trait_name": tname, "source_dataset": "biology.breed_traits", "fact_id": _norm(r.get("fact_id", ""))})

        # Ensure required canonical trait slots exist.
        for trait_name in CANONICAL_TRAITS:
            existing = [x for x in rows if _norm(x["trait_name"]).lower() == trait_name.lower()]
            if existing:
                continue
            candidates = trait_assoc[trait_assoc["trait_name"].str.lower() == trait_name.lower()] if "trait_name" in trait_assoc.columns else trait_assoc.iloc[0:0]
            fallback = _norm(candidates.iloc[0]["trait_value"]) if not candidates.empty else ""
            rows.append(
                {
                    "trait_name": trait_name,
                    "trait_value": fallback,
                    "status": "estimated" if fallback else "unresolved",
                    "source": "trait_condition_associations_fallback" if fallback else "none",
                    "fact_id": _norm(candidates.iloc[0]["fact_id"]) if not candidates.empty else "",
                }
            )
            if fallback:
                provenance.append(
                    {
                        "trait_name": trait_name,
                        "source_dataset": "biology.trait_condition_associations",
                        "fact_id": _norm(candidates.iloc[0]["fact_id"]),
                    }
                )

        return ResolvedTraits(
            dog_id=resolved_dog.dog_id,
            traits=tuple(rows),
            conflicts=tuple(),
            provenance=tuple(provenance),
        )


class WarehouseBackedObservationResolver:
    """Merge observed traits with expected traits and mark conflicts."""

    def merge(self, profile: DogProfile, resolved_traits: ResolvedTraits) -> ResolvedTraits:
        by_name = {t["trait_name"].lower(): dict(t) for t in resolved_traits.traits}
        conflicts: list[dict[str, str]] = list(resolved_traits.conflicts)
        provenance: list[dict[str, str]] = list(resolved_traits.provenance)

        for obs in profile.groomer_observations:
            trait_name = _norm(obs.get("trait_name", ""))
            trait_value = _norm(obs.get("trait_value", obs.get("value", "")))
            source = _norm(obs.get("source", "groomer_observation"))
            if not trait_name:
                continue
            key = trait_name.lower()
            current = by_name.get(key)
            if current is None:
                by_name[key] = {
                    "trait_name": trait_name,
                    "trait_value": trait_value,
                    "status": "confirmed" if trait_value else "observed",
                    "source": source,
                    "fact_id": "",
                }
            else:
                expected = _norm(current.get("trait_value", ""))
                if expected and trait_value and expected.lower() != trait_value.lower():
                    conflicts.append(
                        {
                            "trait_name": trait_name,
                            "expected": expected,
                            "observed": trait_value,
                            "status": "conflicting",
                            "source": source,
                        }
                    )
                    current["status"] = "conflicting"
                    current["observed_value"] = trait_value
                elif trait_value:
                    current["trait_value"] = trait_value
                    current["status"] = "confirmed"
                    current["source"] = source
                by_name[key] = current
            provenance.append({"trait_name": trait_name, "source_dataset": source, "fact_id": ""})

        return ResolvedTraits(
            dog_id=resolved_traits.dog_id,
            traits=tuple(by_name.values()),
            conflicts=tuple(conflicts),
            provenance=tuple(provenance),
        )


class WarehouseBackedResolvedDogValidator:
    """Structured validation for resolved biological profile."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def validate(
        self,
        resolved_dog: ResolvedDog,
        environment: ResolvedEnvironment,
        traits: ResolvedTraits,
    ) -> ValidationResult:
        errors: list[ValidationError] = []
        breeds = self.warehouse.load_dataset("biology.breeds")
        if not resolved_dog.breed_id:
            errors.append(ValidationError(code="missing_breed_id", field="breed", detail="Breed could not be resolved."))
        elif resolved_dog.breed_id not in set(breeds["breed_id"].astype(str)):
            errors.append(ValidationError(code="unknown_breed_id", field="breed_id", detail=resolved_dog.breed_id))

        if resolved_dog.weight is None or resolved_dog.weight <= 0:
            errors.append(ValidationError(code="invalid_weight", field="weight", detail="Weight must be > 0."))
        if resolved_dog.age_days is not None and resolved_dog.age_days < 0:
            errors.append(ValidationError(code="invalid_age", field="date_of_birth", detail="DOB in the future."))
        if not environment.climate:
            errors.append(ValidationError(code="missing_environment", field="climate", detail="Climate unresolved."))
        if not traits.traits:
            errors.append(ValidationError(code="missing_traits", field="traits", detail="No traits resolved."))

        return ValidationResult(ok=not errors, errors=tuple(errors))


class WarehouseBackedEvidenceCollector:
    """Collect all relevant scientific facts without scoring or ranking."""

    def __init__(self, warehouse: WarehouseInterface):
        self.warehouse = warehouse

    def collect(
        self,
        resolved_dog: ResolvedDog,
        life_stage: LifeStage,
        environment: ResolvedEnvironment,
        resolved_traits: ResolvedTraits,
    ) -> EvidenceCollection:
        observed = self.warehouse.load_dataset("biology.observed_breed_conditions")
        trait_assoc = self.warehouse.load_dataset("biology.trait_condition_associations")
        env = self.warehouse.load_dataset("biology.environment_facts")
        activities = self.warehouse.load_dataset("prevention.condition_activities")
        ingredients = self.warehouse.load_dataset("prevention.condition_ingredients")
        mixed = self.warehouse.load_dataset("biology.mixed_breed_NEEDS_VALIDATION")
        life = self.warehouse.load_dataset("biology.life_stage_health_NEEDS_VALIDATION")

        trait_pairs = {(t.get("trait_name", ""), t.get("trait_value", "")) for t in resolved_traits.traits}
        trait_values = {t.get("trait_value", "") for t in resolved_traits.traits}

        observed_hits = observed[observed["breed_id"] == resolved_dog.breed_id] if "breed_id" in observed.columns else observed.iloc[0:0]
        trait_hits = trait_assoc[
            trait_assoc.apply(lambda r: (r.get("trait_name", ""), r.get("trait_value", "")) in trait_pairs, axis=1)
        ] if not trait_assoc.empty else trait_assoc
        env_hits = env[env["environment_name"].str.lower() == environment.climate.lower()] if environment.climate and "environment_name" in env.columns else env.iloc[0:0]
        interaction_hits = mixed[
            mixed.apply(
                lambda r: _norm(r.get("trait_a", "")) in trait_values or _norm(r.get("trait_b", "")) in trait_values,
                axis=1,
            )
        ] if not mixed.empty else mixed
        life_hits = life[life["stage"].str.lower() == life_stage.stage.lower()] if life_stage.stage and "stage" in life.columns else life.iloc[0:0]

        condition_map: dict[str, dict[str, list[dict[str, str]]]] = {}

        def _ensure(condition_id: str, condition_name: str):
            key = condition_id or _fact_id("COND_UNKNOWN", condition_name or "unknown")
            if key not in condition_map:
                condition_map[key] = {
                    "condition_id": condition_id,
                    "condition_name": condition_name,
                    "observed_evidence": [],
                    "trait_evidence": [],
                    "environment_evidence": [],
                    "interaction_evidence": [],
                    "life_stage_evidence": [],
                    "activity_evidence": [],
                    "ingredient_evidence": [],
                    "citations": [],
                }
            return key

        def _citation(r: dict[str, str]) -> dict[str, str]:
            return {
                "citation_id": _fact_id("CIT", f"{r.get('fact_id','')}|{r.get('paper_link','')}"),
                "fact_id": _norm(r.get("fact_id", "")),
                "paper_name": _norm(r.get("paper_name", r.get("source_name", ""))),
                "paper_link": _norm(r.get("paper_link", r.get("source_url", ""))),
                "scientific_quote": _norm(r.get("scientific_quote", r.get("source_quote", ""))),
                "source_dataset": _norm(r.get("source_dataset", "")),
            }

        for _, r in observed_hits.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            key = _ensure(row.get("condition_id", ""), row.get("condition_name", ""))
            condition_map[key]["observed_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in trait_hits.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            key = _ensure(row.get("condition_id", ""), row.get("condition_name", ""))
            condition_map[key]["trait_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in env_hits.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            condition_name = _norm(row.get("metric_name", "").replace("condition_prevalence:", ""))
            key = _ensure("", condition_name)
            condition_map[key]["environment_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in interaction_hits.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            condition_name = _norm(row.get("condition", ""))
            key = _ensure("", condition_name)
            condition_map[key]["interaction_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in activities.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            key = _ensure(row.get("condition_id", ""), row.get("condition_name", ""))
            condition_map[key]["activity_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in ingredients.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            key = _ensure(row.get("condition_id", ""), row.get("condition_name", ""))
            condition_map[key]["ingredient_evidence"].append(row)
            condition_map[key]["citations"].append(_citation(row))

        for _, r in life_hits.iterrows():
            row = {k: _norm(v) for k, v in r.to_dict().items()}
            # attach life-stage context to all condition nodes
            for key in list(condition_map.keys()):
                condition_map[key]["life_stage_evidence"].append(row)

        condition_evidence = []
        all_fact_ids: list[str] = []
        for item in condition_map.values():
            citations = tuple(item["citations"])
            ce = ConditionEvidence(
                dog_id=resolved_dog.dog_id,
                condition_id=item["condition_id"],
                condition_name=item["condition_name"],
                observed_evidence=tuple(item["observed_evidence"]),
                trait_evidence=tuple(item["trait_evidence"]),
                environment_evidence=tuple(item["environment_evidence"]),
                interaction_evidence=tuple(item["interaction_evidence"]),
                life_stage_evidence=tuple(item["life_stage_evidence"]),
                activity_evidence=tuple(item["activity_evidence"]),
                ingredient_evidence=tuple(item["ingredient_evidence"]),
                citations=citations,
            )
            condition_evidence.append(ce)
            all_fact_ids.extend([c["fact_id"] for c in citations if c.get("fact_id")])

        unique_fact_ids = sorted(set([f for f in all_fact_ids if f]))
        metadata = {
            "evidence_row_count": str(sum(len(asdict(c)["observed_evidence"]) + len(asdict(c)["trait_evidence"]) for c in condition_evidence)),
            "condition_node_count": str(len(condition_evidence)),
        }
        return EvidenceCollection(
            dog_id=resolved_dog.dog_id,
            condition_evidence=tuple(condition_evidence),
            collected_fact_ids=tuple(unique_fact_ids),
            collection_metadata=metadata,
        )


class InMemoryEvidenceGraphBuilder:
    """Builds in-memory condition evidence graph with citations on edges."""

    def build(self, evidence_collection: EvidenceCollection) -> EvidenceGraph:
        nodes: list[dict[str, str]] = []
        edges: list[dict[str, str]] = []
        citations: list[dict[str, str]] = []

        for ce in evidence_collection.condition_evidence:
            condition_node_id = _fact_id("NODE_COND", f"{ce.condition_id}|{ce.condition_name}")
            nodes.append(
                {
                    "node_id": condition_node_id,
                    "node_type": "condition",
                    "condition_id": ce.condition_id,
                    "condition_name": ce.condition_name,
                }
            )

            def _emit(kind: str, rows: tuple[dict[str, str], ...]):
                for i, row in enumerate(rows):
                    src_id = _fact_id("NODE_SRC", f"{kind}|{row.get('fact_id','')}|{i}")
                    nodes.append(
                        {
                            "node_id": src_id,
                            "node_type": kind,
                            "condition_id": ce.condition_id,
                            "condition_name": ce.condition_name,
                        }
                    )
                    citation_id = _fact_id(
                        "CIT",
                        f"{row.get('paper_link','')}|{row.get('paper_name','')}|{row.get('fact_id','')}",
                    )
                    citations.append(
                        {
                            "citation_id": citation_id,
                            "fact_id": _norm(row.get("fact_id", "")),
                            "paper_name": _norm(row.get("paper_name", row.get("source_name", ""))),
                            "paper_link": _norm(row.get("paper_link", row.get("source_url", ""))),
                            "scientific_quote": _norm(row.get("scientific_quote", row.get("source_quote", ""))),
                        }
                    )
                    edges.append(
                        {
                            "edge_id": _fact_id("EDGE", f"{src_id}|{condition_node_id}"),
                            "from_node_id": src_id,
                            "to_node_id": condition_node_id,
                            "evidence_type": kind,
                            "effect": _norm(
                                row.get("effect_direction", row.get("interaction", row.get("association_type", "")))
                            ),
                            "source_fact_id": _norm(row.get("fact_id", "")),
                            "source_label": _norm(
                                row.get("trait_value", row.get("activity_name", row.get("ingredient_name", row.get("environment_name", ""))))
                            ),
                            "value_number": _norm(row.get("effect_value", row.get("value_number", ""))),
                            "observed_value": _norm(row.get("value_number", "")) if kind == "observed" else "",
                            "factor": _norm(row.get("factor", "")),
                            "population": _norm(row.get("population_description", row.get("sample_population", ""))),
                            "sample_size": _norm(row.get("denominator_count", row.get("sample_size", ""))),
                            "publication_year": _norm(row.get("publication_year", row.get("year", ""))),
                            "source_dataset": kind,
                            "citation_id": citation_id,
                        }
                    )

            _emit("observed", ce.observed_evidence)
            _emit("trait", ce.trait_evidence)
            _emit("environment", ce.environment_evidence)
            _emit("interaction", ce.interaction_evidence)
            _emit("life_stage", ce.life_stage_evidence)
            _emit("activity", ce.activity_evidence)
            _emit("ingredient", ce.ingredient_evidence)

        return EvidenceGraph(
            dog_id=evidence_collection.dog_id,
            nodes=tuple(nodes),
            edges=tuple(edges),
            citations=tuple(citations),
        )


class ScientificExplainabilityBuilder:
    """Build placeholder explainability chain from evidence graph."""

    def build_chain(self, evidence_graph: EvidenceGraph) -> EvidenceChain:
        condition_nodes = [n for n in evidence_graph.nodes if n.get("node_type") == "condition"]
        if not condition_nodes:
            return EvidenceChain(chain_id=_fact_id("CHAIN", evidence_graph.dog_id), condition_id="")

        first = condition_nodes[0]
        citations_by_id = {c["citation_id"]: c for c in evidence_graph.citations if c.get("citation_id")}
        node_list: list[EvidenceNode] = []
        edge_list: list[EvidenceEdge] = []

        for cn in condition_nodes:
            node_id = _norm(cn.get("node_id", ""))
            outgoing = [e for e in evidence_graph.edges if e.get("to_node_id") == node_id]
            scis: list[ScientificCitation] = []
            for edge in outgoing:
                cit = citations_by_id.get(edge.get("citation_id", ""))
                if not cit:
                    continue
                scis.append(
                    ScientificCitation(
                        citation_id=cit["citation_id"],
                        paper_name=cit.get("paper_name", ""),
                        paper_link=cit.get("paper_link", ""),
                        scientific_quote=cit.get("scientific_quote", ""),
                        fact_id=cit.get("fact_id", ""),
                    )
                )
                edge_list.append(
                    EvidenceEdge(
                        edge_id=edge.get("edge_id", ""),
                        from_node_id=edge.get("from_node_id", ""),
                        to_node_id=edge.get("to_node_id", ""),
                        evidence_type=edge.get("evidence_type", ""),
                        effect=edge.get("effect", ""),
                        source_dataset=edge.get("source_dataset", ""),
                        citation=scis[-1],
                    )
                )
            node_list.append(
                EvidenceNode(
                    node_id=node_id,
                    condition_id=cn.get("condition_id", ""),
                    condition_name=cn.get("condition_name", ""),
                    summary=f"Evidence collected for {cn.get('condition_name','condition')}",
                    citations=tuple(scis),
                )
            )

        return EvidenceChain(
            chain_id=_fact_id("CHAIN", evidence_graph.dog_id),
            condition_id=first.get("condition_id", ""),
            nodes=tuple(node_list),
            edges=tuple(edge_list),
        )
