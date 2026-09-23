"""Package-generation provenance: causality, not snapshot of current SKUs."""

from __future__ import annotations

from tests.interface.frontend_paths import WORKBENCH_CSS, WORKBENCH_HTML, WORKBENCH_JS
import ast
from pathlib import Path
import re

from fastapi.testclient import TestClient
import pytest

from app.agent.package_optimizer import build_optimized_packages, load_candidate_products
from app.agent.state import DogProfileInput
from app.agent.utils import DataRepository
from app.api.main import app
from app.core.paths import clinical_root_str
from app.data.demo_catalog import demo_product_ids


ROOT = Path(__file__).resolve().parents[2]
OPTIMIZER_PATH = ROOT / "app" / "agent" / "package_optimizer.py"
ASSEMBLER_PATH = ROOT / "app" / "agent" / "response_assembler.py"

_AI_DEPENDENCY_TOKENS = (
    "openai",
    "anthropic",
    "google.generativeai",
    "ollama",
    "langchain",
    "litellm",
    "transformers",
    "chat.completions",
    "responses.create",
)

_FRONTEND_ASSETS = (
    ROOT / "legacy" / "archive" / "frontend" / "index.html",
    ROOT / "legacy" / "archive" / "frontend" / "app.js",
    ROOT / "legacy" / "archive" / "frontend" / "business.html",
    ROOT / "legacy" / "archive" / "frontend" / "business.js",
    ROOT / "legacy" / "archive" / "frontend" / "business.css",
    ROOT / "legacy" / "debug" / "calculation.html",
    ROOT / "legacy" / "ppie-validation-console.js",
    ROOT / "legacy" / "archive" / "frontend" / "ppie-shell.js",
    ROOT / "legacy" / "archive" / "frontend" / "ppie-ui.js",
    ROOT / "legacy" / "archive" / "frontend" / "catalog-service.js",
    WORKBENCH_HTML,
    WORKBENCH_JS,
    WORKBENCH_CSS,
)


def _dolly_json() -> dict:
    return {
        "name": "Dolly",
        "pet_name": "Dolly",
        "breeds": ["Golden Retriever", "Labrador Retriever"],
        "birthday": "2021-03-15",
        "weight": 30.1,
        "sex": "Female",
        "activity_level": "High",
        "current_environment": "Shanghai Summer",
        "observed_conditions": [],
    }


def _dolly_profile() -> DogProfileInput:
    return DogProfileInput(
        name="Dolly",
        primary_breed="Golden Retriever",
        secondary_breed="Labrador Retriever",
        breed_split_pct=50.0,
        age_years=5.0,
        weight_kg=30.0,
        current_environment="Shanghai Summer",
        activity_level="High",
    )


def _enable_demo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAGTOPIA_DEMO_MODE", "true")
    monkeypatch.setenv("PPIE_DEBUG", "true")
    monkeypatch.delenv("WAGTOPIA_BUSINESS_ACCESS_KEY", raising=False)
    monkeypatch.delenv("WAGTOPIA_DEVELOPER_ACCESS_KEY", raising=False)
    monkeypatch.delenv("API_KEYS", raising=False)
    for key in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "AZURE_OPENAI_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)


class _CatalogViewRepo:
    """Same optimizer, substituted commercial tables only."""

    def __init__(
        self,
        inner: DataRepository,
        *,
        products=None,
        pricing=None,
        components=None,
        feeding=None,
        functions=None,
    ):
        self._inner = inner
        self._products = products
        self._pricing = pricing
        self._components = components
        self._feeding = feeding
        self._functions = functions

    def active_products(self):
        df = self._inner.active_products() if self._products is None else self._products
        if df is None or df.empty:
            return df
        if "status" not in df.columns:
            return df.copy()
        status = df["status"].astype(str).str.lower()
        return df[status.isin(["active", ""])].copy()

    def product_pricing(self):
        return self._inner.product_pricing() if self._pricing is None else self._pricing

    def product_components(self):
        return self._inner.product_components() if self._components is None else self._components

    def product_feeding_rules(self):
        return self._inner.product_feeding_rules() if self._feeding is None else self._feeding

    def product_functions(self):
        return self._inner.product_functions() if self._functions is None else self._functions

    def __getattr__(self, name):
        return getattr(self._inner, name)


