"""Prototype Gemini adapter. Not Waggy architecture and not a scientific engine."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from app.ai.models import ConversationMessage, ExplanationContext, ModelProviderResult
from app.ai.providers.base import ModelProvider, ProviderError

GEMINI_ENDPOINT_TEMPLATE = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


class GeminiProvider(ModelProvider):
    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = (api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
        self.model = (model or os.getenv("WAGGY_AI_MODEL") or "gemini-2.0-flash").strip()
        self.timeout_seconds = float(timeout_seconds or os.getenv("WAGGY_AI_TIMEOUT_SECONDS") or "20")

    def generate_response(
        self,
        *,
        policy: str,
        context: ExplanationContext,
        conversation: list[ConversationMessage],
        user_message: str,
    ) -> ModelProviderResult:
        if not self.api_key:
            raise ProviderError("Gemini API key is not configured on the server.")
        payload = {
            "systemInstruction": {"parts": [{"text": policy}]},
            "contents": _contents(conversation, context, user_message),
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        url = GEMINI_ENDPOINT_TEMPLATE.format(model=self.model) + "?key=" + self.api_key
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"Gemini HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError("Gemini unavailable") from exc
        except TimeoutError as exc:
            raise ProviderError("Gemini timeout") from exc
        text = _extract_text(body)
        structured = None
        try:
            structured = json.loads(text) if text else None
        except json.JSONDecodeError:
            structured = None
        return ModelProviderResult(
            text=text or "",
            structured_output=structured if isinstance(structured, dict) else None,
            provider=self.name,
            model=self.model,
        )


def _contents(
    conversation: list[ConversationMessage],
    context: ExplanationContext,
    user_message: str,
) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    for item in conversation:
        role = "user" if item.role == "user" else "model"
        turns.append({"role": role, "parts": [{"text": item.content}]})
    blob = json.dumps(
        {
            "explanation_context": context.model_dump(by_alias=True),
            "user_message": user_message,
        },
        separators=(",", ":"),
        default=str,
    )
    turns.append({"role": "user", "parts": [{"text": blob}]})
    return turns


def _extract_text(body: dict[str, Any]) -> str:
    candidates = body.get("candidates") or []
    if not candidates:
        return ""
    content = (candidates[0] or {}).get("content") or {}
    parts = content.get("parts") or []
    texts = [str(part.get("text") or "") for part in parts if isinstance(part, dict)]
    return "".join(texts)
