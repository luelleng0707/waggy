"""Deterministic fake provider for tests. Not a second recommendation engine."""

from __future__ import annotations

from app.ai.feedback import is_ambiguous_preference
from app.ai.models import ConversationMessage, ExplanationContext, ModelProviderResult
from app.ai.providers.base import ModelProvider
from app.ai.version import WAGGY_AI_RESPONSE_SCHEMA


class FakeProvider(ModelProvider):
    name = "fake"
    model = "fake-explanation-1"

    def __init__(self, canned: dict | None = None) -> None:
        self.canned = canned

    def generate_response(
        self,
        *,
        policy: str,
        context: ExplanationContext,
        conversation: list[ConversationMessage],
        user_message: str,
    ) -> ModelProviderResult:
        del policy, conversation
        if self.canned is not None:
            return ModelProviderResult(
                text=str(self.canned.get("message") or ""),
                structured_output=self.canned,
                provider=self.name,
                model=self.model,
            )
        packages = context.packages or []
        first = packages[0] if packages else {}
        products = first.get("products") or []
        names = [str(item.get("name") or item.get("product_id") or "product") for item in products if isinstance(item, dict)]
        bundle = first.get("bundle_id") or context.selected_bundle_id or "the current package"
        evidence_status = context.evidence_status
        message = (
            f"Waggy composed {bundle} from the deterministic optimizer. "
            f"Products in the supplied result: {', '.join(names) or 'none listed'}. "
            f"Evidence status in this context: {evidence_status}."
        )
        feedback: list[dict] = []
        clarification = False
        question = None
        recompute = False
        constraints = None
        lowered = user_message.lower()
        recalc = context.recalculation if isinstance(context.recalculation, dict) else None
        if recalc and any(token in lowered for token in ("why", "change", "changed", "different")):
            facts = [str(item) for item in (recalc.get("summary_facts") or []) if item]
            if facts:
                message = " ".join(facts)
                structured = {
                    "schema": WAGGY_AI_RESPONSE_SCHEMA,
                    "message": message,
                    "response_type": "explanation",
                    "evidence_refs": [
                        {"paper_name": row.get("paper_name"), "paper_link": row.get("paper_link"), "status": row.get("status")}
                        for row in context.evidence[:5]
                    ],
                    "feedback": [],
                    "clarification_needed": False,
                    "clarification_question": None,
                    "requested_recomputation": False,
                    "proposed_constraints": None,
                }
                return ModelProviderResult(
                    text=message,
                    structured_output=structured,
                    provider=self.name,
                    model=self.model,
                )
        if "ignore waggy" in lowered or "replace product" in lowered or "99%" in lowered:
            message += " I cannot override Waggy's package, nutrients, or warehouse evidence."
        elif is_ambiguous_preference(user_message):
            clarification = True
            question = "Would you like me to ask Waggy to recompute with a lower monthly budget?"
            feedback.append(
                {
                    "schema": "waggy_feedback_candidate.v1",
                    "type": "USER_PREFERENCE",
                    "category": "budget",
                    "value": "budget_sensitive",
                    "confidence": "ambiguous",
                    "source": "inferred",
                }
            )
        elif "under" in lowered and any(ch.isdigit() for ch in user_message):
            digits = "".join(ch if ch.isdigit() or ch == "." else " " for ch in user_message).split()
            budget = float(digits[0]) if digits else None
            recompute = budget is not None
            constraints = {"monthly_budget": budget} if budget is not None else None
            feedback.append(
                {
                    "schema": "waggy_feedback_candidate.v1",
                    "type": "RECOMPUTATION_REQUEST",
                    "category": "budget",
                    "value": str(budget),
                    "confidence": "explicit",
                    "source": "explicit_user_statement",
                }
            )
            message += " I can ask Waggy to recompute with that budget. I will not remove products myself."
        elif "chicken" in lowered:
            recompute = True
            constraints = {"ingredient_exclusion": ["chicken"]}
            feedback.append(
                {
                    "schema": "waggy_feedback_candidate.v1",
                    "type": "USER_PREFERENCE",
                    "category": "ingredient_exclusion",
                    "value": "chicken",
                    "confidence": "explicit",
                    "source": "explicit_user_statement",
                }
            )
            message += " Chicken exclusion is a preference. Waggy Engine must recompute; I will not edit the package."
        structured = {
            "schema": WAGGY_AI_RESPONSE_SCHEMA,
            "message": message,
            "response_type": "clarification" if clarification else "explanation",
            "evidence_refs": [
                {"paper_name": row.get("paper_name"), "paper_link": row.get("paper_link"), "status": row.get("status")}
                for row in context.evidence[:5]
            ],
            "feedback": feedback,
            "clarification_needed": clarification,
            "clarification_question": question,
            "requested_recomputation": recompute,
            "proposed_constraints": constraints,
        }
        return ModelProviderResult(
            text=message,
            structured_output=structured,
            provider=self.name,
            model=self.model,
        )