def _package_ids(packages: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for pkg in packages:
        tier = str(pkg.get("tier"))
        rows = pkg.get("products_included") or []
        out[tier] = [str(item.get("product_id")) for item in rows if item.get("product_id")]
    return out


def _package_economics(packages: list[dict]) -> dict[str, tuple]:
    out: dict[str, tuple] = {}
    for pkg in packages:
        out[str(pkg.get("tier"))] = (
            pkg.get("monthly_cost"),
            pkg.get("yearly_cost"),
            pkg.get("yearly_discount_factor"),
        )
    return out


def _all_ids(packages: list[dict]) -> set[str]:
    ids: set[str] = set()
    for row in _package_ids(packages).values():
        ids.update(row)
    return ids


def _run_optimizer(repo) -> list[dict]:
    return build_optimized_packages(
        repo=repo,
        profile=_dolly_profile(),
        health_insights=[],
        ingredients=[],
        product_recs=[{"product_id": "SHOULD_BE_IGNORED"}],
    )


@pytest.fixture
def demo_repo(monkeypatch: pytest.MonkeyPatch) -> DataRepository:
    _enable_demo(monkeypatch)
    return DataRepository(clinical_root_str())


@pytest.fixture
def demo_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    _enable_demo(monkeypatch)
    return TestClient(app)


def test_optimizer_source_has_no_hardcoded_current_package_output():
    source = OPTIMIZER_PATH.read_text(encoding="utf-8")
    for token in ("683", "8192", "823", "9874", "1734", "20802"):
        assert token not in source
    tree = ast.parse(source)
    text_literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text_literals.append(node.value)
    assert "SF001" not in text_literals
    assert "TR007" not in text_literals
    assert "TR011" not in text_literals
    assert "build_optimized_packages" in source
    assert "del product_recs" in source


def test_demo_catalog_is_input_not_package_return(demo_repo: DataRepository):
    catalog_ids = {str(pid) for pid in demo_repo.active_products()["product_id"].tolist()}
    assert catalog_ids == demo_product_ids()
    assert len(catalog_ids) == 12
    candidates = load_candidate_products(demo_repo, 30.0)
    assert {c["product_id"] for c in candidates} == catalog_ids
    source = (ROOT / "app" / "data" / "demo_catalog.py").read_text(encoding="utf-8")
    assert "wellnessPackages" not in source
    assert "products_included" not in source


def test_package_output_comes_from_optimizer_and_ignores_matcher_recs(demo_repo: DataRepository):
    packages = _run_optimizer(demo_repo)
    assert [pkg["tier"] for pkg in packages] == ["essential", "balanced", "optimal"]
    selected = _all_ids(packages)
    assert selected
    assert selected <= demo_product_ids()
    observatory = packages[0].get("observatory") or {}
    assert observatory.get("formula_id") == "PACKAGE_OPTIMIZER_V2_1"
    assert observatory.get("code_file") == "app/agent/package_optimizer.py"
    assert observatory.get("function") == "build_optimized_packages"
    assert "SHOULD_BE_IGNORED" not in selected


def test_catalog_mutation_removes_dropped_sku(demo_repo: DataRepository):
    baseline = _run_optimizer(demo_repo)
    baseline_ids = _all_ids(baseline)
    assert "SF001" in baseline_ids

    products = demo_repo.active_products()
    pricing = demo_repo.product_pricing()
    components = demo_repo.product_components()
    feeding = demo_repo.product_feeding_rules()
    functions = demo_repo.product_functions()
    mutated = _CatalogViewRepo(
        demo_repo,
        products=products[products["product_id"].astype(str) != "SF001"].copy(),
        pricing=pricing[pricing["product_id"].astype(str) != "SF001"].copy(),
        components=components[components["product_id"].astype(str) != "SF001"].copy(),
        feeding=feeding[feeding["product_id"].astype(str) != "SF001"].copy(),
        functions=functions[functions["product_id"].astype(str) != "SF001"].copy(),
    )
    mutated_packages = _run_optimizer(mutated)
    mutated_ids = _all_ids(mutated_packages)
    assert "SF001" not in mutated_ids
    assert mutated_ids
    assert mutated_ids <= (demo_product_ids() - {"SF001"})
    assert _package_ids(mutated_packages) != _package_ids(baseline)


def test_price_mutation_changes_package_economics(demo_repo: DataRepository):
    baseline = _run_optimizer(demo_repo)
    baseline_econ = _package_economics(baseline)
    pricing = demo_repo.product_pricing().copy()
    mask = pricing["product_id"].astype(str) == "SF001"
    assert mask.any()
    pricing.loc[mask, "list_price_rmb"] = pricing.loc[mask, "list_price_rmb"] + 100
    mutated = _CatalogViewRepo(demo_repo, pricing=pricing)
    changed = _run_optimizer(mutated)
    changed_econ = _package_economics(changed)
    assert _package_ids(changed) == _package_ids(baseline)
    assert "SF001" in _all_ids(changed)
    assert changed_econ != baseline_econ
    for tier, (monthly, yearly, _disc) in changed_econ.items():
        base_monthly, base_yearly, _ = baseline_econ[tier]
        if "SF001" in _package_ids(baseline).get(tier, []):
            assert yearly > base_yearly
            assert monthly > base_monthly


def test_analyze_spy_executes_optimizer_not_llm(demo_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []
    import app.agent.package_optimizer as optimizer_mod

    original = optimizer_mod.build_optimized_packages

    def _spy(*args, **kwargs):
        calls.append("build_optimized_packages")
        recs = kwargs.get("product_recs")
        if recs is None and len(args) >= 5:
            recs = args[4]
        assert recs is not None
        return original(*args, **kwargs)

    monkeypatch.setattr(optimizer_mod, "build_optimized_packages", _spy)
    response = demo_client.post("/api/v1/analyze", json=_dolly_json())
    assert response.status_code == 200
    assert calls == ["build_optimized_packages"]
    body = response.json()
    assert body.get("productRecommendations") == [] or isinstance(body.get("productRecommendations"), list)
    packages = body["wellnessPackages"]
    assert _all_ids(packages) <= demo_product_ids()
    fx = (packages[0].get("formula_execution") or {})
    assert fx.get("formula_id") == "PACKAGE_OPTIMIZER_V2_1"


def test_no_llm_or_external_ai_dependency_in_optimizer_path():
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for token in _AI_DEPENDENCY_TOKENS:
        assert token not in req
    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8").lower()
        for token in _AI_DEPENDENCY_TOKENS:
            assert token not in text
    optimizer = OPTIMIZER_PATH.read_text(encoding="utf-8").lower()
    assembler = ASSEMBLER_PATH.read_text(encoding="utf-8").lower()
    for token in _AI_DEPENDENCY_TOKENS:
        assert token not in optimizer
        assert token not in assembler
    assert "import openai" not in optimizer
    assert "requests." not in optimizer
    assert "httpx" not in optimizer


def test_no_ai_credentials_required_for_same_packages(demo_repo: DataRepository):
    first = _package_ids(_run_optimizer(demo_repo))
    second = _package_ids(_run_optimizer(demo_repo))
    assert first == second
    assert _all_ids(_run_optimizer(demo_repo)) <= demo_product_ids()


def test_determinism_three_runs(demo_repo: DataRepository):
    runs = [_run_optimizer(demo_repo) for _ in range(3)]
    id_runs = [_package_ids(run) for run in runs]
    econ_runs = [_package_economics(run) for run in runs]
    rec_runs = [[bool(pkg.get("recommended")) for pkg in run] for run in runs]
    assert id_runs[0] == id_runs[1] == id_runs[2]
    assert econ_runs[0] == econ_runs[1] == econ_runs[2]
    assert rec_runs[0] == rec_runs[1] == rec_runs[2]


def test_frontend_does_not_generate_packages():
    sku_pattern = re.compile(r"\b(SF001|TR007|TR011)\b")
    for path in _FRONTEND_ASSETS:
        text = path.read_text(encoding="utf-8")
        assert "products_included = [" not in text
        assert "wellnessPackages = [" not in text
        assert "Demo Fresh Beef Bowl" not in text
        for token in ("8192", "9874", "20802", "¥683", "¥823", "¥1,734"):
            assert token not in text
        if path.name == "app.js":
            # Grooming session narrative may list historical productIds. That is not
            # PACKAGE_OPTIMIZER_V2_1 membership. Care-package code must not invent SKUs.
            package_region = text.split("async function loadClinicalReport", 1)[-1]
            assert sku_pattern.search(package_region) is None
            assert "sessions" in text
            continue
        assert sku_pattern.search(text) is None, f"{path.name} contains catalog SKUs"


def test_three_surfaces_share_one_optimizer_result(demo_client: TestClient):
    correlation = "omega97a-package-provenance"
    response = demo_client.post(
        "/api/v1/presentation/three-surfaces",
        headers={"x-wagtopia-correlation-id": correlation},
        json=_dolly_json(),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["presentation_correlation_id"] == correlation
    analyze = demo_client.post("/api/v1/analyze", json=_dolly_json()).json()
    runtime_ids = _package_ids(analyze["wellnessPackages"])
    runtime_econ = _package_economics(analyze["wellnessPackages"])
    customer_comp = body["customer"]["wellness"]["package_composition"]
    business_comp = body["business"]["portfolio"]["package_composition"]
    developer = body["developer"]
    customer_ids = {
        str(pkg.get("tier")): [str(p.get("product_id")) for p in (pkg.get("products") or []) if p.get("product_id")]
        for pkg in customer_comp
    }
    business_ids = {
        str(pkg.get("tier")): [str(p.get("product_id")) for p in (pkg.get("products") or []) if p.get("product_id")]
        for pkg in business_comp
    }
    assert customer_ids == runtime_ids
    assert business_ids == runtime_ids
    for pkg in customer_comp:
        tier = str(pkg.get("tier"))
        monthly, yearly, _ = runtime_econ[tier]
        assert pkg.get("monthly_cost") == monthly
        assert pkg.get("yearly_cost") == yearly
    opt = developer["package_optimization"]
    assert opt["formula_id"] == "PACKAGE_OPTIMIZER_V2_1"
    assert opt["function"] == "build_optimized_packages"
    assert opt["independent_of_product_match"] is True
    assert opt["does_not_consume"] == "analyze.productRecommendations"
    assert isinstance(developer["catalog_input"]["scientific_matcher_available"], bool)
    # Warehouse biology is loaded; matcher availability must not change package membership.
    assert "PRODUCT_MATCH_V2_1" in developer["pipeline"]
    assert "PACKAGE_OPTIMIZER_V2_1" in developer["pipeline"]


def test_package_product_ids_exist_in_active_catalog(demo_repo: DataRepository):
    catalog = {str(pid) for pid in demo_repo.active_products()["product_id"].tolist()}
    packages = _run_optimizer(demo_repo)
    selected = _all_ids(packages)
    assert selected <= catalog
    pricing = {
        str(row["product_id"]): float(row["list_price_rmb"])
        for _, row in demo_repo.product_pricing().iterrows()
    }
    for pkg in packages:
        raw = sum(pricing[pid] for pid in _package_ids(packages)[pkg["tier"]] if pid in pricing)
        assert pkg["yearly_cost"] is not None
        assert raw >= 0
        discount = float(pkg.get("yearly_discount_factor") or 0)
        assert 0 < discount <= 1


def test_balanced_is_the_recommended_tier(demo_repo: DataRepository):
    packages = _run_optimizer(demo_repo)
    flags = {pkg["tier"]: bool(pkg.get("recommended")) for pkg in packages}
    assert flags == {"essential": False, "balanced": True, "optimal": False}


def test_dead_legacy_tier_helper_is_not_the_runtime_path():
    assembler = ASSEMBLER_PATH.read_text(encoding="utf-8")
    assert "def _tier_product_ids" in assembler
    assert assembler.count("_tier_product_ids(") == 1
    wellness = assembler.split("def build_wellness_packages", 1)[1].split("\ndef ", 1)[0]
    assert "build_optimized_packages" in wellness
    assert "_tier_product_ids" not in wellness
