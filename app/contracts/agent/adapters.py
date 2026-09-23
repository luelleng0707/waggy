"""Map existing engine models to Ω11 contracts. No scientific reasoning."""

from __future__ import annotations

from typing import Any

from app.agent.state import DogProfileInput
from app.contracts.agent.bundles import (
    OPTIMIZER_ALGORITHM,
    BundleOption,
    BundleSearchResult,
    FilterFunnel,
    NutrientLedger,
    NutrientLedgerRow,
    OptimizerProvenance,
)
from app.contracts.agent.enums import (
    AvailabilityStatus,
    BundleTier,
    EvidenceStatus,
    InputState,
    ObserverRole,
    ToolErrorCode,
)
from app.contracts.agent.errors import missing_required_input
from app.contracts.agent.evidence import ScientificEvidence, ScientificFact
from app.contracts.agent.health import ConditionFinding, HealthAnalysisResult, PreventativeTarget
from app.contracts.agent.inference import BreedPrevalence, PrevalenceValue
from app.contracts.agent.input import CanonicalDogInput, not_provided, provided
from app.contracts.agent.nutrition import NutrientRequirement, NutritionAnalysisResult
from app.contracts.agent.observations import Observation
from app.contracts.agent.products import ProductIdentity, ProductRecord
from app.contracts.agent.provenance import ProvenanceRecord
from app.contracts.agent.versions import VersionStamp, runtime_engine_version


def _status(raw: Any, default: EvidenceStatus = EvidenceStatus.NOT_AVAILABLE) -> EvidenceStatus:
    if raw is None or raw == "":
        return default
    text = str(raw)
    if text == "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE":
        return EvidenceStatus.NOT_AVAILABLE
    try:
        return EvidenceStatus(text)
    except ValueError:
        if text.upper() == "MIGRATED":
            return EvidenceStatus.MIGRATED
        return default


def _prevalence(*, status_raw: Any, percent: Any = None, ratio: Any = None) -> PrevalenceValue:
    if status_raw in {None, "", "NOT_AVAILABLE", "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE"}:
        if percent is None and ratio is None:
            return PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE)
    if percent is None and ratio is None:
        return PrevalenceValue(status=AvailabilityStatus.NOT_AVAILABLE)
    return PrevalenceValue(
        status=AvailabilityStatus.AVAILABLE,
        percent=float(percent) if percent is not None else None,
        ratio=float(ratio) if ratio is not None else None,
        unit="percent" if percent is not None else "ratio",
    )


def canonical_dog_from_engine(profile: DogProfileInput) -> CanonicalDogInput:
    """Every engine-supplied field becomes PROVIDED. No invented values."""
    return CanonicalDogInput(
        name=provided(profile.name) if profile.name else not_provided(),
        primary_breed=provided(profile.primary_breed),
        secondary_breed=provided(profile.secondary_breed) if profile.secondary_breed else not_provided(),
        breed_split_pct=provided(float(profile.breed_split_pct)),
        age_years=provided(float(profile.age_years)),
        birthday=provided(profile.birthday) if profile.birthday else not_provided(),
        weight_kg=provided(float(profile.weight_kg)),
        sex=provided(profile.sex or profile.gender) if (profile.sex or profile.gender) else not_provided(),
        activity_level=provided(profile.activity_level) if profile.activity_level else not_provided(),
        environment=provided(profile.current_environment) if profile.current_environment else not_provided(),
        height_cm=provided(float(profile.height_cm)) if profile.height_cm is not None else not_provided(),
        bcs=provided(float(profile.bcs)) if profile.bcs is not None else not_provided(),
        monthly_budget=provided(float(profile.monthly_budget)) if profile.monthly_budget is not None else not_provided(),
        observations=[
            Observation(
                observer_role=ObserverRole.CUSTOMER,
                observation_type="observed_condition_label",
                value=str(item),
            )
            for item in profile.observed_conditions
            if item
        ],
    )


