"""ΩM Developer SDK — OpenAPI / JSON Schema / TS stubs from live FastAPI app."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "ppie_platform" / "sdk" / "generated"


def generate_sdks() -> dict[str, str]:
    from app.api.main import app

    OUT.mkdir(parents=True, exist_ok=True)
    openapi = app.openapi()
    openapi_path = OUT / "openapi.json"
    openapi_path.write_text(json.dumps(openapi, indent=2), encoding="utf-8")

    # JSON Schema bundle of components
    schemas = openapi.get("components", {}).get("schemas", {})
    schema_path = OUT / "schemas.json"
    schema_path.write_text(json.dumps(schemas, indent=2), encoding="utf-8")

    # Minimal TypeScript types for DogProfile-ish
    ts = OUT / "ppie.d.ts"
    ts.write_text(
        """/** Auto-generated PPIE SDK stubs — regenerate via platform.sdk.generate */
export interface DogProfileInput {
  name: string;
  primary_breed: string;
  secondary_breed?: string | null;
  breed_split_pct?: number;
  age_years: number;
  weight_kg: number;
  current_environment: string;
  activity_level?: string;
  sex?: string | null;
  observed_conditions?: string[];
}

export type ClinicalReportResponse = {
  analyze: Record<string, unknown>;
  assessment: Record<string, unknown>;
  report: Record<string, unknown>;
  reportModels: Record<string, unknown>;
  clinicalReport: Record<string, unknown>;
  trace?: Record<string, unknown>;
};
""",
        encoding="utf-8",
    )

    # Python client stub
    py = OUT / "client.py"
    py.write_text(
        '''"""Minimal PPIE HTTP client stub (auto-generated)."""
from __future__ import annotations
import httpx

class PpieClient:
    def __init__(self, base_url: str, api_key: str = "wagtopia-demo-key"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def clinical_report(self, body: dict) -> dict:
        r = httpx.post(
            f"{self.base_url}/api/v1/clinical-report",
            json=body,
            headers={"x-api-key": self.api_key},
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()

    def platform_status(self) -> dict:
        r = httpx.get(
            f"{self.base_url}/api/v1/platform/status",
            headers={"x-api-key": self.api_key},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()
''',
        encoding="utf-8",
    )

    return {
        "openapi": str(openapi_path),
        "schemas": str(schema_path),
        "typescript": str(ts),
        "python": str(py),
    }
