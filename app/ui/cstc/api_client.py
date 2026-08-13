"""Thin HTTP client for existing Wagtopia API endpoints."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .errors import ApiResponseError, TransportError


class WagtopiaApiClient:
    """API transport wrapper. No scientific logic."""

    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health", require_key=False)

    def breeds(self, query: str | None = None) -> list[str]:
        if query:
            encoded = urllib.parse.quote(query)
            return list(self._request("GET", f"/api/breeds?search={encoded}", require_key=False))
        return list(self._request("GET", "/api/breeds", require_key=False))

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/analyze", body=payload)

    def clinical_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/clinical-report", body=payload)

    def assess(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/ppie/assess", body=payload)

    def trace(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/api/v1/ppie/trace?debug=1", body=payload)

    def store(self) -> dict[str, Any]:
        return self._request("GET", "/api/v1/store")

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        require_key: bool = True,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json"}
        if require_key:
            headers["x-api-key"] = self.api_key
        data: bytes | None = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url=url, method=method, headers=headers, data=data)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                raw = exc.read().decode("utf-8")
                parsed = json.loads(raw) if raw else {}
                detail = str(parsed.get("detail") or raw)
            except Exception:  # noqa: BLE001
                detail = str(exc)
            raise ApiResponseError(exc.code, detail) from exc
        except urllib.error.URLError as exc:
            raise TransportError(f"Failed to reach {url}: {exc}") from exc
