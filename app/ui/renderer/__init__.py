"""Presentation layer — converts PPIE engine output into template-ready view models."""

from app.ui.renderer.formatters import fmt_mass, fmt_percentage, fmt_rmb
from app.ui.renderer.journey import JourneyRenderer
from app.ui.renderer.navigation import NavigationRouter, configure_streamlit
from app.ui.renderer.view_models import vm_to_dict
from app.ui.renderer.template_engine import load_css, render_template
from app.ui.renderer.wellness import WellnessRenderer
from app.ui.renderer.home import HomeRenderer
from app.ui.renderer.diary import DiaryRenderer

__all__ = [
    "fmt_rmb",
    "fmt_percentage",
    "fmt_mass",
    "render_template",
    "load_css",
    "NavigationRouter",
    "configure_streamlit",
    "JourneyRenderer",
    "WellnessRenderer",
    "HomeRenderer",
    "DiaryRenderer",
    "vm_to_dict",
]
