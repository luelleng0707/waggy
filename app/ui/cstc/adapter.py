"""Presentation adapter: UI models <-> existing Wagtopia API."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .api_client import WagtopiaApiClient
from .models import AnalysisPresentation, AnalyzeDogRequest
from .view_models import build_presentation


class WagtopiaPresentationAdapter:
    """Translation-only boundary for CSTC shell integration."""

    def __init__(self, client: WagtopiaApiClient):
        self.client = client
        self._analysis_count = 0
        self._last_result: AnalysisPresentation | None = None

    @property
    def analysis_count(self) -> int:
        return self._analysis_count

    @property
    def last_result(self) -> AnalysisPresentation | None:
        return self._last_result

    def health(self) -> dict[str, Any]:
        return self.client.health()

    def list_breeds(self, query: str | None = None) -> list[str]:
        return self.client.breeds(query)

    def run_analysis(self, request: AnalyzeDogRequest) -> AnalysisPresentation:
        payload = self.to_api_payload(request)
        analyze = self.client.analyze(payload)
        assessment = self.client.assess(payload)
        presentation = build_presentation(analyze, assessment)
        self._analysis_count += 1
        self._last_result = presentation
        return presentation

    def fetch_trace(self, request: AnalyzeDogRequest) -> dict[str, Any]:
        """Optional debug trace. May fail when debug mode is disabled server-side."""
        return self.client.trace(self.to_api_payload(request))

    def to_api_payload(self, request: AnalyzeDogRequest) -> dict[str, Any]:
        """Map UI request into existing API request shape."""
        payload = asdict(request)
        breeds = [request.primary_breed]
        if request.secondary_breed:
            breeds.append(request.secondary_breed)
        payload.update(
            {
                "pet_name": request.name,
                "name": request.name,
                "breeds": breeds,
                "weight": request.weight_kg,
                "height": request.height_cm,
                "sex": request.sex,
                "gender": request.sex,
                "environment": request.current_environment,
                "activity": request.activity_level,
                "observed_conditions": list(request.observed_conditions),
            }
        )
        return payload