def engine_profile_from_canonical(dog: CanonicalDogInput) -> DogProfileInput:
    """Convert only when required fields are PROVIDED. No silent defaults.

    Refuses age=5 / weight=20 / name=Pet / activity=High / environment defaults.
    The application payload_adapter still applies those defaults for HTTP.
    """
    if dog.primary_breed.state == InputState.UNKNOWN:
        raise ValueError("UNKNOWN breed cannot enter breed-dependent analysis")
    error = dog.validate_for_tools()
    if error:
        raise ValueError(error.message)
    extra_missing: list[str] = []
    if dog.name.state != InputState.PROVIDED or not dog.name.value:
        extra_missing.append("name")
    if dog.environment.state != InputState.PROVIDED or not dog.environment.value:
        extra_missing.append("environment")
    if dog.activity_level.state != InputState.PROVIDED or not dog.activity_level.value:
        extra_missing.append("activity_level")
    if (
        dog.secondary_breed.state == InputState.PROVIDED
        and dog.breed_split_pct.state != InputState.PROVIDED
    ):
        extra_missing.append("breed_split_pct")
    if extra_missing:
        raise ValueError(missing_required_input(extra_missing).message)
    split = (
        float(dog.breed_split_pct.value)
        if dog.breed_split_pct.state == InputState.PROVIDED and dog.breed_split_pct.value is not None
        else 100.0
    )
    return DogProfileInput(
        name=str(dog.name.value),
        primary_breed=str(dog.primary_breed.value),
        secondary_breed=dog.secondary_breed.value if dog.secondary_breed.state == InputState.PROVIDED else None,
        breed_split_pct=split,
        age_years=float(dog.age_years.value),  # type: ignore[arg-type]
        weight_kg=float(dog.weight_kg.value),  # type: ignore[arg-type]
        current_environment=str(dog.environment.value),
        activity_level=str(dog.activity_level.value),
        sex=dog.sex.value if dog.sex.state == InputState.PROVIDED else None,
        gender=dog.sex.value if dog.sex.state == InputState.PROVIDED else None,
        birthday=dog.birthday.value if dog.birthday.state == InputState.PROVIDED else None,
        height_cm=dog.height_cm.value if dog.height_cm.state == InputState.PROVIDED else None,
        bcs=dog.bcs.value if dog.bcs.state == InputState.PROVIDED else None,
        observed_conditions=[obs.value for obs in dog.observations],
        monthly_budget=dog.monthly_budget.value if dog.monthly_budget.state == InputState.PROVIDED else None,
    )


def evidence_from_warehouse_row(row: dict[str, Any], *, warehouse_version: str | None = None) -> ScientificEvidence:
    return ScientificEvidence(
        paper_id=row.get("paper_id") or None,
        paper_name=row.get("paper_name") or None,
        paper_link=row.get("paper_link") or row.get("source_url") or None,
        publication_year=str(row["publication_year"]) if row.get("publication_year") not in (None, "") else None,
        study_type=row.get("study_type") or None,
        species=row.get("species") or None,
        scientific_quote=row.get("scientific_quote") or row.get("source_quote") or None,
        status=_status(row.get("status"), EvidenceStatus.MISSING_PROVENANCE),
        warehouse_version=warehouse_version,
        source_table=row.get("source_table"),
        relationship_ref=row.get("fact_id") or None,
    )


def fact_from_warehouse_row(row: dict[str, Any], *, warehouse_version: str | None = None) -> ScientificFact:
    evidence = evidence_from_warehouse_row(row, warehouse_version=warehouse_version)
    status = _status(row.get("status"), EvidenceStatus.MISSING_PROVENANCE)
    return ScientificFact(
        fact_id=row.get("fact_id") or None,
        subject=str(row.get("breed_name") or row.get("subject") or ""),
        relationship=str(row.get("measure_type") or row.get("relationship") or "associated_with"),
        object=str(row.get("condition_name") or row.get("object") or ""),
        value=row.get("value_number") if row.get("value_number") not in (None, "") else row.get("value"),
        unit=row.get("unit") or None,
        status=status,
        evidence=[evidence],
        provenance=[
            ProvenanceRecord(
                source_type="warehouse_row",
                source_id=row.get("fact_id") or None,
                fact_id=row.get("fact_id") or None,
                paper_id=row.get("paper_id") or None,
                source_name=row.get("paper_name") or None,
                source_link=row.get("paper_link") or row.get("source_url") or None,
                publication_year=str(row["publication_year"]) if row.get("publication_year") not in (None, "") else None,
                quote=row.get("scientific_quote") or row.get("source_quote") or None,
                study_type=row.get("study_type") or None,
                species=row.get("species") or None,
                status=status,
                warehouse_version=warehouse_version,
                engine_version=runtime_engine_version(),
                source_table=row.get("source_table"),
            )
        ],
        warehouse_version=warehouse_version,
    )


