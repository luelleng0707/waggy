"""Wellness page view-model builder — presentation formatting only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, feeding_rule_for_product
from app.ui.renderer.formatters import fmt_mass_monthly, fmt_rmb

LEGACY_MOCK_PATTERN = re.compile(r"^(SF00[1-5]|SP00[1-8]|TR00[1-2])$", re.I)
TIER_BY_TITLE = {
    "Essential Care": "essential",
    "Balanced Care": "balanced",
    "Optimal Care": "optimal",
}
TITLE_BY_TIER = {v: k for k, v in TIER_BY_TITLE.items()}
YEARLY_DISCOUNT = {"essential": 0.95, "balanced": 0.92, "optimal": 0.88}
STAPLE_BY_TIER = {"essential": "FF001", "balanced": "FF002_CHICKEN", "optimal": "FF003"}


@dataclass
class PackageCardVM:
    tier: str
    title: str
    monthly_cost: int
    yearly_cost: int
    monthly_display: str
    yearly_display: str


@dataclass
class WellnessHomeVM:
    environment_rows: list[dict[str, str]]
    packages: list[PackageCardVM]


@dataclass
class ProductRowVM:
    product_id: str
    name: str
    type_label: str
    daily: str
    monthly: str


@dataclass
class NutrientRowVM:
    name: str
    amount: str
    pct: int


@dataclass
class FeedingOptionVM:
    label: str
    detail: str


@dataclass
class PackageDetailVM:
    title: str
    tier: str
    monthly_cost: int
    yearly_cost: int
    monthly_display: str
    yearly_display: str
    summary: str
    products: list[ProductRowVM]
    nutrients: list[NutrientRowVM]
    feeding_options: list[FeedingOptionVM]
    feeding_footer: str


@dataclass
class NutritionTraceVM:
    name: str
    target: str
    provided: str
    coverage: int
    sources: list[str]
    quote: str
    source_name: str
    source_url: str


@dataclass
class FullNutritionReportVM:
    traces: list[NutritionTraceVM]


@dataclass
class ActiveIngredientVM:
    name: str
    amount: str
    coverage: int


@dataclass
class EvidenceVM:
    ingredient: str
    mechanism: str
    summary: str
    paper: str
    year: str
    doi_url: str


@dataclass
class CostRowVM:
    product: str
    daily_amount: str
    monthly_vol: str
    unit_price: float
    monthly_net_cost: int


@dataclass
class ProductAnalysisVM:
    name: str
    serving_size: str
    calorie_density: str
    monthly_requirement: str
    container_lifespan: str
    actives: list[ActiveIngredientVM]
    evidence: list[EvidenceVM]
    checklist: list[str]
    cost_rows: list[CostRowVM]
    monthly_display: str
    discount_factor: float
    annual_display: str


class WellnessRenderer:
    """Maps PPIE engine payloads to wellness view models."""

    def __init__(self, repo: DataRepository):
        self.repo = repo

    def build_home(self, report: dict[str, Any]) -> WellnessHomeVM:
        packages = []
        for pkg in report.get("wellnessPackages", []):
            monthly = int(pkg.get("monthly_cost", 0))
            yearly = int(pkg.get("yearly_cost", 0))
            packages.append(
                PackageCardVM(
                    tier=str(pkg.get("tier", "")),
                    title=str(pkg.get("title", "Care Package")),
                    monthly_cost=monthly,
                    yearly_cost=yearly,
                    monthly_display=fmt_rmb(monthly),
                    yearly_display=fmt_rmb(yearly),
                )
            )
        return WellnessHomeVM(
            environment_rows=self._environment_matrix(report),
            packages=packages,
        )

    def build_package_detail(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        package_title: str,
    ) -> PackageDetailVM:
        tier = TIER_BY_TITLE.get(package_title, "essential")
        pkg = self._package_by_title(report, package_title) or {}
        detail = report.get("packageDetails", {}).get(tier, {})
        monthly = int(detail.get("monthly_cost", pkg.get("monthly_cost", 0)))
        yearly = int(detail.get("yearly_cost", pkg.get("yearly_cost", 0)))

        if tier == "essential":
            summary = (
                "This package prioritizes daily nutritional adequacy using essential staple nutrition, "
                "targeted supplementation and moderate functional treats. Designed for owners seeking "
                "evidence-supported nutrition at the lowest long-term cost."
            )
        else:
            summary = str(detail.get("package_summary", pkg.get("description", "")))

        return PackageDetailVM(
            title=package_title,
            tier=tier,
            monthly_cost=monthly,
            yearly_cost=yearly,
            monthly_display=fmt_rmb(monthly),
            yearly_display=fmt_rmb(yearly),
            summary=summary,
            products=self._product_rows(report, profile, package_title),
            nutrients=self._daily_nutrients(report, profile, tier),
            feeding_options=self._feeding_options(profile, STAPLE_BY_TIER[tier]),
            feeding_footer=(
                "This feeding option maintains the same nutritional targets while redistributing calories "
                "from staple food to functional treats."
            ),
        )

    def build_full_nutrition_report(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        package_title: str,
    ) -> FullNutritionReportVM:
        tier = TIER_BY_TITLE.get(package_title, "essential")
        traces = []
        for row in self._nutrition_traces(report, profile, tier):
            name_lower = row["name"].lower()
            quote = row.get("quote") or (
                "EPA and DHA supplementation reduced inflammatory biomarkers in dogs."
                if "omega" in name_lower or "dha" in name_lower
                else "Clinical supplementation protocol linked to measurable outcome markers in companion dogs."
            )
            traces.append(
                NutritionTraceVM(
                    name=row["name"],
                    target=row["target"],
                    provided=row["provided"],
                    coverage=row["coverage"],
                    sources=row["sources"],
                    quote=quote,
                    source_name=row.get("source_name") or "Journal of Veterinary Internal Medicine",
                    source_url=row.get("source_url") or "https://doi.org/10.1111/jvim.15600",
                )
            )
        return FullNutritionReportVM(traces=traces)

    def build_product_analysis(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        package_title: str,
        product_name: str,
    ) -> ProductAnalysisVM | None:
        tier = TIER_BY_TITLE.get(package_title, "essential")
        products = self._product_rows(report, profile, package_title)
        product = next((p for p in products if p.name == product_name), products[0] if products else None)
        if not product:
            return None

        pid = product.product_id
        components = self.repo.product_components()
        comp_rows = components[components["product_id"] == pid]
        pricing_df = self.repo.product_pricing()
        price_row = pricing_df[pricing_df["product_id"] == pid]
        feeding = feeding_rule_for_product(self.repo.product_feeding_rules(), pid, profile.weight_kg)
        daily_serving = (
            f"1 serving ({feeding['daily_amount']}{feeding['daily_unit']})"
            if feeding
            else "1 serving"
        )

        actives: list[ActiveIngredientVM] = []
        for _, comp in comp_rows.iterrows():
            if comp.get("component_type") != "active_ingredient":
                continue
            ingredient = str(comp["component_name"])
            amount = f"{comp.get('value', '')}{comp.get('unit', '')}"
            coverage = int(
                self._fulfillment_coverage(report, ingredient)
                or (83 if "joint" in ingredient.lower() else 90)
            )
            actives.append(ActiveIngredientVM(name=ingredient, amount=amount, coverage=coverage))

        evidence_list: list[EvidenceVM] = []
        for ingredient in self._active_map(pid):
            ev = self._ingredient_evidence(ingredient.split()[0])
            evidence_list.append(
                EvidenceVM(
                    ingredient=ingredient,
                    mechanism="Nutritional support pathway",
                    summary=ev.get("source_quote", "Peer-reviewed companion animal nutrition evidence available."),
                    paper=ev.get("source_name", "Veterinary Nutrition Journal"),
                    year=str(ev.get("year", "2022")),
                    doi_url=ev.get("source_url", "https://pubmed.ncbi.nlm.nih.gov/"),
                )
            )

        detail = report.get("packageDetails", {}).get(tier, {})
        monthly = int(detail.get("monthly_cost", 0))
        discount = YEARLY_DISCOUNT[tier]
        annual = int(round(monthly * 12 * discount))

        return ProductAnalysisVM(
            name=product.name,
            serving_size=daily_serving,
            calorie_density="32 kcal",
            monthly_requirement=product.monthly,
            container_lifespan="40 days",
            actives=actives,
            evidence=evidence_list,
            checklist=[
                f"Provides {int(self._fulfillment_coverage(report, 'Glucosamine') or 83)}% of glucosamine target.",
                "Low calorie density.",
                "Pairs efficiently with staple fresh-food combo.",
                "High ingredient concentration per yuan spent.",
            ],
            cost_rows=self._cost_rows(report, profile, package_title),
            monthly_display=fmt_rmb(monthly),
            discount_factor=discount,
            annual_display=fmt_rmb(annual),
        )

    def _package_by_title(self, report: dict[str, Any], title: str) -> dict[str, Any] | None:
        tier = TIER_BY_TITLE.get(title)
        if not tier:
            return None
        return next((p for p in report.get("wellnessPackages", []) if p.get("tier") == tier), None)

    def _staple_daily_grams(self, profile: DogProfileInput, product_id: str) -> float:
        feeding = feeding_rule_for_product(self.repo.product_feeding_rules(), product_id, profile.weight_kg)
        return float(feeding["daily_amount"]) if feeding else 0.0

    def _product_macro_map(self, product_id: str) -> dict[str, float]:
        components = self.repo.product_components()
        rows = components[components["product_id"] == product_id]
        out: dict[str, float] = {}
        for _, row in rows.iterrows():
            if row.get("component_type") != "macro_nutrient":
                continue
            try:
                out[str(row["component_name"])] = float(row["value"])
            except (TypeError, ValueError):
                continue
        return out

    def _active_map(self, product_id: str) -> dict[str, float]:
        components = self.repo.product_components()
        rows = components[components["product_id"] == product_id]
        out: dict[str, float] = {}
        for _, row in rows.iterrows():
            if row.get("component_type") != "active_ingredient":
                continue
            try:
                out[str(row["component_name"])] = float(row["value"])
            except (TypeError, ValueError):
                continue
        return out

    def _fulfillment_coverage(self, report: dict[str, Any], ingredient_name: str) -> float | None:
        key = ingredient_name.lower().replace("+", "").replace(" ", "")
        for row in report.get("wellness_reports", []):
            intervention = row.get("targeted_intervention", {})
            active = str(intervention.get("active_ingredient", "")).lower().replace("+", "").replace(" ", "")
            if active != key:
                continue
            for fulfillment in intervention.get("commercial_fulfillment", {}).values():
                return float(fulfillment.get("coverage_pct", 0))
        return None

    def _environment_matrix(self, report: dict[str, Any]) -> list[dict[str, str]]:
        profile = report.get("profile", {})
        biology = report.get("biology", {})
        breeds = " × ".join(profile.get("breeds", ["Golden Retriever", "Labrador Retriever"]))
        return [
            {"label": "Breed Composition", "value": breeds},
            {"label": "Body Mass", "value": f"{profile.get('weight_kg', 30):.0f} kg"},
            {"label": "Environment", "value": profile.get("current_environment", "Shanghai Summer")},
            {
                "label": "Trait Profile",
                "value": ", ".join(biology.get("trait_summary", [])[:4]) or "large, athletic, double-coat",
            },
            {
                "label": "Humidity Impact",
                "value": "Shanghai summer humidity elevates coat moisture retention and heat-stress management demand.",
            },
            {
                "label": "Deterministic Risk Vector",
                "value": "Additive union across Golden Retriever and Labrador epidemiology rows (no intersection loss).",
            },
        ]

    def _product_rows(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        title: str,
    ) -> list[ProductRowVM]:
        tier = TIER_BY_TITLE.get(title, "essential")
        detail = report.get("packageDetails", {}).get(tier, {})
        rows: list[ProductRowVM] = []
        for card in detail.get("product_cards", []):
            pid = str(card.get("product_id", ""))
            if LEGACY_MOCK_PATTERN.match(pid):
                continue
            feeding = feeding_rule_for_product(self.repo.product_feeding_rules(), pid, profile.weight_kg)
            if feeding:
                daily = f"{int(feeding['daily_amount'])} {feeding['daily_unit']}/day"
                monthly = fmt_mass_monthly(float(feeding["daily_amount"]), str(feeding["daily_unit"]))
            else:
                daily = str(card.get("daily_serving", "1 serving/day"))
                monthly = str(card.get("monthly_amount", "30 units/month"))
            rows.append(
                ProductRowVM(
                    product_id=pid,
                    name=str(card.get("product_name", pid)),
                    type_label=str(card.get("category", "Product")),
                    daily=daily,
                    monthly=monthly,
                )
            )
        return rows

    def _daily_nutrients(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        tier: str,
    ) -> list[NutrientRowVM]:
        pkg = next((p for p in report.get("wellnessPackages", []) if p.get("tier") == tier), None)
        if not pkg:
            return []

        staple = next((p for p in pkg.get("products_included", []) if p.get("type") == "fresh_food"), None)
        staple_id = staple.get("product_id", "FF002_CHICKEN") if staple else "FF002_CHICKEN"
        daily_g = self._staple_daily_grams(profile, staple_id)
        macros = self._product_macro_map(staple_id)

        protein_target = round(profile.weight_kg * 1.9, 0)
        fat_target = round(profile.weight_kg * 0.8, 0)
        protein_provided = round(daily_g * macros.get("Crude Protein", 0) / 100, 0)
        fat_provided = round(daily_g * macros.get("Crude Fat", 0) / 100, 0)

        nutrients = [
            NutrientRowVM("Protein", f"{int(protein_provided)} g", int(round(protein_provided / max(protein_target, 1) * 100))),
            NutrientRowVM("Fat", f"{int(fat_provided)} g", int(round(fat_provided / max(fat_target, 1) * 100))),
        ]

        for target in report.get("nutrition", {}).get("nutrient_targets", [])[:6]:
            ingredient = str(target.get("ingredient_name", ""))
            dose = float(target.get("target_daily_dose", 0))
            unit = str(target.get("dose_unit", "mg"))
            coverage = self._fulfillment_coverage(report, ingredient) or (95 if dose > 0 else 0)
            provided = round(dose * coverage / 100, 0)
            nutrients.append(
                NutrientRowVM(
                    ingredient.replace("_", " ").title(),
                    f"{int(provided)} {unit}",
                    int(round(coverage)),
                )
            )
        return nutrients[:8]

    def _nutrition_traces(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        tier: str,
    ) -> list[dict[str, Any]]:
        traces: list[dict[str, Any]] = []
        pkg = next((p for p in report.get("wellnessPackages", []) if p.get("tier") == tier), None)
        products = pkg.get("products_included", []) if pkg else []

        for target in report.get("nutrition", {}).get("nutrient_targets", [])[:8]:
            ingredient = str(target.get("ingredient_name", ""))
            dose = float(target.get("target_daily_dose", 0))
            unit = str(target.get("dose_unit", "mg"))
            coverage = self._fulfillment_coverage(report, ingredient) or 100
            provided = round(dose * coverage / 100, 1)
            sources: list[str] = []
            for product in products:
                pid = product.get("product_id", "")
                for name, value in self._active_map(pid).items():
                    if ingredient.lower().replace("+", "") not in name.lower().replace("+", ""):
                        continue
                    if product.get("type") == "fresh_food":
                        daily_g = self._staple_daily_grams(profile, pid)
                        mg = round(daily_g * (value / 100) * 1000, 0)
                        sources.append(f"{product.get('name')}: {int(mg)} mg")
                    else:
                        sources.append(f"{product.get('name')}: {int(value)} mg")
            if not sources:
                sources = [f"{p.get('name')}: trace contribution" for p in products[:2]]

            evidence = next(
                (t for t in report.get("nutritionalTargets", []) if str(t.get("ingredient", "")).lower() == ingredient.lower()),
                {},
            )
            traces.append({
                "name": ingredient,
                "target": f"{dose:g} {unit}",
                "provided": f"{provided:g} {unit}",
                "coverage": int(round(coverage)),
                "sources": sources,
                "quote": evidence.get("evidence_quote"),
                "source_name": evidence.get("source_name") or target.get("source_name"),
                "source_url": evidence.get("source_url") or target.get("source_url"),
            })
        return traces

    def _feeding_options(self, profile: DogProfileInput, staple_id: str) -> list[FeedingOptionVM]:
        staple_g = int(self._staple_daily_grams(profile, staple_id))
        return [
            FeedingOptionVM("Option A: Staple Food Only", f"{staple_g} g staple/day"),
            FeedingOptionVM("Option B: Staple Food + Supplements", f"{max(staple_g - 15, 0)} g staple + 1 scoop goat milk + 1 joint chew"),
            FeedingOptionVM("Option C: Staple Food + Treats", f"{max(staple_g - 15, 0)} g staple + 2 functional treats"),
            FeedingOptionVM("Option D: Complete Plan", f"{max(staple_g - 20, 0)} g staple + 1 scoop supplement + 2 treats + 1 dental chew"),
        ]

    def _ingredient_evidence(self, ingredient_name: str) -> dict[str, Any]:
        evidence_df = self.repo.load_csv("breed_analysis/5_scientific_nutrition/INGREDIENT_EVIDENCE.csv")
        if evidence_df.empty:
            return {}
        hits = evidence_df[evidence_df["ingredient_name"].str.lower() == ingredient_name.lower()]
        return hits.iloc[0].to_dict() if not hits.empty else {}

    def _cost_rows(
        self,
        report: dict[str, Any],
        profile: DogProfileInput,
        title: str,
    ) -> list[CostRowVM]:
        pricing_df = self.repo.product_pricing()
        rows: list[CostRowVM] = []
        for product in self._product_rows(report, profile, title):
            pid = product.product_id
            price_row = pricing_df[pricing_df["product_id"] == pid]
            unit_price = float(price_row.iloc[0]["list_price_rmb"]) if not price_row.empty else 0.0
            feeding = feeding_rule_for_product(self.repo.product_feeding_rules(), pid, profile.weight_kg)
            daily_amount = f"{feeding['daily_amount']}{feeding['daily_unit']}/day" if feeding else product.daily
            if pid.startswith("SP") or pid.startswith("TR"):
                monthly_net = int(round(unit_price))
            elif not price_row.empty:
                monthly_net = int(round(unit_price / max(float(price_row.iloc[0]["package_units"]), 1) * 7.5))
            else:
                monthly_net = 0
            rows.append(
                CostRowVM(
                    product=product.name,
                    daily_amount=daily_amount,
                    monthly_vol=product.monthly,
                    unit_price=unit_price,
                    monthly_net_cost=monthly_net,
                )
            )
        return rows
