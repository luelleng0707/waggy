"""Single-page journey view-model assembler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.ui.renderer.diary import DiaryRenderer
from app.ui.renderer.home import HomeRenderer, HomePageVM
from app.ui.renderer.shop import ShopRenderer
from app.ui.renderer.wellness import (
    NutritionTraceVM,
    PackageCardVM,
    PackageDetailVM,
    ProductAnalysisVM,
    WellnessRenderer,
)


@dataclass
class PriorityRowVM:
    condition: str
    prevalence_display: str


@dataclass
class TraitBenefitVM:
    title: str
    detail: str


@dataclass
class TraitWeaknessVM:
    trait: str
    condition: str
    prevalence_display: str


@dataclass
class NutritionPriorityVM:
    ingredient: str
    daily_target: str
    monthly_target: str
    supports: str


@dataclass
class WellnessRecommendationVM:
    title: str
    detail: str


@dataclass
class JourneyPageVM:
    home: HomePageVM
    environment_rows: list[dict[str, str]]
    trait_labels: list[str]
    trait_benefits: list[TraitBenefitVM]
    trait_weaknesses: list[TraitWeaknessVM]
    priorities: list[PriorityRowVM]
    nutrition_priorities: list[NutritionPriorityVM]
    wellness_recommendations: list[WellnessRecommendationVM]
    packages: list[PackageCardVM]
    package_detail: PackageDetailVM
    nutrition_traces: list[NutritionTraceVM]
    product_analysis: ProductAnalysisVM | None
    shop_items: list[dict[str, str]]
    diary_selected_label: str
    diary_logs: list[dict[str, str]]


class JourneyRenderer:
    """Assembles all section view models for the continuous scroll page."""

    def __init__(self, repo: DataRepository):
        self.repo = repo
        self.home_renderer = HomeRenderer()
        self.wellness_renderer = WellnessRenderer(repo)
        self.shop_renderer = ShopRenderer()
        self.diary_renderer = DiaryRenderer()

    def build(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        package_title: str,
        product_name: str | None,
        diary_day: str,
    ) -> JourneyPageVM:
        home = self.home_renderer.build(report)
        wellness_home = self.wellness_renderer.build_home(report)
        package_detail = self.wellness_renderer.build_package_detail(report, profile, package_title)
        nutrition = self.wellness_renderer.build_full_nutrition_report(report, profile, package_title)

        if not product_name and package_detail.products:
            product_name = package_detail.products[0].name
        product_analysis = None
        if product_name and product_name != "—":
            product_analysis = self.wellness_renderer.build_product_analysis(
                report, profile, package_title, product_name
            )

        shop_vm = self.shop_renderer.build(
            report, self.repo.product_catalog(), self.repo.product_pricing()
        )
        diary_vm = self.diary_renderer.build(diary_day)

        traits = report.get("biology", {}).get("trait_summary", [])[:8]
        if not traits:
            traits = ["large", "athletic", "double-coat", "high"]

        trait_benefits = [
            TraitBenefitVM(
                title=str(h.get("title", "Wellness Support")),
                detail=str(h.get("why_this_matters", h.get("explanation", ""))),
            )
            for h in report.get("healthInsights", [])[:6]
        ]

        trait_weaknesses = []
        for row in report.get("epidemiology", {}).get("breed_evidence_detail", [])[:6]:
            prev = float(row.get("prevalence_pct", row.get("prevalence", 0)))
            if prev <= 1:
                prev *= 100
            trait_weaknesses.append(
                TraitWeaknessVM(
                    trait=str(row.get("breed", "Breed")),
                    condition=str(row.get("condition", "")).replace("_", " ").title(),
                    prevalence_display=f"{prev:.1f}%",
                )
            )

        priorities = []
        for row in report.get("epidemiology", {}).get("priority_conditions", [])[:6]:
            prev = float(row.get("prevalence", row.get("weighted_priority_score", 0)))
            pct = prev * 100 if prev <= 1 else prev
            priorities.append(
                PriorityRowVM(
                    condition=str(row.get("condition", "")).replace("_", " ").title(),
                    prevalence_display=f"{pct:.1f}%",
                )
            )

        nutrition_priorities = []
        for target in report.get("nutritionalTargets", [])[:8]:
            supports = target.get("supports_goals") or target.get("for_conditions") or []
            nutrition_priorities.append(
                NutritionPriorityVM(
                    ingredient=str(target.get("ingredient", "")),
                    daily_target=str(target.get("daily_target", "")),
                    monthly_target=str(target.get("monthly_target", "")),
                    supports=", ".join(str(s) for s in supports) if supports else "Core wellness",
                )
            )

        wellness_recommendations = []
        for insight in report.get("wellness_summary", {}).get("analysis_detail", [])[:6]:
            wellness_recommendations.append(
                WellnessRecommendationVM(
                    title=str(insight.get("title", "")),
                    detail=str(insight.get("explanation", "")),
                )
            )
        if not wellness_recommendations:
            for p in report.get("wellness_summary", {}).get("primary_priorities", [])[:4]:
                wellness_recommendations.append(
                    WellnessRecommendationVM(
                        title=str(p),
                        detail="Evidence-backed preventative focus derived from breed epidemiology and nutrition literature.",
                    )
                )

        return JourneyPageVM(
            home=home,
            environment_rows=wellness_home.environment_rows,
            trait_labels=traits,
            trait_benefits=trait_benefits,
            trait_weaknesses=trait_weaknesses,
            priorities=priorities,
            nutrition_priorities=nutrition_priorities,
            wellness_recommendations=wellness_recommendations,
            packages=wellness_home.packages,
            package_detail=package_detail,
            nutrition_traces=nutrition.traces,
            product_analysis=product_analysis,
            shop_items=[
                {
                    "name": i.name,
                    "category": i.category,
                    "product_id": i.product_id,
                    "price_display": i.price_display,
                }
                for i in shop_vm.items
            ],
            diary_selected_label=diary_vm.selected_label,
            diary_logs=diary_vm.selected_logs,
        )
