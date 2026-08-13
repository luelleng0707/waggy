"""
Central formula registry — single source of formula IDs + metadata.

No equation text. Used by EngineTrace and Validation Console.
Does not execute formulas.
"""

from __future__ import annotations

from typing import Any

from app.agent.version import ALGORITHM_VERSION

# Stable IDs (import these everywhere — do not redefine strings)
FORMULA_PROFILE = "PROFILE_NORMALIZE_V2_1"
FORMULA_BREED = "BREED_RESOLVE_V2_1"
FORMULA_TRAIT = "TRAIT_BLEND_V2_1"
FORMULA_RISK = "RISK_V2_1"
FORMULA_RISK_TRACE = "RISK_TRACE_V1"
FORMULA_NUTRIENT = "NUTRIENT_TARGET_V2_1"
FORMULA_NUTRIENT_EST = "NUTRIENT_EST_V1"
FORMULA_FRAC_ORDER = "ING_FRAC_ORDER_V1"
FORMULA_ACTIVITY = "ACTIVITY_V2_1"
FORMULA_PRODUCT = "PRODUCT_MATCH_V2_1"
FORMULA_PACKAGE = "PACKAGE_OPTIMIZER_V2_1"
FORMULA_COVERAGE = "COVERAGE_V2_1"
FORMULA_CONDITION_SUPPORT = "CONDITION_SUPPORT_V1"
FORMULA_EVIDENCE = "EVIDENCE_RANK_V2_1"
FORMULA_VALIDATION = "VALIDATION_V2_1"
FORMULA_ASSESSMENT = "ASSESSMENT_PROJECT_V1"
FORMULA_CONF = "CONF_V1"


def _entry(
    formula_id: str,
    *,
    purpose: str,
    owner_module: str,
    inputs: list[str],
    outputs: list[str],
    depends_on: list[str] | None = None,
    csv_tables: list[str] | None = None,
    production: bool = True,
    emits_ledger: bool = False,
    display_name: str | None = None,
    callable_path: str | None = None,
    consumes: list[str] | None = None,
    produces: list[str] | None = None,
    trace_schema: str = "formula_execution.v2",
) -> dict[str, Any]:
    return {
        "formula_id": formula_id,
        "formula_name": display_name or purpose,
        "display_name": display_name or purpose,
        "purpose": purpose,
        "owner_module": owner_module,
        "callable_path": callable_path or owner_module,
        "inputs": inputs,
        "outputs": outputs,
        "depends_on": depends_on or [],
        "csv_tables": csv_tables or [],
        "input_tables": csv_tables or [],
        "consumes": consumes or depends_on or [],
        "produces": produces or outputs,
        "trace_schema": trace_schema if emits_ledger else None,
        "version": ALGORITHM_VERSION,
        "production": production,
        "emits_ledger": emits_ledger,
        "equation_exposed": False,
    }


