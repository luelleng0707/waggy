"""
Standardized clinical report models (Phase 11).

Each builder returns a deterministic dictionary. UI renders these only —
no CSV reads, no clinical assembly in the browser.
"""

from __future__ import annotations

from typing import Any

from app.agent.utils import DataRepository
from app.data.report_generator import ReportGenerator, build_standard_report


class BreedAnalysisReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        profile = self._analyze.get("profile") or self._analyze.get("pet") or {}
        biology = self._analyze.get("biology") or {}
        return self._gen._breed_analysis(biology, profile)


class RiskAnalysisReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        profile = self._analyze.get("profile") or self._analyze.get("pet") or {}
        biology = self._analyze.get("biology") or {}
        return self._gen._risk_analysis(self._analyze, biology, profile)


class NutritionReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        return self._gen._nutrition(self._analyze)


class PackageComparisonReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        return self._gen._packages(self._analyze)


class PackageDetailReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any], tier: str):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze
        self._tier = tier

    def build(self) -> dict[str, Any] | None:
        reports = self._gen._package_detail_reports(self._analyze)
        return reports.get(self._tier)


class ProductAnalysisReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any], product_id: str):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze
        self._product_id = product_id

    def build(self) -> dict[str, Any] | None:
        reports = self._gen._product_detail_reports(self._analyze)
        return reports.get(self._product_id)


class ScientificEvidenceReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        return self._gen._references(self._analyze)


class ActivityReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        profile = self._analyze.get("profile") or self._analyze.get("pet") or {}
        biology = self._analyze.get("biology") or {}
        return self._gen._activity(self._analyze, biology, profile)


class GroomingPlanReport:
    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._gen = ReportGenerator(repo)
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        return self._gen._grooming(self._analyze)


class AnnualPlanReport:
    """365-day plans derived from optimized packages (yearly first, monthly = yearly/12)."""

    def __init__(self, repo: DataRepository, analyze: dict[str, Any]):
        self._repo = repo
        self._analyze = analyze

    def build(self) -> dict[str, Any]:
        packages = self._analyze.get("wellnessPackages") or []
        plans = []
        for pkg in packages:
            plan = pkg.get("plan_365") or {}
            plans.append(
                {
                    "tier": pkg.get("tier"),
                    "title": pkg.get("title"),
                    "yearly_cost": pkg.get("yearly_cost") or plan.get("yearly_cost"),
                    "monthly_cost_derived": pkg.get("monthly_cost")
                    or plan.get("monthly_cost_derived"),
                    "products": plan.get("products") or [],
                    "coverage_score": pkg.get("coverage_score"),
                    "overall_score": pkg.get("overall_score"),
                }
            )
        return {
            "id": "annual_plan",
            "title": "Annual Plan",
            "priority": 85,
            "summary": "365-day inventory and cost plans for each optimized care package.",
            "score": None,
            "widgets": [
                {
                    "type": "ledger",
                    "title": f"{p.get('title')} · 365-day",
                    "columns": ["Product", "Daily", "Packages/year", "Yearly cost"],
                    "rows": [
                        [
                            row.get("product_name"),
                            row.get("daily_serving"),
                            row.get("packages_needed"),
                            row.get("yearly_cost"),
                        ]
                        for row in (p.get("products") or [])
                    ],
                    "meta": {
                        "yearly_cost": p.get("yearly_cost"),
                        "monthly_cost_derived": p.get("monthly_cost_derived"),
                    },
                }
                for p in plans
            ],
            "references": [],
            "plans": plans,
        }


def build_all_report_models(repo: DataRepository, analyze: dict[str, Any]) -> dict[str, Any]:
    """Envelope of named models + full standard report for the UI."""
    standard = build_standard_report(repo, analyze)
    return {
        "standard_report": standard,
        "breed_analysis": BreedAnalysisReport(repo, analyze).build(),
        "risk_analysis": RiskAnalysisReport(repo, analyze).build(),
        "nutrition": NutritionReport(repo, analyze).build(),
        "package_comparison": PackageComparisonReport(repo, analyze).build(),
        "scientific_evidence": ScientificEvidenceReport(repo, analyze).build(),
        "activity": ActivityReport(repo, analyze).build(),
        "grooming": GroomingPlanReport(repo, analyze).build(),
        "annual_plan": AnnualPlanReport(repo, analyze).build(),
        "package_details": {
            tier: PackageDetailReport(repo, analyze, tier).build()
            for tier in ("essential", "balanced", "optimal")
        },
        "product_details": standard.get("product_reports") or {},
    }
