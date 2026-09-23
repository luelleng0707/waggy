from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_no_frontend_default_demo_key_fallbacks():
    frontend_files = [
        "legacy/archive/frontend/app.js",
        "legacy/archive/frontend/business.js",
        "legacy/archive/frontend/catalog-service.js",
        "legacy/ppie-validation-console.js",
        "waggy-frontend/src/workbench.js",
    ]
    for rel in frontend_files:
        text = _read(rel)
        assert "wagtopia-demo-key" not in text
        assert "window.WAGTOPIA_API_KEY || 'wagtopia-demo-key'" not in text


def test_no_backend_default_api_key_seed():
    text = _read("app/api/main.py")
    assert 'os.getenv("API_KEYS", "wagtopia-demo-key,ppie-dev-key")' not in text
    assert 'os.getenv("API_KEYS", "")' in text


def test_local_launchers_do_not_default_to_embedded_api_key():
    for rel in ("scripts/run_wagtopia_local.py", "scripts/run_wagtopia_remote.py"):
        text = _read(rel)
        assert 'parser.add_argument("--api-key", default="wagtopia-demo-key")' not in text
