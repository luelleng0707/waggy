"""FastAPI entrypoint — Python is the sole production PPIE runtime."""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response

from app.agent.version import ALGORITHM_VERSION
from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.ai.agent import AnalysisMismatchError, WaggyExplanationAgent
from app.ai.config import configured_provider_name, get_provider, provider_status
from app.ai.events import current_projection, events_for, record_event
from app.ai.models import ExplainRequest, ProfileEventRequest
from app.ai.version import WAGGY_AI_POLICY_VERSION, WAGGY_AI_RESPONSE_SCHEMA
from app.tools.errors import http_status_for_envelope
from app.tools.gateway import WaggyToolGateway
from app.tools.models import ToolCaller, ToolInvokeRequest
from app.state.errors import DogStateError
from app.state.groomer import apply_groomer_update, get_groomer_session, observations_for_legacy_analyze
from app.state.models import (
    DogCreateRequest,
    DogEventRequest,
    DogPatchRequest,
    PreferenceCreateRequest,
    RecomputationRequest,
)
from app.state.package_constraints import constraints_from_dog, using_package_constraints
from app.state.preferences import persist_durable_feedback, persist_explicit_preference
from app.state.recalculation import explain_from_digests
from app.state.recompute import (
    apply_preference_change,
    effective_input_snapshot,
    effective_profile,
    latest_analysis,
    require_expected_signature,
)
from app.state.service import persist_workbench_run
from app.state.store import (
    analyses_for,
    create_dog,
    get_dog,
    patch_dog,
    preferences_for,
    require_dog,
)
from app.api.evidence import get_evidence_for_condition, get_products_for_condition
from app.api.evidence_report import read_evidence_report
from app.api.http_models import (
    HTTP_API_VERSION,
    AnalyzeRawResponse,
    AnalyzeRequest,
    ApiErrorResponse,
    WorkbenchPresentationResponse,
    WorkbenchRequest,
)
from app.api.payload_adapter import (
    WorkbenchInputError,
    map_legacy_response,
    profile_from_analyze_body,
    profile_from_workbench_body,
)
from app.core.paths import clinical_root_str, resolve_clinical_root
from app.data.clinical_assessment import MODULE_IDS, build_clinical_assessment, get_assessment_module
from app.data.clinical_report_builder import build_clinical_report
from app.data.demo_catalog import demo_mode_enabled
from app.data.report_generator import build_standard_report
from app.data.report_models import build_all_report_models
from app.debug.clinical_execution_debug import (
    DEFAULT_PRESET_ID,
    build_engine_trace,
    build_validation_console,
    compare_analyses,
    console_to_markdown,
    debug_status_payload,
    get_preset_body,
    is_engine_debug,
    is_local_dev_boot,
    list_presets,
    list_repository_tables,
    maybe_open_validation_console,
    preview_table,
    print_developer_banner,
)
from app.presentation.adapter import (
    analysis_signature,
    build_three_surface_presentations,
    build_workbench_presentations,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ppie.api")

ROOT = Path(__file__).resolve().parents[2]
_legacy_python_root = ROOT / "legacy"
if _legacy_python_root.is_dir() and str(_legacy_python_root) not in sys.path:
    # Compatibility packages (authoring, ontology, curation) live under legacy/.
    sys.path.insert(0, str(_legacy_python_root))
# Clinical CSVs load exclusively from warehouse/current (see app.core.paths).
DATA_DIR = clinical_root_str()
VALID_KEYS = {
    k.strip()
    for k in os.getenv("API_KEYS", "").split(",")
    if k.strip()
}


def _request_wants_debug(request: Request) -> bool:
    debug_q = request.query_params.get("debug")
    return str(debug_q or "").strip().lower() in ("1", "true", "yes", "on")


def _provided_surface_key(request: Request) -> str:
    return (
        request.headers.get("x-wagtopia-access-key")
        or request.query_params.get("access_key")
        or request.cookies.get("wagtopia_access_key")
        or ""
    )


def _require_surface_access(request: Request, *, env_var: str, surface: str) -> None:
    expected = str(os.getenv(env_var, "")).strip()
    if not expected:
        return
    provided = _provided_surface_key(request).strip()
    if provided != expected:
        raise HTTPException(
            status_code=401,
            detail=f"{surface} surface requires access key via x-wagtopia-access-key or ?access_key=",
        )


def _require_debug(request: Request) -> None:
    if not is_engine_debug(request_debug=_request_wants_debug(request)):
        raise HTTPException(
            status_code=403,
            detail="Developer tools disabled. Set PPIE_DEBUG=true or pass ?debug=1.",
        )
    _require_surface_access(request, env_var="WAGTOPIA_DEVELOPER_ACCESS_KEY", surface="developer")


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    print_developer_banner()
    maybe_open_validation_console()
    yield


app = FastAPI(
    title="Wagtopia PPIE Wellness Agent API",
    version=HTTP_API_VERSION,
    description=(
        "HTTP API version (this OpenAPI `info.version`) is **v1**, not the engine version. "
        "Engine version is ALGORITHM_VERSION on analyze payloads (`version`) and "
        "`X-PPIE-Algorithm-Version`. "
        "POST /api/v1/analyze returns the raw engine JSON from "
        "PPIEWellnessAgent.generate_reproducible_report (legacy silent defaults; "
        "optional in-memory groomer session merge; API_KEYS when configured). "
        "POST /api/v1/presentation/workbench is the canonical application contract: "
        "fail-closed request validation, one engine call, four role projections. "
        "These two responses are not the same. There are no /api/v1/analyze/{role} routes."
    ),
    lifespan=_lifespan,
)
agent = PPIEWellnessAgent(data_dir=DATA_DIR)
_last_validation_console_doc: dict[str, Any] | None = None
_last_execution_index: dict[str, dict[str, Any]] = {}

# Hot-reload CSVs under data/ without restarting the API process.
try:
    from app.data.watcher import start_data_watcher

    start_data_watcher(DATA_DIR)
except Exception:  # noqa: BLE001
    logger.exception("Failed to start data watcher — hot reload disabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_timing(request: Request, call_next):
    started = datetime.now(timezone.utc)
    t0 = started.timestamp()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled exception path=%s", request.url.path)
        raise
    elapsed_ms = round((datetime.now(timezone.utc).timestamp() - t0) * 1000, 1)
    response.headers["X-PPIE-Elapsed-Ms"] = str(elapsed_ms)
    response.headers["X-PPIE-Algorithm-Version"] = ALGORITHM_VERSION
    try:
        response.headers["X-PPIE-Data-Version"] = str(agent.repo.version)
        response.headers["X-PPIE-Csv-Hash"] = str(agent.repo.csv_hash)
    except Exception:  # noqa: BLE001
        pass
    if request.url.path.startswith("/api") or request.url.path == "/health":
        logger.info(
            "request method=%s path=%s status=%s elapsed_ms=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
    return response


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not VALID_KEYS:
        return ""
    if not x_api_key or x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing x-api-key")
    return x_api_key


def _apply_surface_cookie(
    *,
    response: Response,
    request: Request,
    env_var: str,
) -> None:
    expected = str(os.getenv(env_var, "")).strip()
    if not expected:
        return
    provided = _provided_surface_key(request).strip()
    if provided != expected:
        return
    if request.cookies.get("wagtopia_access_key", "").strip() == expected:
        return
    response.set_cookie(
        key="wagtopia_access_key",
        value=expected,
        httponly=True,
        samesite="lax",
        secure=False,
    )


@app.get("/health")
async def health() -> dict[str, Any]:
    csv_ok = True
    csv_detail = "ok"
    meta = {
        "data_version": None,
        "csv_hash": None,
        "loaded_files": 0,
        "loaded_at": None,
    }
    try:
        from app.data.runtime import platform_meta

        pm = platform_meta()
        meta = {
            "data_version": pm.version,
            "csv_hash": pm.csv_hash,
            "loaded_files": pm.file_count,
            "loaded_at": pm.loaded_at,
        }
        breeds = agent.repo.breeds()
        if breeds.empty:
            csv_ok = False
            csv_detail = "BREEDS.csv empty or missing"
        else:
            csv_detail = f"breeds_loaded={len(breeds)}"
    except Exception as exc:  # noqa: BLE001
        csv_ok = False
        csv_detail = str(exc)
    return {
        "status": "ok" if csv_ok else "degraded",
        "engine": "PPIE",
        "version": ALGORITHM_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "runtime": "python",
        "csv": {"ok": csv_ok, "detail": csv_detail},
        "data_version": meta["data_version"],
        "csv_hash": meta["csv_hash"],
        "loaded_files": meta["loaded_files"],
        "loaded_at": meta["loaded_at"],
        "demo_catalog": demo_mode_enabled(),
        "demo_mode": demo_mode_enabled(),
        "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
        "catalog_count": int(len(agent.repo.active_products())),
    }


def _filter_product_rows(
    rows: list[dict[str, Any]],
    *,
    category: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    if category:
        cat = category.lower()
        rows = [
            r for r in rows
            if cat in str(r.get("category", "")).lower()
            or cat in str(r.get("subcategory", "")).lower()
        ]
    if q:
        query = q.lower()
        rows = [
            r for r in rows
            if query in str(r.get("product_name") or r.get("name") or "").lower()
            or query in str(r.get("product_id", "")).lower()
            or query in str(r.get("brand", "")).lower()
            or query in str(r.get("category", "")).lower()
            or query in str(r.get("subcategory", "")).lower()
        ]
    return rows


def _joined_catalog_payload(
    *,
    category: str | None = None,
    q: str | None = None,
    weight_kg: float | None = None,
) -> dict[str, Any]:
    rows = _filter_product_rows(
        agent.repo.store_api_rows(weight_kg=weight_kg),
        category=category,
        q=q,
    )
    return {
        "products": rows,
        "count": len(rows),
        "weight_kg": weight_kg,
        "data_version": agent.repo.version,
        "csv_hash": agent.repo.csv_hash,
        "loaded_at": agent.repo.loaded_at,
        "demo_catalog": demo_mode_enabled(),
        "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
    }


@app.get("/api/v1/catalog")
async def product_catalog(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> dict[str, Any]:
    """Read-only product catalog from PRODUCT_* CSVs — no hardcoded products."""
    rows = _filter_product_rows(agent.repo.catalog_api_rows(), category=category, q=q)
    return {
        "products": rows,
        "count": len(rows),
        "data_version": agent.repo.version,
        "csv_hash": agent.repo.csv_hash,
        "demo_catalog": demo_mode_enabled(),
        "catalog_source": "demo" if demo_mode_enabled() else "warehouse",
    }


@app.get("/api/v1/presentation/catalog")
async def presentation_catalog(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    weight_kg: float | None = Query(default=None),
) -> dict[str, Any]:
    """Browser-safe read-only catalog for customer/business presentation surfaces."""
    return _joined_catalog_payload(category=category, q=q, weight_kg=weight_kg)


@app.get("/api/v1/store")
async def product_store(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    weight_kg: float | None = Query(default=None),
) -> dict[str, Any]:
    """
    Read-only joined storefront payload — catalog + pricing + components + feeding
    + supplement/bakery extensions. Frontend should render this, not join CSVs.
    Mutations remain on separate authenticated endpoints.
    """
    return _joined_catalog_payload(category=category, q=q, weight_kg=weight_kg)


@app.get("/api/v1/store/{product_id}")
async def product_store_detail(
    product_id: str,
    weight_kg: float | None = Query(default=None),
) -> dict[str, Any]:
    rows = agent.repo.store_api_rows(weight_kg=weight_kg)
    match = next((r for r in rows if str(r.get("product_id")) == product_id), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")
    return {
        "product": match,
        "data_version": agent.repo.version,
        "csv_hash": agent.repo.csv_hash,
    }


@app.post("/api/v2/wellness/evaluate")
async def evaluate_dog_profile(profile: DogProfileInput) -> dict[str, Any]:
    try:
        return await agent.generate_reproducible_report(profile)
    except Exception as exc:
        logger.exception("Agent pipeline failure")
        raise HTTPException(
            status_code=500,
            detail=f"Agent Pipeline Execution Failure: {exc}",
        ) from exc


@app.post(
    "/api/v1/analyze",
    response_model=None,
    responses={
        200: {
            "model": AnalyzeRawResponse,
            "description": (
                "Raw generate_reproducible_report JSON. Not a workbench projection. "
                "Does not include roles.* or workbench_presentation.v1."
            ),
        },
        400: {"description": "Malformed request (legacy string detail)."},
    },
)
async def analyze_v1(
    body: AnalyzeRequest,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    payload = body.model_dump()
    pet_key = str(payload.get("pet_name") or payload.get("petName") or "").lower()
    extra = observations_for_legacy_analyze(pet_key)
    observed = list(payload.get("observed_conditions") or [])
    if extra:
        observed = list(dict.fromkeys([*observed, *extra]))
    payload = {**payload, "observed_conditions": observed}
    try:
        profile = profile_from_analyze_body(payload)
        return await agent.generate_reproducible_report(profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("analyze failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/presentation/three-surfaces")
async def presentation_three_surfaces(
    request: Request,
) -> dict[str, Any]:
    """Single-analysis projection for customer/business/developer surfaces."""
    _require_surface_access(request, env_var="WAGTOPIA_BUSINESS_ACCESS_KEY", surface="business")
    body = await request.json()
    try:
        profile = profile_from_analyze_body(body)
        analyze = await agent.generate_reproducible_report(profile)
        assessment = build_clinical_assessment(agent.repo, analyze)
        console = None
        if _request_wants_debug(request):
            _require_debug(request)
            console = build_validation_console(agent.repo, analyze, assessment, raw_request=body)
        corr = request.headers.get("x-wagtopia-correlation-id") or f"presentation-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        return build_three_surface_presentations(
            analyze,
            assessment,
            console,
            correlation_id=corr,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("three-surface presentation failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _split_workbench_body(body: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    """Base analyze fields + role context. Role context is stored, not a second engine."""
    role_context = body.get("role_context") if isinstance(body.get("role_context"), dict) else {}
    correlation_id = body.get("correlation_id")
    analyze_body = {
        key: value
        for key, value in body.items()
        if key not in {"role_context", "correlation_id", "dog_id"}
    }
    groomer = role_context.get("groomer") if isinstance(role_context.get("groomer"), dict) else {}
    extra = groomer.get("observed_conditions")
    if isinstance(extra, list) and extra:
        existing = [str(item) for item in (analyze_body.get("observed_conditions") or [])]
        merged = list(dict.fromkeys([*existing, *[str(item) for item in extra if item]]))
        analyze_body["observed_conditions"] = merged
    return analyze_body, role_context, str(correlation_id) if correlation_id else None


def _dog_state_error(exc: DogStateError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content=exc.to_http_body())


async def _run_workbench_analysis(
    profile,
    *,
    dog_id: str | None,
    role_context: dict[str, Any] | None,
    analyze_body: dict[str, Any],
    correlation_id: str | None,
    request: Request,
    apply_stored_preferences: bool,
    preference_changes: list[dict[str, Any]] | None = None,
):
    constraints = constraints_from_dog(dog_id) if dog_id and apply_stored_preferences else None
    with using_package_constraints(constraints):
        analyze = await agent.generate_reproducible_report(profile)
    assessment = build_clinical_assessment(agent.repo, analyze)
    console = None
    if _request_wants_debug(request):
        _require_debug(request)
        console = build_validation_console(
            agent.repo, analyze, assessment, raw_request=analyze_body
        )
    corr = (
        request.headers.get("x-wagtopia-correlation-id")
        or correlation_id
        or analysis_signature(analyze)
    )
    envelope = build_workbench_presentations(
        analyze,
        assessment,
        console,
        correlation_id=corr,
        role_context=role_context,
    )
    envelope["api_version"] = HTTP_API_VERSION
    envelope["engine_version"] = ALGORITHM_VERSION
    envelope["warehouse_version"] = agent.repo.version
    if constraints is not None:
        envelope["effective_preferences"] = constraints.as_dict()
    explanation = None
    if dog_id:
        previous = latest_analysis(dog_id)
        explanation = persist_workbench_run(
            dog_id=dog_id,
            profile=profile,
            envelope=envelope,
            role_context=role_context,
            engine_version=ALGORITHM_VERSION,
            warehouse_version=agent.repo.version,
            input_snapshot=effective_input_snapshot(profile, constraints) if constraints is not None else None,
            previous=previous,
            preference_changes=preference_changes,
        )
    return envelope, explanation


@app.post(
    "/api/v1/presentation/workbench",
    response_model=None,
    responses={
        200: {
            "model": WorkbenchPresentationResponse,
            "description": (
                "One generate_reproducible_report call projected for customer, "
                "groomer, business, and developer. Fail-closed input. No silent "
                "age/weight/activity/environment defaults. No hidden groomer session merge."
            ),
        },
        400: {
            "model": ApiErrorResponse,
            "description": "Typed validation error (MISSING_REQUIRED_INPUT / INVALID_INPUT).",
        },
    },
)
async def presentation_workbench(body: WorkbenchRequest, request: Request) -> JSONResponse | dict[str, Any]:
    """ONE analysis → customer / groomer / business / developer projections.

    Browser-safe like /api/v1/clinical-report. Does not invent a second optimizer.
    Canonical workbench contract: not the raw /api/v1/analyze response.
    """
    payload = body.model_dump()
    analyze_body, role_context, body_corr = _split_workbench_body(payload)
    try:
        dog_id = str(payload.get("dog_id") or "").strip()
        if dog_id:
            require_dog(dog_id)
        profile = profile_from_workbench_body(payload)
        envelope, _explanation = await _run_workbench_analysis(
            profile,
            dog_id=dog_id or None,
            role_context=role_context,
            analyze_body=analyze_body,
            correlation_id=body_corr,
            request=request,
            apply_stored_preferences=bool(dog_id),
        )
        return envelope
    except DogStateError as exc:
        return _dog_state_error(exc)
    except WorkbenchInputError as exc:
        return JSONResponse(status_code=400, content=exc.to_http_body())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("workbench presentation failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/ai/status")
async def ai_status() -> dict[str, Any]:
    """AI layer availability. Canonical analysis does not use this path."""
    status = provider_status()
    status.update(
        {
            "schema": WAGGY_AI_RESPONSE_SCHEMA,
            "ai_policy_version": WAGGY_AI_POLICY_VERSION,
            "configured_provider": configured_provider_name(),
        }
    )
    return status


@app.post("/api/v1/ai/explain")
async def ai_explain(body: ExplainRequest) -> dict[str, Any]:
    """Explain an existing canonical result. Does not run the engine or optimizer."""
    try:
        result = WaggyExplanationAgent(get_provider()).explain(body)
    except AnalysisMismatchError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "ANALYSIS_MISMATCH", "message": str(exc), "field": "analysis_signature"}},
        )
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_INPUT", "message": str(exc), "field": None}},
        )
    if body.dog_id:
        try:
            persist_durable_feedback(body.dog_id, result.feedback, result.proposed_constraints)
        except DogStateError:
            pass
    return result.model_dump(by_alias=True)


def _tool_catalog_rows() -> list[dict[str, Any]]:
    return list(agent.repo.store_api_rows() or [])


@app.post("/api/v1/ai/tools/invoke")
async def ai_tools_invoke(body: ToolInvokeRequest) -> dict[str, Any]:
    """Allowlisted internal tool invocation. Not MCP. Does not run the engine."""
    gateway = WaggyToolGateway(catalog_loader=_tool_catalog_rows)
    caller = ToolCaller(
        role=body.role,
        owner_id=body.owner_id,
        authorized_dog_ids=body.authorized_dog_ids,
        actor=body.actor,
    )
    envelope = gateway.invoke(body.tool, body.arguments, caller, request_id=body.request_id)
    payload = envelope.model_dump(by_alias=True)
    status = http_status_for_envelope(envelope.status, envelope.errors)
    if status == 200:
        return payload
    return JSONResponse(status_code=status, content=payload)


@app.post("/api/v1/profile/events")
async def create_profile_event(body: ProfileEventRequest) -> dict[str, Any]:
    """Authorized application event. Not a warehouse write and not an engine run."""
    try:
        event = record_event(
            dog_id=body.dog_id,
            source=body.source,
            kind=body.kind,
            value=body.value,
            session_id=body.session_id,
            confirmed=body.confirmed,
            notes=body.notes,
        )
    except DogStateError as exc:
        return _dog_state_error(exc)
    except ValueError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_INPUT", "message": str(exc), "field": "source"}},
        )
    return event.model_dump(by_alias=True)


@app.get("/api/v1/profile/events")
async def list_profile_events(dog_id: str) -> dict[str, Any]:
    return {
        "dog_id": dog_id,
        "events": [item.model_dump(by_alias=True) for item in events_for(dog_id)],
        "projection": current_projection(dog_id),
    }


def _event_kind_for_type(event_type: str) -> str:
    return {
        "GROOMER_OBSERVATION": "observation",
        "USER_STATEMENT": "observation",
        "USER_PREFERENCE": "preference",
        "PROFILE_UPDATE": "profile_update",
        "PACKAGE_INTERACTION": "package_interaction",
        "ANALYSIS_RUN": "analysis_snapshot",
        "SYSTEM_EVENT": "system",
    }.get(event_type, "system")


@app.post("/api/v1/dogs")
async def create_persisted_dog(body: DogCreateRequest) -> dict[str, Any]:
    """Create a persistent dog. Does not run the engine and does not write warehouse facts."""
    try:
        dog = create_dog(body)
    except DogStateError as exc:
        return _dog_state_error(exc)
    return dog.model_dump(by_alias=True)


@app.get("/api/v1/dogs/{dog_id}")
async def get_persisted_dog(dog_id: str) -> dict[str, Any]:
    dog = get_dog(dog_id)
    if dog is None:
        return _dog_state_error(DogStateError("DOG_NOT_FOUND", f"dog {dog_id} was not found", field="dog_id", status=404))
    return dog.model_dump(by_alias=True)


@app.patch("/api/v1/dogs/{dog_id}")
async def patch_persisted_dog(dog_id: str, body: DogPatchRequest) -> dict[str, Any]:
    try:
        dog = patch_dog(dog_id, body)
    except DogStateError as exc:
        return _dog_state_error(exc)
    return dog.model_dump(by_alias=True)


@app.post("/api/v1/dogs/{dog_id}/events")
async def create_dog_event(dog_id: str, body: DogEventRequest) -> dict[str, Any]:
    try:
        require_dog(dog_id)
        if body.source not in {"GROOMER", "USER", "SYSTEM"}:
            raise DogStateError(
                "SCIENTIFIC_EVENT_FORBIDDEN" if body.source == "SCIENTIFIC" else "INVALID_EVENT_TYPE",
                "unsupported event source",
                field="source",
            )
        event = record_event(
            dog_id=dog_id,
            source=body.source,  # type: ignore[arg-type]
            kind=_event_kind_for_type(body.event_type),  # type: ignore[arg-type]
            value=body.value or str((body.payload or {}).get("observation") or (body.payload or {}).get("value") or body.event_type),
            session_id=body.session_id,
            confirmed=body.confirmed,
            notes=body.notes,
            event_type=body.event_type,
            payload=body.payload,
            status=body.status,
            correlation_id=body.correlation_id,
            public=True,
            observed_at=body.observed_at,
        )
    except DogStateError as exc:
        return _dog_state_error(exc)
    return event.model_dump(by_alias=True)


@app.get("/api/v1/dogs/{dog_id}/events")
async def list_dog_events(dog_id: str) -> dict[str, Any]:
    try:
        require_dog(dog_id)
    except DogStateError as exc:
        return _dog_state_error(exc)
    return {
        "dog_id": dog_id,
        "events": [item.model_dump(by_alias=True) for item in events_for(dog_id)],
        "projection": current_projection(dog_id),
    }


@app.get("/api/v1/dogs/{dog_id}/evidence-report")
async def get_dog_evidence_report(
    dog_id: str,
    observation_type: str | None = None,
    as_of: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Read-only longitudinal evidence report. Does not diagnose or persist."""
    try:
        return read_evidence_report(
            dog_id,
            observation_type=observation_type,
            as_of=as_of,
            generated_at=generated_at,
        )
    except DogStateError as exc:
        return _dog_state_error(exc)


@app.get("/api/v1/dogs/{dog_id}/preferences")
async def list_dog_preferences(dog_id: str) -> dict[str, Any]:
    try:
        require_dog(dog_id)
    except DogStateError as exc:
        return _dog_state_error(exc)
    return {
        "dog_id": dog_id,
        "preferences": [item.model_dump(by_alias=True) for item in preferences_for(dog_id)],
    }


@app.post("/api/v1/dogs/{dog_id}/preferences")
async def create_dog_preference(dog_id: str, body: PreferenceCreateRequest) -> dict[str, Any]:
    try:
        record = persist_explicit_preference(
            dog_id,
            category=body.category,
            value=body.value,
            status=body.status,
            source=body.source,
        )
    except DogStateError as exc:
        return _dog_state_error(exc)
    return record.model_dump(by_alias=True)


@app.post("/api/v1/dogs/{dog_id}/recompute")
async def recompute_persisted_dog(
    dog_id: str,
    request: Request,
    body: RecomputationRequest | None = None,
) -> dict[str, Any]:
    """Persist a validated preference change and run a NEW deterministic analysis.

    Does not overwrite prior analysis rows. Does not run the AI layer.
    Ingredient exclusions constrain catalog eligibility only. Budget uses the
    existing optimizer monthly_budget field. Nutrient min/max are unchanged.
    """
    payload = body or RecomputationRequest()
    if payload.provenance == "SCIENTIFIC":
        return _dog_state_error(
            DogStateError(
                "SCIENTIFIC_EVENT_FORBIDDEN",
                "preferences cannot write scientific facts",
                field="provenance",
            )
        )
    try:
        require_expected_signature(dog_id, payload.expected_analysis_signature)
        previous = latest_analysis(dog_id)
        saved, before, after, changed = apply_preference_change(
            dog_id,
            payload.preference_change,
            source=payload.provenance or "USER",
        )
        profile = effective_profile(dog_id, after)
        envelope, explanation = await _run_workbench_analysis(
            profile,
            dog_id=dog_id,
            role_context=None,
            analyze_body={},
            correlation_id=(
                payload.correlation_id
                or request.headers.get("x-wagtopia-correlation-id")
                or f"recompute-{dog_id}"
            ),
            request=request,
            apply_stored_preferences=True,
            preference_changes=changed,
        )
        stored = latest_analysis(dog_id)
        return {
            "schema": "preference_recompute.v1",
            "dog_id": dog_id,
            "previous_analysis_id": previous.analysis_id if previous else None,
            "previous_analysis_signature": previous.analysis_signature if previous else None,
            "analysis_id": stored.analysis_id if stored else None,
            "analysis_signature": envelope.get("analysis_signature"),
            "engine_version": envelope.get("engine_version"),
            "optimizer_version": "PACKAGE_OPTIMIZER_V2_1",
            "warehouse_version": envelope.get("warehouse_version"),
            "changed_preferences": changed,
            "effective_preferences": after.as_dict(),
            "previous_preferences": before.as_dict(),
            "persisted_preferences": [item.model_dump(by_alias=True) for item in saved],
            "scientific": False,
            "llm_used": False,
            "explanation": explanation,
            "presentation": envelope,
        }
    except DogStateError as exc:
        return _dog_state_error(exc)
    except WorkbenchInputError as exc:
        return JSONResponse(status_code=400, content=exc.to_http_body())


@app.post("/api/v1/dogs/{dog_id}/analyze")
async def analyze_persisted_dog(dog_id: str, request: Request) -> dict[str, Any]:
    """Project stored dog state to DogProfileInput and run the existing engine once."""
    try:
        constraints = constraints_from_dog(dog_id)
        profile = effective_profile(dog_id, constraints)
        envelope, _explanation = await _run_workbench_analysis(
            profile,
            dog_id=dog_id,
            role_context=None,
            analyze_body={},
            correlation_id=request.headers.get("x-wagtopia-correlation-id") or f"dog-{dog_id}",
            request=request,
            apply_stored_preferences=True,
        )
        return envelope
    except DogStateError as exc:
        return _dog_state_error(exc)
    except WorkbenchInputError as exc:
        return JSONResponse(status_code=400, content=exc.to_http_body())


@app.get("/api/v1/dogs/{dog_id}/analyses/compare")
async def compare_dog_analyses(
    dog_id: str,
    previous_analysis_id: str | None = Query(default=None),
    new_analysis_id: str | None = Query(default=None),
    previous_signature: str | None = Query(default=None),
    new_signature: str | None = Query(default=None),
) -> dict[str, Any]:
    """Diff two stored analysis digests. Does not run the engine or an LLM."""
    try:
        require_dog(dog_id)
    except DogStateError as exc:
        return _dog_state_error(exc)
    rows = analyses_for(dog_id)

    def _by_id(analysis_id: str | None):
        if not analysis_id:
            return None
        for row in rows:
            if row.analysis_id == analysis_id:
                return row
        return None

    def _by_signature(signature: str | None):
        if not signature:
            return None
        matches = [row for row in rows if row.analysis_signature == signature]
        return matches[-1] if matches else None

    previous_row = _by_id(previous_analysis_id) or _by_signature(previous_signature)
    new_row = _by_id(new_analysis_id) or _by_signature(new_signature)
    if previous_row is None and new_row is None and len(rows) >= 2:
        previous_row, new_row = rows[-2], rows[-1]
    if previous_row is None or new_row is None:
        return _dog_state_error(
            DogStateError(
                "COMPARISON_UNAVAILABLE",
                "two stored analyses are required to explain a recommendation change",
                field="previous_analysis_id",
                status=400,
            )
        )
    explanation = explain_from_digests(
        previous_row.result_digest,
        new_row.result_digest,
        previous_signature=previous_row.analysis_signature,
        new_signature=new_row.analysis_signature,
        engine_version=new_row.engine_version,
    )
    return {
        "schema": "analysis_compare.v1",
        "dog_id": dog_id,
        "previous_analysis_id": previous_row.analysis_id,
        "new_analysis_id": new_row.analysis_id,
        "scientific": False,
        "llm_used": False,
        "engine_ran": False,
        "explanation": explanation,
    }


@app.get("/api/v1/dogs/{dog_id}/analyses")
async def list_dog_analyses(dog_id: str) -> dict[str, Any]:
    try:
        require_dog(dog_id)
    except DogStateError as exc:
        return _dog_state_error(exc)
    return {
        "dog_id": dog_id,
        "analyses": [item.model_dump(by_alias=True) for item in analyses_for(dog_id)],
    }


@app.post("/api/v1/clinical-report")
async def clinical_report_v1(
    request: Request,
) -> dict[str, Any]:
    """Standardized clinical report over frozen PPIE analyze output.

    Returns JSON only — never HTML.
    `assessment` is the Phase 17.5 modular ClinicalAssessment contract.
    `report` remains schema-v4 widgets for transitional clients.
    """
    body = await request.json()
    pet_key = str(body.get("pet_name") or body.get("petName") or "").lower()
    extra = observations_for_legacy_analyze(pet_key)
    observed = list(body.get("observed_conditions") or [])
    if extra:
        observed = list(dict.fromkeys([*observed, *extra]))
    body = {**body, "observed_conditions": observed}
    try:
        profile = profile_from_analyze_body(body)
        analyze = await agent.generate_reproducible_report(profile)
        report = build_standard_report(agent.repo, analyze)
        clinical_v3 = build_clinical_report(agent.repo, analyze)
        models = build_all_report_models(agent.repo, analyze)
        assessment = build_clinical_assessment(agent.repo, analyze)
        payload = {
            "analyze": analyze,
            "assessment": assessment,
            "report": report,
            "reportModels": models,
            "clinicalReport": clinical_v3,
        }
        debug_q = request.query_params.get("debug")
        request_debug = str(debug_q or "").strip().lower() in ("1", "true", "yes", "on")
        if is_engine_debug(request_debug=request_debug):
            payload["trace"] = build_engine_trace(agent.repo, analyze, assessment)
        return payload
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("clinical-report failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/ppie/assess")
async def ppie_assess(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    """Stable integration contract: DogProfile-like body → ClinicalAssessment.

    Runs the clinical pipeline once, then projects modular report objects.
    Optional query `module` returns a single module envelope for independent cache.
    When PPIE_DEBUG / DEBUG_ENGINE is true, or `?debug=1`, attaches `trace` (EngineTrace).
    """
    body = await request.json()
    module = request.query_params.get("module")
    debug_q = request.query_params.get("debug")
    request_debug = str(debug_q or "").strip().lower() in ("1", "true", "yes", "on")
    try:
        profile = profile_from_analyze_body(body)
        t0 = datetime.now(timezone.utc).timestamp()
        analyze = await agent.generate_reproducible_report(profile)
        analyze_ms = round((datetime.now(timezone.utc).timestamp() - t0) * 1000, 2)
        t1 = datetime.now(timezone.utc).timestamp()
        assessment = build_clinical_assessment(agent.repo, analyze)
        assess_ms = round((datetime.now(timezone.utc).timestamp() - t1) * 1000, 2)
        if module:
            if module not in MODULE_IDS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown module '{module}'. Expected one of: {', '.join(MODULE_IDS)}",
                )
            mod = get_assessment_module(assessment, module)
            out: dict[str, Any] = {
                "meta": assessment["meta"],
                "module": mod,
            }
            if is_engine_debug(request_debug=request_debug):
                out["trace"] = build_engine_trace(
                    agent.repo,
                    analyze,
                    assessment,
                    timings={"analyze": analyze_ms, "assessment": assess_ms},
                )
            return out
        if is_engine_debug(request_debug=request_debug):
            assessment = {
                **assessment,
                "trace": build_engine_trace(
                    agent.repo,
                    analyze,
                    assessment,
                    timings={"analyze": analyze_ms, "assessment": assess_ms},
                ),
            }
        return assessment
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("ppie assess failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/ppie/trace")
async def ppie_trace(
    request: Request,
) -> dict[str, Any]:
    """Developer-only EngineTrace. Requires PPIE_DEBUG / DEBUG_ENGINE or ?debug=1."""
    body = await request.json()
    debug_q = request.query_params.get("debug")
    request_debug = str(debug_q or "").strip().lower() in ("1", "true", "yes", "on")
    if not is_engine_debug(request_debug=request_debug):
        raise HTTPException(
            status_code=403,
            detail="Engine trace disabled. Set PPIE_DEBUG=true or pass ?debug=1.",
        )
    try:
        profile = profile_from_analyze_body(body)
        t0 = datetime.now(timezone.utc).timestamp()
        analyze = await agent.generate_reproducible_report(profile)
        analyze_ms = round((datetime.now(timezone.utc).timestamp() - t0) * 1000, 2)
        assessment = build_clinical_assessment(agent.repo, analyze)
        return build_engine_trace(
            agent.repo,
            analyze,
            assessment,
            timings={"analyze": analyze_ms},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("ppie trace failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/ppie/validation-console")
async def ppie_validation_console(
    request: Request,
) -> dict[str, Any]:
    """Developer Validation Console document. Requires debug."""
    _require_debug(request)
    body = await request.json()
    try:
        profile = profile_from_analyze_body(body)
        t0 = datetime.now(timezone.utc).timestamp()
        analyze = await agent.generate_reproducible_report(profile)
        analyze_ms = round((datetime.now(timezone.utc).timestamp() - t0) * 1000, 2)
        t1 = datetime.now(timezone.utc).timestamp()
        assessment = build_clinical_assessment(agent.repo, analyze)
        assess_ms = round((datetime.now(timezone.utc).timestamp() - t1) * 1000, 2)
        doc = build_validation_console(
            agent.repo,
            analyze,
            assessment,
            timings={"analyze": analyze_ms, "assessment": assess_ms},
            raw_request=body,
        )
        global _last_validation_console_doc, _last_execution_index
        _last_validation_console_doc = doc
        _last_execution_index = {
            str(x.get("execution_id")): x
            for x in (doc.get("execution_records") or doc.get("formula_executions") or [])
            if isinstance(x, dict) and x.get("execution_id")
        }
        return doc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("validation console failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/ppie/validation-console/markdown")
async def ppie_validation_console_md(
    request: Request,
):
    """Markdown export of Validation Console (debug only)."""
    from fastapi.responses import PlainTextResponse

    _require_debug(request)
    body = await request.json()
    try:
        profile = profile_from_analyze_body(body)
        analyze = await agent.generate_reproducible_report(profile)
        assessment = build_clinical_assessment(agent.repo, analyze)
        doc = build_validation_console(agent.repo, analyze, assessment, raw_request=body)
        return PlainTextResponse(console_to_markdown(doc), media_type="text/markdown")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("validation console markdown failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/v1/ppie/validation-console/compare")
async def ppie_validation_console_compare(
    request: Request,
) -> dict[str, Any]:
    """Side-by-side assessment diff (debug only). Body: {left, right, left_label?, right_label?}."""
    _require_debug(request)
    body = await request.json()
    left_body = body.get("left") or {}
    right_body = body.get("right") or {}
    if not left_body or not right_body:
        raise HTTPException(status_code=400, detail="Body must include left and right profile objects")
    try:
        left_profile = profile_from_analyze_body(left_body)
        right_profile = profile_from_analyze_body(right_body)
        t0 = datetime.now(timezone.utc).timestamp()
        left_analyze = await agent.generate_reproducible_report(left_profile)
        left_ms = round((datetime.now(timezone.utc).timestamp() - t0) * 1000, 2)
        t1 = datetime.now(timezone.utc).timestamp()
        right_analyze = await agent.generate_reproducible_report(right_profile)
        right_ms = round((datetime.now(timezone.utc).timestamp() - t1) * 1000, 2)
        left_assessment = build_clinical_assessment(agent.repo, left_analyze)
        right_assessment = build_clinical_assessment(agent.repo, right_analyze)
        diff = compare_analyses(
            left_analyze,
            right_analyze,
            left_raw=left_body,
            right_raw=right_body,
            left_label=str(body.get("left_label") or left_body.get("name") or "Left"),
            right_label=str(body.get("right_label") or right_body.get("name") or "Right"),
            left_timings={"analyze": left_ms},
            right_timings={"analyze": right_ms},
        )
        return {
            "diff": diff,
            "left_console": build_validation_console(
                agent.repo, left_analyze, left_assessment, raw_request=left_body, timings={"analyze": left_ms}
            ),
            "right_console": build_validation_console(
                agent.repo, right_analyze, right_assessment, raw_request=right_body, timings={"analyze": right_ms}
            ),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("validation console compare failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/ppie/validation-console/execution/{execution_id:path}")
async def ppie_validation_console_execution(
    execution_id: str,
    request: Request,
) -> dict[str, Any]:
    """Read-only execution provenance record from last validation-console run."""
    _require_debug(request)
    if not _last_execution_index:
        raise HTTPException(status_code=404, detail="No execution cache available. Run validation-console first.")
    hit = _last_execution_index.get(execution_id)
    if not hit:
        raise HTTPException(status_code=404, detail=f"Execution not found: {execution_id}")
    return {"schema": "execution_record.v1", "execution": hit}


@app.get("/api/v1/ppie/debug/status")
async def ppie_debug_status(request: Request) -> dict[str, Any]:
    """Boot id / csv hash for live refresh. Requires debug."""
    _require_debug(request)
    return debug_status_payload(agent.repo)


@app.get("/api/v1/ppie/debug/presets")
async def ppie_debug_presets(request: Request) -> dict[str, Any]:
    _require_debug(request)
    return {"schema": "debug_presets.v1", "default": DEFAULT_PRESET_ID, "presets": list_presets()}


@app.get("/api/v1/ppie/debug/repository")
async def ppie_debug_repository(request: Request) -> dict[str, Any]:
    """Read-only manifest table catalog."""
    _require_debug(request)
    return list_repository_tables(agent.repo)


@app.get("/api/v1/ppie/debug/repository/{table}")
async def ppie_debug_repository_table(
    table: str,
    request: Request,
    limit: int = Query(default=25, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None),
) -> dict[str, Any]:
    """Read-only table preview."""
    _require_debug(request)
    try:
        return preview_table(agent.repo, table, limit=limit, offset=offset, q=q)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _graph_repo():
    from app.science.repository import GraphRepository

    return GraphRepository.from_platform(agent.repo.platform)


@app.get("/api/v1/graph/summary")
async def graph_summary(_: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    return {"schema": "knowledge_graph.v1", "summary": grepo.graph.summary()}


@app.get("/api/v1/graph/condition/{condition_id:path}")
async def graph_condition(condition_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    hit = grepo.condition(condition_id)
    if not hit:
        raise HTTPException(status_code=404, detail=f"Condition not found: {condition_id}")
    return {"schema": "graph_entity.v1", "entity": hit}


@app.get("/api/v1/graph/paper/{paper_id:path}")
async def graph_paper(paper_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    hit = grepo.paper(paper_id)
    if not hit:
        raise HTTPException(status_code=404, detail=f"Paper not found: {paper_id}")
    return {"schema": "graph_entity.v1", "entity": hit}


@app.get("/api/v1/graph/ingredient/{ingredient_id:path}")
async def graph_ingredient(ingredient_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    hit = grepo.ingredient(ingredient_id)
    if not hit:
        raise HTTPException(status_code=404, detail=f"Ingredient not found: {ingredient_id}")
    return {"schema": "graph_entity.v1", "entity": hit}


@app.get("/api/v1/graph/product/{product_id:path}")
async def graph_product(product_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    hit = grepo.product(product_id)
    if not hit:
        raise HTTPException(status_code=404, detail=f"Product not found: {product_id}")
    return {"schema": "graph_entity.v1", "entity": hit}


@app.get("/api/v1/graph/explanation/{recommendation_id:path}")
async def graph_explanation(recommendation_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    grepo = _graph_repo()
    return {"schema": "graph_explanation.v1", **grepo.explanation(recommendation_id)}


@app.get("/api/v1/graph/why")
async def graph_why(
    q: str = Query(..., min_length=1),
    kind: str = Query(default="ingredient"),
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    grepo = _graph_repo()
    return {"schema": "graph_why.v1", **grepo.why(q, kind=kind)}


@app.get("/api/v1/science/audit")
async def science_audit(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from app.science.audit import ScientificAudit

    return {"schema": "scientific_audit.v1", **ScientificAudit(agent.repo.platform).build()}


@app.get("/api/v1/science/coverage")
async def science_coverage(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from app.science.coverage import KnowledgeCoverageReport
    from app.science.repository import GraphRepository

    grepo = GraphRepository.from_platform(agent.repo.platform)
    return {"schema": "knowledge_coverage.v1", **KnowledgeCoverageReport(grepo.graph).build()}


@app.get("/api/v1/science/versions")
async def science_versions(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from app.science.versioning import current_science_versions

    return {"schema": "versioned_science.v1", **current_science_versions().to_dict()}


# ── Scientific authoring & research portal (staging only; no clinical math) ──


@app.get("/api/v1/authoring/drafts")
async def authoring_list_drafts(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.models import list_drafts

    return {"schema": "authoring_drafts.v1", "drafts": list_drafts()}


@app.post("/api/v1/authoring/evidence")
async def authoring_create_evidence(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    """Evidence Builder: New Paper → conditions → ingredients → submit (staging only)."""
    body = await request.json()
    from authoring.builder import create_evidence_interactive

    return {"schema": "authoring_evidence.v1", **create_evidence_interactive(body)}


@app.post("/api/v1/authoring/evidence/{draft_id}/materialize")
async def authoring_materialize(draft_id: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.builder import materialize_draft

    return {"schema": "authoring_materialize.v1", **materialize_draft(draft_id)}


@app.get("/api/v1/authoring/ontology")
async def authoring_ontology(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from ontology import CONDITION_ONTOLOGY, INGREDIENT_ONTOLOGY, ontology_summary

    return {
        "schema": "ontology.v1",
        "summary": ontology_summary(),
        "conditions": CONDITION_ONTOLOGY,
        "ingredients": INGREDIENT_ONTOLOGY,
    }


@app.get("/api/v1/authoring/conflicts")
async def authoring_conflicts(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from curation.conflict_resolution import detect_conflicts

    return {"schema": "evidence_conflicts.v1", "conflicts": detect_conflicts()}


@app.get("/api/v1/authoring/duplicates")
async def authoring_duplicates(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from curation.duplicate_detection import (
        suggest_condition_duplicates,
        suggest_ingredient_duplicates,
    )

    return {
        "schema": "duplicate_suggestions.v1",
        "conditions": suggest_condition_duplicates(),
        "ingredients": suggest_ingredient_duplicates(),
    }


@app.get("/api/v1/research/condition/{condition}")
async def research_condition(condition: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {"schema": "research_condition.v1", **ResearchPortal().evidence_for_condition(condition)}


@app.get("/api/v1/research/omega3")
async def research_omega3(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {"schema": "research_omega3.v1", **ResearchPortal().omega3_studies()}


@app.get("/api/v1/research/joint")
async def research_joint(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {"schema": "research_joint.v1", **ResearchPortal().joint_papers()}


@app.get("/api/v1/research/compare")
async def research_compare(
    a: str = Query(...),
    b: str = Query(...),
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {"schema": "research_compare.v1", **ResearchPortal().compare_papers(a, b)}


@app.get("/api/v1/research/ingredient/{ingredient}/products")
async def research_ingredient_products(ingredient: str, _: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {
        "schema": "research_ingredient_products.v1",
        "ingredient": ingredient,
        "products": ResearchPortal().products_for_ingredient(ingredient),
    }


@app.get("/api/v1/research/gaps")
async def research_gaps(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {
        "schema": "research_gaps.v1",
        "conditions_missing_interventions": ResearchPortal().conditions_missing_interventions(),
    }


@app.get("/api/v1/research/curation")
async def research_curation(_: str = Depends(require_api_key)) -> dict[str, Any]:
    from authoring.portal import ResearchPortal

    return {"schema": "research_curation.v1", **ResearchPortal().curation_dashboard()}


@app.post("/api/recommendations")
async def recommendations_legacy(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    body = await request.json()
    dog_name = body.get("dogName") or body.get("pet_name") or body.get("name")
    observed = list(body.get("observed_conditions") or [])
    if dog_name and not observed:
        observed = observations_for_legacy_analyze(str(dog_name).lower())
    analyze_body = {
        **body,
        "pet_name": dog_name,
        "name": dog_name,
        "breeds": body.get("breeds"),
        "birthday": body.get("birthday"),
        "weight": body.get("weight"),
        "observed_conditions": observed,
    }
    try:
        profile = profile_from_analyze_body(analyze_body)
        result = await agent.generate_reproducible_report(profile)
        return map_legacy_response(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("recommendations failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/v1/evidence/{condition}")
async def evidence_for_condition(
    condition: str,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    key = condition.replace("-", "_")
    evidence = get_evidence_for_condition(agent.repo, key)
    return {"condition": condition, "evidence": evidence}


@app.get("/api/v1/products/{condition}")
async def products_for_condition(
    condition: str,
    weight: float = Query(default=20.0),
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    key = condition.replace("-", "_")
    products = get_products_for_condition(agent.repo, key, weight)
    return {"condition": condition, "products": products}


@app.post("/api/v1/groomer/update")
async def groomer_update(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    body = await request.json()
    pet_id = body.get("pet_id") or body.get("pet_name")
    if not pet_id:
        raise HTTPException(status_code=400, detail="pet_id or pet_name required")
    try:
        session = apply_groomer_update(
            pet_id=str(pet_id),
            observed_conditions=body.get("observed_conditions"),
            notes=body.get("notes"),
            weight=body.get("weight"),
            height=body.get("height"),
            dog_id=body.get("dog_id"),
        )
    except DogStateError as exc:
        return _dog_state_error(exc)
    payload = {
        "pet_id": pet_id,
        "pet_name": body.get("pet_name") or pet_id,
        "observed_conditions": session.get("observed_conditions") or [],
        "notes": session.get("notes"),
        "weight": session.get("weight"),
        "height": session.get("height"),
        "timestamp": session.get("updated_at"),
        "canonical": bool(session.get("canonical")),
        "dog_id": session.get("dog_id"),
    }
    return {"success": True, "payload": payload}


@app.get("/api/v1/groomer/session/{pet_id}")
async def groomer_session(
    pet_id: str,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    return get_groomer_session(pet_id)


@app.post("/api/groomer/submit")
async def groomer_submit(request: Request) -> dict[str, Any]:
    body = await request.json()
    pet_id = body.get("pet_name") or body.get("petName")
    if not pet_id:
        raise HTTPException(status_code=400, detail="pet_name required")
    try:
        session = apply_groomer_update(
            pet_id=str(pet_id),
            observed_conditions=body.get("checklist") or body.get("observed_conditions"),
            notes=body.get("notes"),
            weight=body.get("weight"),
            height=body.get("height"),
            dog_id=body.get("dog_id"),
        )
    except DogStateError as exc:
        return _dog_state_error(exc)
    payload = {
        "pet_id": pet_id,
        "pet_name": pet_id,
        "observed_conditions": session.get("observed_conditions") or [],
        "weight": session.get("weight"),
        "height": session.get("height"),
        "timestamp": session.get("updated_at"),
        "canonical": bool(session.get("canonical")),
        "dog_id": session.get("dog_id"),
    }
    return {"success": True, "payload": payload}


@app.get("/api/breeds")
async def list_breeds(
    search: str | None = Query(default=None),
    q: str | None = Query(default=None),
) -> list[str]:
    query = (search or q or "").lower()
    breeds_df = agent.repo.breeds()
    if breeds_df.empty or "breed" not in breeds_df.columns:
        return []
    names = breeds_df["breed"].dropna().astype(str).tolist()
    if query:
        names = [n for n in names if query in n.lower()]
    return names[:15]


# Product UI lives in waggy-frontend/. Debug/archive assets stay under legacy/.
_legacy_static_root = ROOT / "legacy"
_frontend_root = ROOT / "waggy-frontend"
_static_root = _legacy_static_root


def _static_file_response(relative_path: str, media_type: str) -> FileResponse:
    target = _static_root / relative_path
    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Static asset missing: {relative_path}")
    return FileResponse(
        target,
        media_type=media_type,
        headers={"Cache-Control": "no-cache"},
    )


def _frontend_file_response(relative_path: str, media_type: str) -> FileResponse:
    root = _frontend_root.resolve()
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"Frontend asset missing: {relative_path}") from exc
    if not target.is_file():
        raise HTTPException(status_code=404, detail=f"Frontend asset missing: {relative_path}")
    return FileResponse(
        target,
        media_type=media_type,
        headers={"Cache-Control": "no-cache"},
    )


def _workbench_page() -> FileResponse:
    """Canonical product UI. Role aliases share this file."""
    return _frontend_file_response("index.html", "text/html")


@app.get("/")
async def index_page() -> FileResponse:
    return _workbench_page()


@app.get("/demo")
async def demo_page() -> FileResponse:
    return _workbench_page()


@app.get("/classic")
async def classic_customer_page() -> FileResponse:
    return _workbench_page()


@app.get("/business")
async def business_page() -> FileResponse:
    return _workbench_page()


@app.get("/developer")
async def developer_page() -> FileResponse:
    return _workbench_page()


@app.get("/evidence-report")
async def evidence_report_page() -> FileResponse:
    """Read-only evidence report page. The report itself stays on the Phase N route."""
    return _frontend_file_response("evidence-report.html", "text/html")


@app.get("/favicon.ico")
async def favicon() -> Response:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
        "<rect width='32' height='32' rx='6' fill='#1a237e'/>"
        "<text x='16' y='21' text-anchor='middle' font-size='16' fill='white'>W</text>"
        "</svg>"
    )
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/authoring/explorer")
async def authoring_explorer_page() -> FileResponse:
    page = ROOT / "authoring" / "studio" / "explorer.html"
    if not page.exists():
        raise HTTPException(status_code=404, detail="Run: py -3 -m authoring.pipeline")
    return FileResponse(page)


@app.get("/archive/frontend/{asset_path:path}")
async def archived_frontend_asset(asset_path: str) -> FileResponse:
    """On-disk reference UIs. Not the active product surface."""
    archive_root = (_legacy_static_root / "archive" / "frontend").resolve()
    target = (archive_root / asset_path).resolve()
    try:
        target.relative_to(archive_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Archived frontend asset missing") from exc
    if not target.is_file():
        raise HTTPException(status_code=404, detail="Archived frontend asset missing")
    suffix = target.suffix.lower()
    media = {
        ".html": "text/html",
        ".js": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".md": "text/markdown",
    }.get(suffix, "application/octet-stream")
    return FileResponse(
        target,
        media_type=media,
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/src/{asset_path:path}")
async def serve_frontend_src(asset_path: str) -> FileResponse:
    suffix = Path(asset_path).suffix.lower()
    media = {
        ".js": "application/javascript",
        ".css": "text/css",
        ".svg": "image/svg+xml",
        ".json": "application/json",
        ".md": "text/plain",
        ".map": "application/json",
    }.get(suffix, "application/octet-stream")
    return _frontend_file_response(f"src/{asset_path}", media)


@app.get("/ppie-validation-console.js")
async def serve_ppie_validation_console_js() -> FileResponse:
    return _static_file_response("ppie-validation-console.js", "application/javascript")


@app.get("/ppie-validation-console.css")
async def serve_ppie_validation_console_css() -> FileResponse:
    return _static_file_response("ppie-validation-console.css", "text/css")


@app.get("/workbench.js")
async def serve_workbench_js() -> FileResponse:
    return _frontend_file_response("src/workbench.js", "application/javascript")


@app.get("/workbench.css")
async def serve_workbench_css() -> FileResponse:
    return _frontend_file_response("src/styles/workbench.css", "text/css")


@app.get("/debug/calculation")
async def debug_calculation_page(request: Request):
    """Internal Validation Console HTML shell (developer route)."""
    _require_surface_access(request, env_var="WAGTOPIA_DEVELOPER_ACCESS_KEY", surface="developer")
    response = _static_file_response("debug/calculation.html", "text/html")
    _apply_surface_cookie(response=response, request=request, env_var="WAGTOPIA_DEVELOPER_ACCESS_KEY")
    return response


@app.get("/theme.css")
async def serve_theme() -> FileResponse:
    return _frontend_file_response("src/styles/theme.css", "text/css")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
