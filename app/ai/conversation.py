"""Conversation store. Conversation is not scientific truth."""

from __future__ import annotations

from app.ai.models import ConversationMessage, ConversationRecord
from app.state.store import append_messages, create_conversation, get_conversation, reset_conversations

__all__ = [
    "ConversationMessage",
    "ConversationRecord",
    "append_messages",
    "create_conversation",
    "get_conversation",
    "reset_conversations",
]
