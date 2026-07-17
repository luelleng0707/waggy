"""FastAPI entrypoint — Python is the sole production PPIE runtime."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.agent.version import ALGORITHM_VERSION
from app.agent.engine import PPIEWellnessAgent
from app.agent.state import DogProfileInput
from app.api.evidence import get_evidence_for_condition, get_products_for_condition
from app.api.payload_adapter import map_legacy_response, profile_from_analyze_body

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ppie.api")

ROOT = Path(__file__).resolve().parents[2]
_raw_data = os.getenv("PPIE_DATA_DIR", "data")
_data_path = Path(_raw_data)
# Resolve relative data dirs against repo root (not process cwd) so clean
# clones / service managers still find CSVs.
if not _data_path.is_absolute():
    _data_path = ROOT / _data_path
DATA_DIR = str(_data_path)
VALID_KEYS = {
    k.strip()
    for k in os.getenv("API_KEYS", "wagtopia-demo-key,ppie-dev-key").split(",")
    if k.strip()
}

app = FastAPI(title="Wagtopia PPIE Wellness Agent API", version=ALGORITHM_VERSION)
agent = PPIEWellnessAgent(data_dir=DATA_DIR)
_groomer_sessions: dict[str, dict[str, Any]] = {}

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
    if not x_api_key or x_api_key not in VALID_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing x-api-key")
    return x_api_key


@app.get("/health")
async def health() -> dict[str, Any]:
    csv_ok = True
    csv_detail = "ok"
    try:
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


@app.post("/api/v1/analyze")
async def analyze_v1(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    body = await request.json()
    pet_key = str(body.get("pet_name") or body.get("petName") or "").lower()
    session = _groomer_sessions.get(pet_key) if pet_key else None
    observed = list(body.get("observed_conditions") or [])
    if session:
        observed = list({*observed, *(session.get("observed_conditions") or [])})
    body = {**body, "observed_conditions": observed}
    try:
        profile = profile_from_analyze_body(body)
        return await agent.generate_reproducible_report(profile)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("analyze failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/recommendations")
async def recommendations_legacy(
    request: Request,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    body = await request.json()
    dog_name = body.get("dogName") or body.get("pet_name") or body.get("name")
    observed = list(body.get("observed_conditions") or [])
    if dog_name and not observed:
        session = _groomer_sessions.get(str(dog_name).lower())
        observed = list((session or {}).get("observed_conditions") or [])
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
    key = str(pet_id).lower()
    session = _groomer_sessions.get(key) or {"observed_conditions": []}
    session["observed_conditions"] = list({
        *(session.get("observed_conditions") or []),
        *(body.get("observed_conditions") or []),
    })
    session["notes"] = body.get("notes")
    session["weight"] = body.get("weight")
    session["height"] = body.get("height")
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    _groomer_sessions[key] = session
    payload = {
        "pet_id": pet_id,
        "pet_name": body.get("pet_name") or pet_id,
        "observed_conditions": session["observed_conditions"],
        "notes": body.get("notes"),
        "weight": body.get("weight"),
        "height": body.get("height"),
        "timestamp": session["updated_at"],
    }
    return {"success": True, "payload": payload}


@app.get("/api/v1/groomer/session/{pet_id}")
async def groomer_session(
    pet_id: str,
    _: str = Depends(require_api_key),
) -> dict[str, Any]:
    session = _groomer_sessions.get(pet_id.lower())
    return session or {"observed_conditions": []}


@app.post("/api/groomer/submit")
async def groomer_submit(request: Request) -> dict[str, Any]:
    body = await request.json()
    pet_id = body.get("pet_name") or body.get("petName")
    if not pet_id:
        raise HTTPException(status_code=400, detail="pet_name required")
    key = str(pet_id).lower()
    session = _groomer_sessions.get(key) or {"observed_conditions": []}
    session["observed_conditions"] = list({
        *(session.get("observed_conditions") or []),
        *(body.get("checklist") or []),
    })
    session["weight"] = body.get("weight")
    session["height"] = body.get("height")
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    _groomer_sessions[key] = session
    payload = {
        "pet_id": pet_id,
        "pet_name": pet_id,
        "observed_conditions": session["observed_conditions"],
        "weight": body.get("weight"),
        "height": body.get("height"),
        "timestamp": session["updated_at"],
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


# Static demo UI (formerly served by Node express.static)
_static_root = ROOT
if (_static_root / "index.html").exists():

    @app.get("/")
    async def index_page() -> FileResponse:
        return FileResponse(_static_root / "index.html")

    @app.get("/app.js")
    async def serve_app_js() -> FileResponse:
        return FileResponse(_static_root / "app.js", media_type="application/javascript")

    @app.get("/styles.css")
    async def serve_styles() -> FileResponse:
        return FileResponse(_static_root / "styles.css", media_type="text/css")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