FORMULA_REGISTRY: dict[str, dict[str, Any]] = {
    FORMULA_PROFILE: _entry(
        FORMULA_PROFILE,
        purpose="Normalize DogProfile payload into analyze.profile",
        owner_module="app.api.payload_adapter",
        inputs=["raw request body"],
        outputs=["profile"],
    ),
    FORMULA_BREED: _entry(
        FORMULA_BREED,
        purpose="Resolve breed names via aliases and load breed rows",
        owner_module="app.formulas.stages.biological",
        inputs=["breeds", "breed_split"],
        outputs=["resolved_breeds"],
        csv_tables=["breeds", "breed_aliases"],
    ),
    FORMULA_TRAIT: _entry(
        FORMULA_TRAIT,
        purpose="Blend trait fields across resolved breeds",
        owner_module="app.formulas.stages.biological",
        inputs=["resolved_breeds"],
        outputs=["trait_summary"],
        depends_on=[FORMULA_BREED],
        csv_tables=["trait_purposes", "trait_attribute_explanations"],
    ),
    FORMULA_RISK: _entry(
        FORMULA_RISK,
        purpose="Rank condition risks (locked parity path)",
        display_name="Condition Risk Ranking",
        owner_module="app.formulas.stages.health_risk",
        callable_path="app.formulas.stages.health_risk.compute_risks",
        inputs=["traits", "profile", "observed_conditions"],
        outputs=["healthInsights", "risk_percent", "confidence_percent"],
        depends_on=[FORMULA_TRAIT, FORMULA_BREED],
        csv_tables=[
            "breed_conditions",
            "size_conditions",
            "bodytype_conditions",
            "trait_interactions",
            "trait_benefits",
            "mixed_breed_matrix",
        ],
        emits_ledger=True,
    ),
    FORMULA_RISK_TRACE: _entry(
        FORMULA_RISK_TRACE,
        purpose="Observability ledger of risk modifiers (does not recompute RISK_V2_1)",
        owner_module="app.inference.risk",
        inputs=["healthInsights", "calculationTrace"],
        outputs=["modifier_steps"],
        depends_on=[FORMULA_RISK],
        production=False,
        emits_ledger=True,
    ),
    FORMULA_NUTRIENT: _entry(
        FORMULA_NUTRIENT,
        purpose="Map priority conditions to nutrient / ingredient targets",
        display_name="Condition → Nutrient Targets",
        owner_module="app.agent.ingredient_engine",
        callable_path="app.agent.ingredient_engine.map_ingredients",
        inputs=["risks", "weight_kg"],
        outputs=["nutritionalTargets", "ingredients"],
        depends_on=[FORMULA_RISK],
        csv_tables=["condition_ingredients_sci", "condition_ingredients_prev", "ingredient_aliases"],
        emits_ledger=True,
    ),
    FORMULA_NUTRIENT_EST: _entry(
        FORMULA_NUTRIENT_EST,
        purpose="Estimate nutrient from ingredient fractions × densities (opt-in)",
        owner_module="app.inference.ingredient",
        inputs=["fractions", "ingredient_nutrient_estimates"],
        outputs=["estimated_nutrient"],
        csv_tables=["ingredient_nutrient_estimates"],
        production=False,
    ),
    FORMULA_FRAC_ORDER: _entry(
        FORMULA_FRAC_ORDER,
        purpose="Estimate ingredient mass fractions from declaration order (opt-in)",
        owner_module="app.inference.ingredient",
        inputs=["ordered ingredients"],
        outputs=["fractions"],
        production=False,
    ),
    FORMULA_ACTIVITY: _entry(
        FORMULA_ACTIVITY,
        purpose="Activity prescription from rules + condition activities",
        owner_module="app.agent.response_assembler",
        inputs=["activity_level", "traits", "conditions"],
        outputs=["activityRecommendations"],
        csv_tables=["activity_prescription_rules", "condition_activities"],
    ),
    FORMULA_PRODUCT: _entry(
        FORMULA_PRODUCT,
        purpose="Match catalog products to nutrient targets",
        owner_module="app.formulas.stages.optimization / package_optimizer",
        inputs=["targets", "catalog"],
        outputs=["productRecommendations"],
        depends_on=[FORMULA_NUTRIENT],
        csv_tables=["products", "product_components", "product_pricing"],
    ),
    FORMULA_COVERAGE: _entry(
        FORMULA_COVERAGE,
        purpose="provided / recommended coverage ratio",
        owner_module="app.agent.package_optimizer / inference.nutrition",
        inputs=["provided", "recommended"],
        outputs=["coverage"],
        depends_on=[FORMULA_PRODUCT, FORMULA_NUTRIENT],
    ),
    FORMULA_PACKAGE: _entry(
        FORMULA_PACKAGE,
        purpose="Build three-tier wellness packages",
        display_name="Tier Package Optimizer",
        owner_module="app.agent.package_optimizer",
        callable_path="app.agent.package_optimizer.build_optimized_packages",
        inputs=["candidates", "targets", "goals"],
        outputs=["wellnessPackages"],
        depends_on=[FORMULA_PRODUCT, FORMULA_COVERAGE],
        csv_tables=["package_tiers", "product_defaults", "product_functions"],
        emits_ledger=True,
    ),
    FORMULA_CONDITION_SUPPORT: _entry(
        FORMULA_CONDITION_SUPPORT,
        purpose="Σ coverage × evidence_weight × priority (opt-in, disabled)",
        owner_module="app.inference.nutrition",
        inputs=["coverage terms"],
        outputs=["support_score"],
        production=False,
    ),
    FORMULA_EVIDENCE: _entry(
        FORMULA_EVIDENCE,
        purpose="Attach and rank scientific evidence for conditions/ingredients",
        owner_module="app.agent.response_assembler",
        inputs=["conditions", "ingredients"],
        outputs=["scientificEvidence"],
        csv_tables=["clinical_evidence_base", "ingredient_evidence_sci", "ingredient_evidence_prev"],
    ),
    FORMULA_VALIDATION: _entry(
        FORMULA_VALIDATION,
        purpose="Compare estimates to published prevalence slots",
        owner_module="app.agent.calculation_trace / assessment",
        inputs=["healthInsights"],
        outputs=["validation items"],
        depends_on=[FORMULA_RISK],
    ),
    FORMULA_ASSESSMENT: _entry(
        FORMULA_ASSESSMENT,
        purpose="Project frozen analyze into ClinicalAssessment modules",
        owner_module="app.data.clinical_assessment",
        inputs=["analyze"],
        outputs=["assessment modules"],
        depends_on=[FORMULA_RISK, FORMULA_PACKAGE, FORMULA_EVIDENCE],
        production=True,
    ),
    FORMULA_CONF: _entry(
        FORMULA_CONF,
        purpose="Confidence source-class ladder (opt-in metadata)",
        owner_module="app.inference.confidence",
        inputs=["source_class"],
        outputs=["confidence_percent"],
        production=False,
    ),
}


def formula_list() -> list[dict[str, Any]]:
    return list(FORMULA_REGISTRY.values())


def formula_dependency_edges() -> list[dict[str, str]]:
    edges = []
    for fid, meta in FORMULA_REGISTRY.items():
        for dep in meta.get("depends_on") or []:
            edges.append({"from": dep, "to": fid})
    return edges


def get_formula(formula_id: str) -> dict[str, Any] | None:
    return FORMULA_REGISTRY.get(formula_id)