def health_from_care_model(
    care_model: dict[str, Any],
    *,
    versions: VersionStamp | None = None,
) -> HealthAnalysisResult:
    """Transport mapping from existing careModel dict. Does not compute findings."""
    stamp = versions or VersionStamp()
    findings: list[ConditionFinding] = []
    for raw in care_model.get("condition_records") or []:
        if not isinstance(raw, dict):
            continue
        prev = raw.get("prevalence") if isinstance(raw.get("prevalence"), dict) else {}
        observed = prev.get("observed")
        estimated = prev.get("estimated")
        observed_numeric = None
        if isinstance(observed, (int, float)):
            observed_numeric = float(observed)
        est_status = estimated
        findings.append(
            ConditionFinding(
                condition=str(raw.get("condition") or raw.get("label") or ""),
                pathway=raw.get("pathway"),
                status=_status(raw.get("status"), EvidenceStatus.WAREHOUSE_EVIDENCE),
                observed_prevalence=_prevalence(
                    status_raw=None if observed_numeric is not None else observed,
                    percent=observed_numeric,
                ),
                estimated_prevalence=_prevalence(status_raw=est_status),
                observed_by_breed=[
                    BreedPrevalence(
                        breed=str(item.get("breed") or ""),
                        percent=item.get("percent"),
                        ratio=item.get("ratio"),
                    )
                    for item in (prev.get("observed_by_breed") or [])
                    if isinstance(item, dict)
                ],
                contributing_traits=[
                    str(item)
                    for item in (raw.get("contributing_traits") or [])
                    if item
                ],
                preventative_targets=[
                    _target_from_dict(item) for item in (raw.get("preventative_targets") or []) if isinstance(item, dict)
                ],
                source_fact_ids=[
                    str(item.get("fact_id"))
                    for item in (raw.get("evidence") or [])
                    if isinstance(item, dict) and item.get("fact_id")
                ],
                diagnosis_claim=bool(raw.get("diagnosis_claim", False)),
            )
        )
    evidence_status = _status(care_model.get("evidence_status"))
    return HealthAnalysisResult(
        findings=findings,
        trait_associations=[
            str(item)
            for item in (care_model.get("trait_associations") or [])
            if item
        ],
        preventative_targets=[
            _target_from_dict(item)
            for item in (care_model.get("preventative_targets") or [])
            if isinstance(item, dict)
        ],
        evidence_status=evidence_status,
        prevalence_available=bool(care_model.get("prevalence_available")),
        diagnosis_claim=bool(care_model.get("diagnosis_claim", False)),
        versions=stamp,
        note=care_model.get("note"),
        provenance=[
            ProvenanceRecord(
                source_type="computation",
                capability_id="analyze_health",
                source_name="resolve_care_model",
                status=evidence_status,
                engine_version=stamp.engine_version,
                warehouse_version=stamp.warehouse_version,
                csv_hash=stamp.csv_hash,
            )
        ],
    )


def _target_from_dict(item: dict[str, Any]) -> PreventativeTarget:
    return PreventativeTarget(
        ingredient_name=item.get("ingredient_name"),
        ingredient_id=str(item["ingredient_id"]) if item.get("ingredient_id") not in (None, "") else None,
        nutrient_id=item.get("nutrient_id"),
        display=str(item.get("display") or item.get("ingredient_name") or ""),
        kind=item.get("kind"),
        breed_recommended=bool(item.get("star") or item.get("breed_recommended")),
        fact_id=item.get("fact_id"),
        status=_status(item.get("status"), EvidenceStatus.NEEDS_VALIDATION) if item.get("status") else None,
        paper_name=item.get("paper_name"),
        scientific_quote=item.get("scientific_quote"),
        paper_link=item.get("paper_link"),
        condition=item.get("condition"),
    )


