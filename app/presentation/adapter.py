"""Shared read-only adapter for customer/business/developer presentations."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def analysis_signature(analyze: dict[str, Any]) -> str:
    """Stable signature proving all surfaces came from one analysis payload."""
    payload = {
        "profile": analyze.get("profile"),
        "healthInsights": analyze.get("healthInsights"),
        "nutritionalTargets": analyze.get("nutritionalTargets"),
        "productRecommendations": analyze.get("productRecommendations"),
        "wellnessPackages": analyze.get("wellnessPackages"),
        "scientificEvidence": analyze.get("scientificEvidence"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_customer_presentation(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    profile = analyze.get("profile") or analyze.get("pet") or {}
    return {
        "surface": "customer",
        "dog": {
            "name": profile.get("pet_name") or profile.get("name"),
            "breeds": profile.get("breeds") or [],
            "weight_kg": profile.get("weight_kg"),
            "age_years": profile.get("age_years"),
        },
        "wellness": {
            "health_insights": analyze.get("healthInsights") or [],
            "products": analyze.get("productRecommendations") or [],
            "packages": analyze.get("wellnessPackages") or [],
            "monthly_plan": analyze.get("monthly_plan") or {},
            "yearly_plan": analyze.get("yearly_plan") or {},
            "evidence": analyze.get("scientificEvidence") or [],
        },
        "assessment_summary": (assessment or {}).get("summary") or {},
    }


def build_business_presentation(analyze: dict[str, Any], assessment: dict[str, Any] | None) -> dict[str, Any]:
    products = analyze.get("productRecommendations") or []
    packages = analyze.get("wellnessPackages") or []
    monthly = analyze.get("monthly_plan") or {}
    yearly = analyze.get("yearly_plan") or {}
    health = analyze.get("healthInsights") or []
    return {
        "surface": "business",
        "overview": {
            "dogs_analyzed": 1,
            "priority_health_opportunities": len(health),
            "product_count": len(products),
            "package_count": len(packages),
            "evidence_count": len(analyze.get("scientificEvidence") or []),
            "estimated_business_opportunity": monthly.get("total_cost") or "NOT AVAILABLE",
        },
        "portfolio": {
            "products": products,
            "packages": packages,
            "product_gaps": "NOT AVAILABLE",
            "portfolio_expansion": "NOT AVAILABLE",
        },
        "health_opportunities": [
            {
                "condition": item.get("title") or item.get("condition"),
                "observed_prevalence": item.get("observed_breed_prevalence_percent")
                if item.get("observed_breed_prevalence_percent") is not None
                else "NOT AVAILABLE",
                "estimated_prevalence": item.get("biological_risk_percent")
                if item.get("biological_risk_percent") is not None
                else "NOT AVAILABLE",
                "evidence_status": "AVAILABLE"
                if item.get("evidence_count") or item.get("source_count")
                else "NOT AVAILABLE",
                "breed_relevance": item.get("breed_relevance") or "NOT AVAILABLE",
                "business_relevance": item.get("priority_score") or "NOT AVAILABLE",
            }
            for item in health
            if isinstance(item, dict)
        ],
        "financial_model": {
            "monthly_total": monthly.get("total_cost") or "NOT AVAILABLE",
            "yearly_total": yearly.get("total_cost") or "NOT AVAILABLE",
            "discount": monthly.get("discount") or yearly.get("discount") or "NOT AVAILABLE",
            "margin": "NOT AVAILABLE",
            "recurring_price": monthly.get("monthly_equivalent") or "NOT AVAILABLE",
            "package_pricing": [
                {
                    "tier": p.get("tier"),
                    "monthly_cost": p.get("monthly_cost", "NOT AVAILABLE"),
                    "yearly_cost": p.get("yearly_cost", "NOT AVAILABLE"),
                }
                for p in packages
                if isinstance(p, dict)
            ],
        },
        "assessment_summary": (assessment or {}).get("summary") or {},
    }


def build_developer_presentation(validation_console: dict[str, Any] | None) -> dict[str, Any]:
    doc = validation_console or {}
    return {
        "surface": "developer",
        "summary": doc.get("execution_status_summary") or {},
        "execution_records": doc.get("execution_records") or doc.get("formula_executions") or [],
        "runtime_stage_flow": doc.get("runtime_stage_flow") or [],
    }


def build_three_surface_presentations(
    analyze: dict[str, Any],
    assessment: dict[str, Any] | None = None,
    validation_console: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    signature = analysis_signature(analyze)
    return {
        "schema": "three_surface_presentation.v1",
        "analysis_signature": signature,
        "presentation_correlation_id": correlation_id or "NOT AVAILABLE",
        "customer": build_customer_presentation(analyze, assessment),
        "business": build_business_presentation(analyze, assessment),
        "developer": build_developer_presentation(validation_console),
    }
