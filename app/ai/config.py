"""Provider registry. Domain code depends on ModelProvider, not Gemini."""

from __future__ import annotations

import os

from app.ai.providers.base import ModelProvider
from app.ai.providers.fake import FakeProvider
from app.ai.providers.gemini import GeminiProvider


def configured_provider_name() -> str:
    return (os.getenv("WAGGY_AI_PROVIDER") or "fake").strip().lower()


def provider_status() -> dict[str, object]:
    name = configured_provider_name()
    available = True
    if name == "gemini":
        available = bool((os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip())
    return {
        "provider": name,
        "available": available,
        "core_analysis_requires_ai": False,
    }


def get_provider(name: str | None = None) -> ModelProvider:
    chosen = (name or configured_provider_name()).strip().lower()
    if chosen in {"fake", "test"}:
        return FakeProvider()
    if chosen == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown AI provider: {chosen}")
