"""Paths to the portable product frontend (waggy-frontend/)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ROOT = ROOT / "waggy-frontend"
WORKBENCH_HTML = FRONTEND_ROOT / "index.html"
WORKBENCH_JS = FRONTEND_ROOT / "src" / "workbench.js"
WORKBENCH_CSS = FRONTEND_ROOT / "src" / "styles" / "workbench.css"
THEME_CSS = FRONTEND_ROOT / "src" / "styles" / "theme.css"
CLIENT_JS = FRONTEND_ROOT / "src" / "api" / "client.js"
CONFIG_JS = FRONTEND_ROOT / "src" / "api" / "config.js"
DEMO_JS = FRONTEND_ROOT / "src" / "demo" / "dogs.js"


def frontend_js_text() -> str:
    parts: list[str] = []
    src = FRONTEND_ROOT / "src"
    for path in sorted(src.rglob("*.js")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)
