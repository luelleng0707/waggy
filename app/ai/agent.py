"""Explanation orchestration. Does not call the scientific engine."""

from __future__ import annotations

from pydantic import ValidationError

from app.ai.context import build_explanation_context, canonical_signature
from app.ai.conversation import append_messages, create_conversation, get_conversation
from app.ai.feedback import parse_constraints, parse_feedback
from app.ai.models import (
    ConversationMessage,
    EvidenceRef,
    ExplainRequest,
    WaggyAIResponse,
)
from app.ai.policy import policy_text
from app.ai.providers.base import ModelProvider, ProviderError
from app.ai.version import WAGGY_AI_POLICY_VERSION, WAGGY_AI_RESPONSE_SCHEMA


class AnalysisMismatchError(ValueError):
    """Conversation/request is bound to a different analysis_signature."""


def _allowed_evidence(context_evidence: list[dict]) -> set[tuple[str | None, str | None]]:
    return {
        (row.get("paper_name"), row.get("paper_link"))
        for row in context_evidence
        if isinstance(row, dict)
    }


def _filter_evidence_refs(raw: list, allowed: set[tuple[str | None, str | None]]) -> list[EvidenceRef]:
    out: list[EvidenceRef] = []
    for item in raw:
        try:
            ref = EvidenceRef.model_validate(item)
        except ValidationError:
            continue
        key = (ref.paper_name, ref.paper_link)
        if key in allowed or (ref.paper_name, None) in allowed:
            out.append(ref)
    return out


class WaggyExplanationAgent:
    def __init__(self, provider: ModelProvider) -> None:
        self.provider = provider

    def explain(self, request: ExplainRequest) -> WaggyAIResponse:
        signature = request.analysis_signature
        payload = request.canonical
        if isinstance(payload.get("canonical"), dict) and "scientific_analysis" not in payload:
            payload = payload["canonical"]
        canonical_sig = canonical_signature(payload, signature)
        if canonical_sig and canonical_sig != signature:
            raise AnalysisMismatchError("canonical analysis_id does not match analysis_signature")
        context = build_explanation_context(
            payload,
            analysis_signature=signature,
            role=request.role,
            bundle_id=request.bundle_id,
            previous_canonical=(
                request.previous_canonical.get("canonical")
                if isinstance(request.previous_canonical, dict)
                and "scientific_analysis" not in request.previous_canonical
                and isinstance(request.previous_canonical.get("canonical"), dict)
                else request.previous_canonical
            ),
            recalculation=request.recalculation,
        )
        conversation = None
        if request.conversation_id:
            conversation = get_conversation(request.conversation_id)
            if conversation is None:
                conversation = create_conversation(
                    analysis_signature=signature,
                    dog_id=request.dog_id,
                    selected_bundle_id=request.bundle_id,
                    conversation_id=request.conversation_id,
                )
            elif conversation.analysis_signature != signature:
                raise AnalysisMismatchError("conversation is bound to a different analysis_signature")
        else:
            conversation = create_conversation(
                analysis_signature=signature,
                dog_id=request.dog_id,
                selected_bundle_id=request.bundle_id,
            )
        history = list(conversation.messages or [])
        if request.messages:
            history = list(request.messages)
        try:
            result = self.provider.generate_response(
                policy=policy_text(),
                context=context,
                conversation=history,
                user_message=request.user_message,
            )
        except ProviderError as exc:
            response = WaggyAIResponse(
                message=(
                    "AI explanation is temporarily unavailable. You can still review "
                    "Waggy's package rationale and scientific evidence."
                ),
                response_type="unavailable",
                conversation_id=conversation.conversation_id,
                analysis_signature=signature,
                ai_policy_version=WAGGY_AI_POLICY_VERSION,
                provider=self.provider.name,
                model=getattr(self.provider, "model", None),
                unavailable_reason=str(exc),
                recalculation=context.recalculation,
            )
            return response

        structured = result.structured_output if isinstance(result.structured_output, dict) else {}
        try:
            parsed = WaggyAIResponse.model_validate(
                {
                    "schema": structured.get("schema") or WAGGY_AI_RESPONSE_SCHEMA,
                    "message": structured.get("message") or result.text or "",
                    "response_type": structured.get("response_type") or "explanation",
                    "clarification_needed": bool(structured.get("clarification_needed")),
                    "clarification_question": structured.get("clarification_question"),
                    "requested_recomputation": bool(structured.get("requested_recomputation")),
                }
            )
        except ValidationError:
            parsed = WaggyAIResponse(
                message=result.text or "The model returned an unusable explanation.",
                response_type="error",
            )
        parsed.feedback = parse_feedback(structured.get("feedback"))
        parsed.proposed_constraints = parse_constraints(structured.get("proposed_constraints"))
        if parsed.requested_recomputation and parsed.proposed_constraints is None:
            parsed.requested_recomputation = False
        parsed.evidence_refs = _filter_evidence_refs(
            structured.get("evidence_refs") or [],
            _allowed_evidence(context.evidence),
        )
        if any(item.confidence == "ambiguous" for item in parsed.feedback):
            parsed.clarification_needed = True
        parsed.conversation_id = conversation.conversation_id
        parsed.analysis_signature = signature
        parsed.ai_policy_version = WAGGY_AI_POLICY_VERSION
        parsed.provider = result.provider
        parsed.model = result.model
        parsed.recalculation = context.recalculation
        append_messages(
            conversation.conversation_id,
            [
                ConversationMessage(role="user", content=request.user_message),
                ConversationMessage(role="assistant", content=parsed.message),
            ],
        )
        return parsed


def explain_with_provider(provider: ModelProvider, request: ExplainRequest) -> WaggyAIResponse:
    return WaggyExplanationAgent(provider).explain(request)
