"""ModelProvider interface. Domain logic must not import a specific SDK."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.models import ConversationMessage, ExplanationContext, ModelProviderResult


class ProviderError(Exception):
    """Transport/config failure. Canonical Waggy analysis is unaffected."""


class ModelProvider(ABC):
    name: str = "base"
    model: str = "unspecified"

    @abstractmethod
    def generate_response(
        self,
        *,
        policy: str,
        context: ExplanationContext,
        conversation: list[ConversationMessage],
        user_message: str,
    ) -> ModelProviderResult:
        raise NotImplementedError
