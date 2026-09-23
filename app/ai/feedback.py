"""Validate untrusted model feedback. Never apply it as a warehouse write."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.ai.models import (
    ALLOWED_RECOMPUTE_KEYS,
    FeedbackCandidate,
    ProposedConstraints,
)

_DURABLE_CONFIDENCE = {"explicit"}
_DURABLE_SOURCE = {"explicit_user_statement"}


def parse_feedback(raw: Any) -> list[FeedbackCandidate]:
    if not isinstance(raw, list):
        return []
    accepted: list[FeedbackCandidate] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            candidate = FeedbackCandidate.model_validate(item)
        except ValidationError:
            continue
        durable = (
            candidate.confidence in _DURABLE_CONFIDENCE
            and candidate.source in _DURABLE_SOURCE
            and candidate.type in {"USER_PREFERENCE", "RECOMPUTATION_REQUEST"}
        )
        accepted.append(candidate.model_copy(update={"durable": durable}))
    return accepted


def parse_constraints(raw: Any) -> ProposedConstraints | None:
    if not isinstance(raw, dict) or not raw:
        return None
    filtered = {key: value for key, value in raw.items() if key in ALLOWED_RECOMPUTE_KEYS}
    if not filtered:
        return None
    try:
        return ProposedConstraints.model_validate(filtered)
    except ValidationError:
        return None


def is_ambiguous_preference(message: str) -> bool:
    text = message.strip().lower()
    if not text:
        return False
    vague = ("expensive", "too much", "not sure", "maybe", "kind of")
    explicit = ("keep it under", "don't want", "do not want", "exclude", "budget is", "no chicken")
    if any(token in text for token in explicit):
        return False
    return any(token in text for token in vague)
