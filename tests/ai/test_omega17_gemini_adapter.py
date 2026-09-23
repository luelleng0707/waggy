"""Gemini adapter tests. Core Waggy tests must not require a live Gemini key."""

from __future__ import annotations

import json
from urllib.error import URLError

import pytest

from app.ai.context import build_explanation_context
from app.ai.providers.base import ProviderError
from app.ai.providers.gemini import GeminiProvider


def _context():
    return build_explanation_context(
        {
            "analysis_id": "sig",
            "input": {"dog_profile": {"name": "Dolly"}},
            "scientific_analysis": {"findings": [], "nutrient_targets": [], "evidence": []},
            "product_matching": {"recommendations": []},
            "package_optimization": {"package_options": {}, "search": {"llm_used": False}},
            "system": {},
        },
        analysis_signature="sig",
    )


def test_gemini_requires_server_side_key():
    provider = GeminiProvider(api_key="", model="gemini-2.0-flash")
    with pytest.raises(ProviderError):
        provider.generate_response(
            policy="policy",
            context=_context(),
            conversation=[],
            user_message="Why?",
        )


def test_gemini_parses_json_candidate(monkeypatch: pytest.MonkeyPatch):
    payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "schema": "waggy_ai_response.v1",
                                    "message": "Because Waggy selected these products.",
                                    "response_type": "explanation",
                                    "evidence_refs": [],
                                    "feedback": [],
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    monkeypatch.setattr("app.ai.providers.gemini.urllib.request.urlopen", lambda *args, **kwargs: _Resp())
    result = GeminiProvider(api_key="server-only", model="gemini-2.0-flash").generate_response(
        policy="policy",
        context=_context(),
        conversation=[],
        user_message="Why?",
    )
    assert result.ok is True
    assert result.structured_output["message"].startswith("Because Waggy")
    assert result.provider == "gemini"


def test_gemini_transport_failure(monkeypatch: pytest.MonkeyPatch):
    def _boom(*_args, **_kwargs):
        raise URLError("down")

    monkeypatch.setattr("app.ai.providers.gemini.urllib.request.urlopen", _boom)
    with pytest.raises(ProviderError):
        GeminiProvider(api_key="server-only", model="x").generate_response(
            policy="p",
            context=_context(),
            conversation=[],
            user_message="Why?",
        )