def nutrition_from_requirement_profile(
    profile: dict[str, Any],
    *,
    versions: VersionStamp | None = None,
) -> NutritionAnalysisResult:
    """Transport mapping from existing requirementProfile dict."""
    stamp = versions or VersionStamp()
    nutrients: list[NutrientRequirement] = []
    raw_nutrients = profile.get("nutrients") or {}
    if isinstance(raw_nutrients, dict):
        items = raw_nutrients.values()
    else:
        items = raw_nutrients
    for item in items:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        source_label = None
        if isinstance(source, dict):
            source_label = source.get("label") or source.get("kind")
        elif source:
            source_label = str(source)
        nutrients.append(
            NutrientRequirement(
                nutrient_id=str(item.get("id") or item.get("nutrient_id") or ""),
                display=str(item.get("display") or item.get("id") or ""),
                minimum=item.get("minimum"),
                maximum=item.get("maximum"),
                unit=str(item.get("unit") or ""),
                basis=str(item.get("basis") or profile.get("basis") or "dry_matter_diet_density"),
                breed_recommended=bool(item.get("breed_recommended") or item.get("star")),
                source=source_label,
                life_stage=item.get("life_stage") or profile.get("life_stage"),
                status=EvidenceStatus.NOT_MODELED if item.get("status") == "NOT_MODELED" else EvidenceStatus.WAREHOUSE_EVIDENCE,
                daily_requirement_status=EvidenceStatus.NOT_AVAILABLE,
            )
        )
    senior = str(profile.get("senior_specific_minima") or "")
    if senior.startswith("NOT_AVAILABLE"):
        senior_status = EvidenceStatus.NOT_AVAILABLE
    elif senior == "NOT_APPLICABLE":
        senior_status = EvidenceStatus.NOT_APPLICABLE
    else:
        senior_status = EvidenceStatus.NOT_APPLICABLE
    return NutritionAnalysisResult(
        dog_size=profile.get("dog_size"),
        life_stage=profile.get("life_stage"),
        basis=str(profile.get("basis") or "dry_matter_diet_density"),
        nutrients=nutrients,
        not_modeled=[
            str(item.get("id") if isinstance(item, dict) else item)
            for item in (profile.get("not_modeled") or [])
        ],
        senior_specific_minima=senior_status,
        senior_specific_minima_note=senior or None,
        complete_diet_claim=bool(profile.get("complete_diet_claim", False)),
        breed_used_for_nutrient_minima=bool(profile.get("breed_used_for_nutrient_minima", False)),
        versions=stamp,
        provenance=[
            ProvenanceRecord(
                source_type="computation",
                capability_id="calculate_nutrition",
                source_name=str((profile.get("source") or {}).get("label") or "requirement_profile"),
                status=EvidenceStatus.WAREHOUSE_EVIDENCE,
                engine_version=stamp.engine_version,
                warehouse_version=stamp.warehouse_version,
                csv_hash=stamp.csv_hash,
            )
        ],
    )


def bundles_from_search_envelope(
    envelope: dict[str, Any],
    *,
    versions: VersionStamp | None = None,
) -> BundleSearchResult:
    """Transport mapping from package_options + optimizer provenance."""
    stamp = versions or VersionStamp()
    options = envelope.get("package_options") or {}
    prov = envelope.get("optimizer_provenance") or envelope.get("provenance") or {}
    funnel_raw = prov.get("filter_funnel") if isinstance(prov, dict) else None
    displayed = (funnel_raw or {}).get("displayed") if isinstance(funnel_raw, dict) else {}
    funnel = None
    if isinstance(funnel_raw, dict):
        funnel = FilterFunnel(
            generated=funnel_raw.get("generated"),
            evaluated=funnel_raw.get("evaluated"),
            life_stage_species_structurally_eligible=funnel_raw.get("life_stage_species_structurally_eligible"),
            nutrient_calculated=funnel_raw.get("nutrient_calculated"),
            passed_minimum_filter=funnel_raw.get("passed_minimum_filter"),
            passed_maximum_filter=funnel_raw.get("passed_maximum_filter"),
            nutrient_valid=funnel_raw.get("nutrient_valid"),
            non_dominated=funnel_raw.get("non_dominated"),
            with_any_care_coverage=funnel_raw.get("with_any_care_coverage"),
            full_care_coverage=funnel_raw.get("full_care_coverage"),
            within_budget=funnel_raw.get("within_budget"),
            satisfy_essential=funnel_raw.get("satisfy_essential"),
            satisfy_balanced=funnel_raw.get("satisfy_balanced"),
            satisfy_optimal=funnel_raw.get("satisfy_optimal"),
            displayed_essential=(displayed or {}).get("essential"),
            displayed_balanced=(displayed or {}).get("balanced"),
            displayed_optimal=(displayed or {}).get("optimal"),
            note=funnel_raw.get("note"),
        )
    optimizer = OptimizerProvenance(
        algorithm=str(prov.get("algorithm") or OPTIMIZER_ALGORITHM),
        search_method=prov.get("search_method"),
        candidate_count=prov.get("candidate_count"),
        total_possible_subsets=prov.get("total_possible_subsets"),
        evaluated_count=prov.get("evaluated_count"),
        valid_count=prov.get("valid_count"),
        rejected_count=prov.get("rejected_count"),
        filter_funnel=funnel,
        ranking_rules=list(prov.get("ranking_rules") or []),
        llm_used=bool(prov.get("llm_used", False)),
        constraint_failures=[
            str(key) for key in (prov.get("constraint_failures") or {})
        ]
        if isinstance(prov.get("constraint_failures"), dict)
        else [str(item) for item in (prov.get("constraint_failures") or [])],
    )
    result = BundleSearchResult(
        essential=[_bundle_option(item, BundleTier.ESSENTIAL) for item in (options.get("essential") or []) if isinstance(item, dict)],
        balanced=[_bundle_option(item, BundleTier.BALANCED) for item in (options.get("balanced") or []) if isinstance(item, dict)],
        optimal=[_bundle_option(item, BundleTier.OPTIMAL) for item in (options.get("optimal") or []) if isinstance(item, dict)],
        optimizer=optimizer,
        versions=stamp,
        provenance=[
            ProvenanceRecord(
                source_type="computation",
                capability_id=OPTIMIZER_ALGORITHM,
                source_name=OPTIMIZER_ALGORITHM,
                status=EvidenceStatus.WAREHOUSE_EVIDENCE,
                engine_version=stamp.engine_version,
                warehouse_version=stamp.warehouse_version,
                csv_hash=stamp.csv_hash,
            )
        ],
    )
    if not (result.essential or result.balanced or result.optimal):
        result = result.model_copy(update={"status": ToolErrorCode.NO_VALID_BUNDLES})
    return result


