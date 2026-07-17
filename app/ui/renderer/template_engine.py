"""Jinja2 template loader — single entry point for HTML rendering."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@lru_cache(maxsize=1)
def _environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(template_name: str, **context: Any) -> str:
    """Render a template relative to app/ui/templates/."""
    return _environment().get_template(template_name).render(**context)


def load_css(relative_path: str) -> str:
    """Load a CSS file from templates/base/ or templates/."""
    candidates = [
        TEMPLATES_DIR / relative_path,
        TEMPLATES_DIR / "base" / relative_path,
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"CSS not found: {relative_path}")
