"""Intentional projection of canonical analysis for explanation. Not canonical.analyze."""

from __future__ import annotations

from typing import Any

from app.ai.models import ExplanationContext, RoleName
from app.ai.version import WAGGY_EXPLANATION_CONTEXT_SCHEMA
from app.state.recalculation import explain_from_envelopes, package_membership_difference
from app.state.version import WAGGY_RECALCULATION_EXPLANATION_SCHEMA

_DOG_KEYS = (
    "name",
    "pet_name",
    "breeds",
    "primary_breed",
    "secondary_breed",
    "age_years",
    "weight_kg",
    "activity_level",
    "current_environment",
    "sex",
    "observed_conditions",
)

_FINDING_KEYS = ("title", "explanation", "why", "priority", "status", "source_name")
_NUTRIENT_KEYS = (
    "nutrient",
    "name",
    "min",
    "max",
    "unit",
    "status",
    "source_status",
    "target",
)
_PRODUCT_KEYS = ("product_id", "name", "product_name", "why_selected", "reason", "monthly_cost")


def _pick(item: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: item[key] for key in keys if key in item and item[key] not in (None, "")}


def _dog_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    profile = ((canonical.get("input") or {}).get("dog_profile")) or {}
    if not isinstance(profile, dict):
        profile = {}
    return _pick(profile, _DOG_KEYS)


def _project_evidence(rows: list[Any]) -> tuple[list[dict[str, Any]], str]:
    if not isinstance(rows, list) or not rows:
        return [], "NOT_AVAILABLE"
    out: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        status = raw.get("status") or raw.get("evidence_status") or "NOT_AVAILABLE"
        out.append(
            {
                "paper_name": raw.get("paper_name") or raw.get("source_name") or raw.get("label"),
                "paper_link": raw.get("paper_link") or raw.get("url") or raw.get("link"),
                "publication_year": raw.get("publication_year") or raw.get("year"),
                "study_type": raw.get("study_type"),
                "scientific_quote": raw.get("scientific_quote") or raw.get("quote"),
                "species": raw.get("species"),
                "status": status,
            }
        )
    if not out:
        return [], "NOT_AVAILABLE"
    return out, "SUPPLIED"


def _flatten_packages(canonical: dict[str, Any], bundle_id: str | None) -> list[dict[str, Any]]:
    opt = canonical.get("package_optimization") or {}
    options = opt.get("package_options") if isinstance(opt, dict) else {}
    rows: list[dict[str, Any]] = []
    if isinstance(options, dict):
        for tier, items in options.items():
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                bid = item.get("bundle_id")
                if bundle_id and bid != bundle_id:
                    continue
                products = []
                for prod in item.get("products") or item.get("product_ids") or []:
                    if isinstance(prod, dict):
                        products.append(_pick(prod, _PRODUCT_KEYS + ("product_id",)))
                    else:
                        products.append({"product_id": str(prod)})
                rows.append(
                    {
                        "bundle_id": bid,
                        "tier": item.get("tier") or tier,
                        "monthly_cost": item.get("monthly_cost"),
                        "purpose": item.get("purpose") or item.get("why_ranked_here"),
                        "why_selected": item.get("why_selected"),
                        "products": products,
                    }
                )
    if bundle_id and not rows:
        for pkg in opt.get("tiers") or []:
            if isinstance(pkg, dict):
                rows.append(
                    {
                        "bundle_id": pkg.get("package_id") or pkg.get("bundle_id"),
                        "tier": pkg.get("tier"),
                        "monthly_cost": pkg.get("monthly_cost"),
                        "products": pkg.get("products") or [],
                    }
                )
    return rows


def _optimizer_slice(canonical: dict[str, Any]) -> dict[str, Any]:
    opt = canonical.get("package_optimization") or {}
    search = opt.get("search") if isinstance(opt, dict) else {}
    if not isinstance(search, dict):
        search = {}
    return {
        "algorithm": opt.get("algorithm") if isinstance(opt, dict) else None,
        "search_method": search.get("search_method"),
        "evaluated_count": search.get("evaluated_count"),
        "valid_count": search.get("valid_count"),
        "llm_used": search.get("llm_used", False),
        "budget_status": search.get("balanced_budget_status") or search.get("budget_status"),
    }


def package_difference(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any] | None:
    if not previous:
        return None
    return package_membership_difference(explain_from_envelopes(previous, current))


def _system_recalculation(
    canonical: dict[str, Any],
    previous_canonical: dict[str, Any] | None,
    supplied: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if previous_canonical:
        return explain_from_envelopes(previous_canonical, canonical)
    if isinstance(supplied, dict) and supplied.get("schema") == WAGGY_RECALCULATION_EXPLANATION_SCHEMA:
        return supplied
    return None


def build_explanation_context(
    canonical: dict[str, Any],
    *,
    analysis_signature: str,
    role: RoleName = "customer",
    bundle_id: str | None = None,
    previous_canonical: dict[str, Any] | None = None,
    recalculation: dict[str, Any] | None = None,
) -> ExplanationContext:
    science = canonical.get("scientific_analysis") if isinstance(canonical.get("scientific_analysis"), dict) else {}
    matching = canonical.get("product_matching") if isinstance(canonical.get("product_matching"), dict) else {}
    findings_raw = science.get("findings") or []
    findings = [_pick(item, _FINDING_KEYS) for item in findings_raw if isinstance(item, dict)]
    nutrients = [_pick(item, _NUTRIENT_KEYS) for item in (science.get("nutrient_targets") or []) if isinstance(item, dict)]
    products = [_pick(item, _PRODUCT_KEYS) for item in (matching.get("recommendations") or []) if isinstance(item, dict)]
    evidence, evidence_status = _project_evidence(science.get("evidence") or [])
    system = canonical.get("system") if isinstance(canonical.get("system"), dict) else {}
    warehouse = science.get("warehouse_status") if isinstance(science.get("warehouse_status"), dict) else {}
    system_recalculation = _system_recalculation(canonical, previous_canonical, recalculation)
    return ExplanationContext.model_validate(
        {
            "schema": WAGGY_EXPLANATION_CONTEXT_SCHEMA,
            "analysis_signature": analysis_signature,
            "role": role,
            "dog": _dog_from_canonical(canonical),
            "findings": findings,
            "nutrient_targets": nutrients,
            "products": products,
            "packages": _flatten_packages(canonical, bundle_id),
            "selected_bundle_id": bundle_id,
            "evidence": evidence,
            "evidence_status": evidence_status,
            "optimizer": _optimizer_slice(canonical),
            "uncertainty": {
                "warnings": system.get("warnings") or [],
                "warehouse_status": warehouse,
                "matcher_limitations": matching.get("limitations"),
            },
            "package_difference": (
                package_membership_difference(system_recalculation)
                if system_recalculation
                else package_difference(previous_canonical, canonical)
            ),
            "recalculation": system_recalculation,
        }
    )


def canonical_signature(canonical: dict[str, Any], fallback: str) -> str:
    return str(canonical.get("analysis_id") or fallback)
