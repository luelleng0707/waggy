"""Minimal PPIE HTTP client stub (auto-generated)."""
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
