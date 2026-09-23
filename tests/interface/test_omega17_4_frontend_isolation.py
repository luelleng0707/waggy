"""Ω17.4-FE: product UI lives in waggy-frontend and talks to Waggy over HTTP."""

from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from app.api.main import app
from scripts.run_wagtopia_local import resolve_workbench_static_path
from tests.interface.frontend_paths import (
    CLIENT_JS,
    CONFIG_JS,
    DEMO_JS,
    FRONTEND_ROOT,
    WORKBENCH_HTML,
    WORKBENCH_JS,
    frontend_js_text,
)


def test_fastapi_serves_isolated_frontend(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("API_KEYS", raising=False)
    client = TestClient(app)
    home = client.get("/")
    assert home.status_code == 200
    assert "workbench.js" in home.text
    assert "Personalized Wellness Analysis" in home.text
    src = client.get("/src/workbench.js")
    assert src.status_code == 200
    assert "runWorkbenchAnalysis" in src.text
    css = client.get("/src/styles/workbench.css")
    assert css.status_code == 200
    alias = client.get("/workbench.js")
    assert alias.status_code == 200
    client_js = client.get("/src/api/client.js")
    assert client_js.status_code == 200
    assert "runWorkbenchAnalysis" in client_js.text
    config = client.get("/src/api/config.js")
    assert config.status_code == 200
    assert "getApiBaseUrl" in config.text


def test_frontend_has_no_backend_or_secret_coupling():
    blob = frontend_js_text() + "\n" + WORKBENCH_HTML.read_text(encoding="utf-8")
    for token in (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "AIza",
        "scientific_care",
        "app/agent/package_search",
        "app/agent/package_optimizer",
        "DataRepository",
        "from app.",
        "warehouse/biology",
        "../../../app/",
    ):
        assert token not in blob
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    for spec in re.findall(r'from ["\']([^"\']+)["\']', js):
        assert spec.startswith("./"), spec
        assert not spec.startswith("../"), spec
    assert "getApiBaseUrl" in CONFIG_JS.read_text(encoding="utf-8")
    assert "SYNTHETIC / DEMO ONLY" in DEMO_JS.read_text(encoding="utf-8")
    assert "runWorkbenchAnalysis" in CLIENT_JS.read_text(encoding="utf-8")
    assert "fetch(" not in js
    assert list(FRONTEND_ROOT.rglob("*.csv")) == []
    assert list(FRONTEND_ROOT.rglob("*.py")) == []


def test_legacy_workbench_is_not_a_second_copy():
    root = FRONTEND_ROOT.parent
    assert not (root / "legacy" / "workbench.html").exists()
    assert not (root / "legacy" / "workbench.js").exists()
    assert not (root / "legacy" / "workbench.css").exists()
    assert (FRONTEND_ROOT / "index.html").is_file()
    assert resolve_workbench_static_path("/").name == "index.html"
    assert "waggy-frontend" in resolve_workbench_static_path("/").parts
    assert resolve_workbench_static_path("/src/api/client.js").name == "client.js"
    assert resolve_workbench_static_path("/debug/calculation").name == "calculation.html"


def test_workbench_still_renders_api_results_not_local_science():
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    client = CLIENT_JS.read_text(encoding="utf-8")
    assert "function renderHealthAnalysis" in js
    assert 'id="nutrition-modal"' in html
    assert "Why this bundle" in js
    assert "warehouse_version" in js
    assert "recomputeWithPreferences" in js
    assert "summary_facts" in js
    assert "runWorkbenchAnalysis" in client
    assert "getRecalculationExplanation" in client
    assert "2 **" not in js
    assert "prevalence * 100" not in js


def test_copied_frontend_workspace_builds_independently(tmp_path: Path):
    dest = tmp_path / "waggy-frontend-migration-test"
    shutil.copytree(
        FRONTEND_ROOT,
        dest,
        ignore=shutil.ignore_patterns("node_modules", "dist"),
    )
    assert not (dest / "app").exists()
    assert not (dest / "warehouse").exists()
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required for the physical migration test")
    check = subprocess.run(
        [node, "scripts/serve.mjs", "--check"],
        cwd=dest,
        capture_output=True,
        text=True,
        check=False,
    )
    assert check.returncode == 0, check.stdout + check.stderr
    tests = subprocess.run(
        [node, "--test", "tests/isolation.test.mjs", "tests/api-client.test.mjs"],
        cwd=dest,
        capture_output=True,
        text=True,
        check=False,
    )
    assert tests.returncode == 0, tests.stdout + tests.stderr
    build = subprocess.run(
        [node, "scripts/build.mjs"],
        cwd=dest,
        capture_output=True,
        text=True,
        check=False,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    assert (dest / "dist" / "index.html").is_file()
    assert (dest / "dist" / "src" / "api" / "client.js").is_file()
    assert "warehouse" not in (dest / "package.json").read_text(encoding="utf-8")
    env_example = (dest / ".env.example").read_text(encoding="utf-8")
    assert "WAGGY_API_BASE_URL" in env_example
    assert "GEMINI" not in env_example
    assert list(dest.rglob("*.csv")) == []
    assert list(dest.rglob("*.py")) == []
    for path in dest.rglob("*"):
        if not path.is_file():
            continue
        if "tests" in path.parts or "node_modules" in path.parts or "dist" in path.parts:
            continue
        if path.suffix.lower() not in {".js", ".mjs", ".html", ".css", ".json", ".md", ".example"} and path.name != ".env.example":
            continue
        text = path.read_text(encoding="utf-8")
        assert "GEMINI_API_KEY" not in text, path
        assert "BEGIN PRIVATE KEY" not in text, path
        assert "OPENAI_API_KEY" not in text, path

    port = _free_port()
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["WAGGY_API_BASE_URL"] = "http://waggy-api.example.test"
    proc = subprocess.Popen(
        [node, "scripts/serve.mjs"],
        cwd=dest,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    html = None
    runtime = None
    last_err: Exception | None = None
    try:
        for _ in range(50):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/src/api/runtime-config.js",
                    timeout=1,
                ) as resp:
                    runtime = resp.read().decode("utf-8", errors="replace")
                break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_err = exc
                time.sleep(0.1)
        if html is None:
            pytest.fail(f"copied frontend did not start: {last_err}")
        assert "Personalized Wellness Analysis" in html
        assert "workbench.js" in html
        assert "http://waggy-api.example.test" in (runtime or "")
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/src/api/client.js", timeout=1) as resp:
            assert "runWorkbenchAnalysis" in resp.read().decode("utf-8", errors="replace")
    finally:
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.terminate()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])
