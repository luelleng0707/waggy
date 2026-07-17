"""Smoke tests for UI template rendering layer."""

from dataclasses import asdict

import pytest

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.ui.renderer.diary import DiaryRenderer
from app.ui.renderer.home import HomeRenderer
from app.ui.renderer.journey import JourneyRenderer
from app.ui.renderer.view_models import vm_to_dict
from app.ui.renderer.navigation import NavigationRouter
from app.ui.renderer.shop import ShopRenderer
from app.ui.renderer.template_engine import load_css, render_template
from app.ui.renderer.wellness import WellnessRenderer


@pytest.fixture
def dolly_profile() -> DogProfileInput:
    return DogProfileInput(
        name="dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=4.3,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )


@pytest.fixture
def engine_report(dolly_profile: DogProfileInput):
    import asyncio

    return asyncio.run(PPIEWellnessAgent(data_dir="data").generate_reproducible_report(dolly_profile))


def test_css_assets_load():
    assert "device-frame" in load_css("app_styles.css")
    assert "phone-app" in load_css("app_styles.css")


def test_home_intro_content(engine_report, dolly_profile):
    home = HomeRenderer().build(engine_report)
    assert "Dolly" in home.greeting
    assert "Personality" in home.detail_blocks[0].title

    journey = JourneyRenderer(DataRepository("data"))
    vm = journey.build(engine_report, dolly_profile, "Balanced Care", None, "jul12")
    html = render_template("home/journey.html", **vm_to_dict(vm))
    assert "Hello" in html
    assert "Wellness Analysis" in html


def test_journey_template_renders(engine_report, dolly_profile):
    journey = JourneyRenderer(DataRepository("data"))
    vm = journey.build(engine_report, dolly_profile, "Balanced Care", None, "jul12")
    html = render_template("home/journey.html", **vm_to_dict(vm))
    assert "Wagtopia" in html
    assert "Premium Care" in html
    assert "Personality" in html
    assert "Trait Benefits" in html
    assert "Trait Weaknesses" in html
    assert "Nutrition Priorities" in html
    assert "breed epidemiology" in html
    assert "Recommended Care Packages" in html
    assert "Grooming Diary" in html
    assert "Frozen yogurt bites" in html


def test_wellness_component_templates_render(engine_report, dolly_profile):
    repo = DataRepository("data")
    wellness = WellnessRenderer(repo)
    detail_vm = wellness.build_package_detail(engine_report, dolly_profile, "Balanced Care")
    html = render_template("wellness/package_detail.html", **vm_to_dict(detail_vm))
    assert "Balanced Care" in html

    nutrition_vm = wellness.build_full_nutrition_report(engine_report, dolly_profile, "Balanced Care")
    html = render_template("wellness/nutrition_report.html", traces=nutrition_vm.traces)
    assert "Full Nutrition Report" in html


def test_shop_and_diary_templates_render(engine_report):
    repo = DataRepository("data")
    shop_vm = ShopRenderer().build(engine_report, repo.product_catalog(), repo.product_pricing())
    html = render_template("shop/page.html", **asdict(shop_vm))
    assert "Wagtopia Shop" in html

    diary_vm = DiaryRenderer().build("jul12")
    html = render_template("diary/page.html", **asdict(diary_vm))
    assert "Grooming Diary" in html


def test_navigation_router_instantiates():
    assert NavigationRouter() is not None