def _bundle_option(raw: dict[str, Any], tier: BundleTier) -> BundleOption:
    products = []
    for item in raw.get("products") or []:
        if isinstance(item, dict) and item.get("product_id"):
            products.append(
                ProductIdentity(
                    product_id=str(item.get("product_id")),
                    product_name=str(item.get("product_name") or item.get("name") or item.get("product_id")),
                    category=item.get("category") or item.get("product_category"),
                    brand=item.get("brand"),
                )
            )
    ids = [str(x) for x in (raw.get("product_ids") or [p.product_id for p in products])]
    ledger = None
    ledger_raw = raw.get("nutrition_ledger")
    if isinstance(ledger_raw, dict):
        rows = []
        for row in ledger_raw.get("nutrients") or []:
            if not isinstance(row, dict):
                continue
            rows.append(
                NutrientLedgerRow(
                    nutrient_id=str(row.get("nutrient_id") or row.get("nutrient") or ""),
                    display=row.get("display") or row.get("nutrient_name"),
                    unit=row.get("unit"),
                    basis=row.get("basis"),
                    required_minimum=row.get("required_minimum"),
                    allowed_maximum=row.get("allowed_maximum"),
                    actual=row.get("actual"),
                    daily_amount=row.get("daily_amount"),
                    status=row.get("status"),
                    breed_recommended=bool(row.get("breed_recommended") or row.get("star")),
                )
            )
        ledger = NutrientLedger(
            nutrients=rows,
            daily_dm_g=ledger_raw.get("daily_dm_g"),
            daily_dm_kg=ledger_raw.get("daily_dm_kg"),
            basis=str(ledger_raw.get("basis") or "dry_matter_diet_density"),
            daily_requirement_note=ledger_raw.get("daily_requirement_note"),
        )
    return BundleOption(
        bundle_id=str(raw.get("bundle_id") or ""),
        tier=tier,
        products=products,
        product_ids=ids,
        monthly_cost=raw.get("monthly_cost"),
        annual_cost=raw.get("annual_cost"),
        constraint_status=raw.get("constraint_status"),
        rejection_reason=raw.get("rejection_reason"),
        care_pathways=[str(x) for x in (raw.get("care_pathways") or [])],
        ranking_rationale=raw.get("ranking_rationale") or raw.get("why"),
        nutrient_ledger=ledger,
    )


def product_from_catalog_row(row: dict[str, Any]) -> ProductRecord:
    return ProductRecord(
        identity=ProductIdentity(
            product_id=str(row.get("product_id") or ""),
            product_name=str(row.get("product_name") or row.get("product_id") or ""),
            category=row.get("product_category") or row.get("category"),
            brand=row.get("brand"),
        ),
    )
