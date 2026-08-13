"""Streamlit navigation — single-page scroll journey."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import streamlit as st

from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository, bootstrap
from app.core.paths import clinical_root_str
from app.ui.renderer.journey import JourneyRenderer
from app.ui.renderer.formatters import vm_to_dict
from app.ui.renderer.template_engine import load_css, render_template

DATA_DIR = clinical_root_str()
DEFAULT_PACKAGE = "Balanced Care"


def default_profile() -> DogProfileInput:
    return DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=3.0,
        weight_kg=28.0,
        current_environment="Shanghai Summer",
        activity_level="High",
        sex="Female",
    )


@st.cache_resource
def get_agent() -> PPIEWellnessAgent:
    return PPIEWellnessAgent(data_dir=DATA_DIR)


@st.cache_resource
def get_repo() -> DataRepository:
    bootstrap(DATA_DIR, strict=True)
    return DataRepository(DATA_DIR)


@st.cache_resource
def get_journey_renderer() -> JourneyRenderer:
    return JourneyRenderer(get_repo())


def run_engine(profile: DogProfileInput) -> dict[str, Any]:
    return asyncio.run(get_agent().generate_reproducible_report(profile))


class NavigationRouter:
    """Renders one continuous premium wellness journey on the Home page."""

    def __init__(self) -> None:
        self.journey_renderer = get_journey_renderer()

    def ensure_state(self) -> None:
        defaults = {
            "selected_package": DEFAULT_PACKAGE,
            "selected_product": None,
            "diary_selected_day": "jul12",
            "demo_profile": default_profile(),
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
        if "demo_report" not in st.session_state:
            st.session_state.demo_report = run_engine(st.session_state.demo_profile)

    def inject_css(self) -> None:
        st.markdown(f"<style>{load_css('app_styles.css')}</style>", unsafe_allow_html=True)

    def render_sidebar(self) -> None:
        with st.sidebar:
            st.markdown("### 🐾 Wagtopia")
            if st.button("♻ Refresh PPIE Output", use_container_width=True):
                st.session_state.demo_report = run_engine(st.session_state.demo_profile)
                st.rerun()
            st.caption("Deterministic veterinary wellness report — scroll to explore every section.")

    def render_journey(self) -> None:
        report = st.session_state.demo_report
        profile = st.session_state.demo_profile

        wellness = self.journey_renderer.wellness_renderer.build_home(report)
        pkg_titles = [p.title for p in wellness.packages]
        if st.session_state.selected_package not in pkg_titles:
            st.session_state.selected_package = DEFAULT_PACKAGE

        with st.container():
            col1, col2, col3 = st.columns([2, 2, 2])
            with col1:
                st.session_state.selected_package = st.selectbox(
                    "Care package focus",
                    pkg_titles,
                    index=pkg_titles.index(st.session_state.selected_package),
                    label_visibility="collapsed",
                )
            with col2:
                detail = self.journey_renderer.wellness_renderer.build_package_detail(
                    report, profile, st.session_state.selected_package
                )
                product_names = [p.name for p in detail.products] or ["—"]
                if st.session_state.selected_product not in product_names:
                    st.session_state.selected_product = product_names[0]
                st.session_state.selected_product = st.selectbox(
                    "Product focus",
                    product_names,
                    index=product_names.index(st.session_state.selected_product),
                    label_visibility="collapsed",
                )
            with col3:
                diary_vm = self.journey_renderer.diary_renderer.build(st.session_state.diary_selected_day)
                day_labels = [d.label for d in diary_vm.days]
                day_keys = [d.key for d in diary_vm.days]
                picked = st.selectbox(
                    "Diary date",
                    day_labels,
                    index=day_keys.index(st.session_state.diary_selected_day),
                    label_visibility="collapsed",
                )
                st.session_state.diary_selected_day = day_keys[day_labels.index(picked)]

        vm = self.journey_renderer.build(
            report=report,
            profile=profile,
            package_title=st.session_state.selected_package,
            product_name=st.session_state.selected_product,
            diary_day=st.session_state.diary_selected_day,
        )
        st.markdown(render_template("home/journey.html", **vm_to_dict(vm)), unsafe_allow_html=True)

    def run(self) -> None:
        self.ensure_state()
        self.inject_css()
        self.render_sidebar()
        self.render_journey()


def configure_streamlit() -> None:
    st.set_page_config(
        page_title="Wagtopia — Premium Wellness Report",
        page_icon="🐾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
