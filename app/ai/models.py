"""Provider-neutral AI contracts. Model output is untrusted input."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.ai.version import (
    WAGGY_AI_RESPONSE_SCHEMA,
    WAGGY_CONVERSATION_SCHEMA,
    WAGGY_EXPLANATION_CONTEXT_SCHEMA,
    WAGGY_FEEDBACK_SCHEMA,
    WAGGY_PROFILE_EVENT_SCHEMA,
)

FeedbackType = Literal[
    "USER_PREFERENCE",
    "USER_REPORTED_OBSERVATION",
    "RECOMPUTATION_REQUEST",
]
FeedbackConfidence = Literal["explicit", "inferred", "ambiguous"]
FeedbackSource = Literal["explicit_user_statement", "inferred", "model_unspecified"]
EventSource = Literal["SCIENTIFIC", "GROOMER", "USER", "SYSTEM", "VETERINARIAN"]
EventKind = Literal[
    "observation",
    "preference",
    "weight_update",
    "analysis_snapshot",
    "profile_update",
    "package_interaction",
    "system",
]
EventTypeName = Literal[
    "PROFILE_UPDATE",
    "GROOMER_OBSERVATION",
    "VETERINARIAN_OBSERVATION",
    "USER_STATEMENT",
    "USER_PREFERENCE",
    "PACKAGE_INTERACTION",
    "ANALYSIS_RUN",
    "SYSTEM_EVENT",
]
ResponseType = Literal["explanation", "clarification", "unavailable", "error"]
RoleName = Literal["customer", "groomer", "business", "developer"]

ALLOWED_RECOMPUTE_KEYS = frozenset({"monthly_budget", "ingredient_exclusion", "preference_notes"})


class FeedbackCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_FEEDBACK_SCHEMA, alias="schema")
    type: FeedbackType
    category: str
    value: str
    confidence: FeedbackConfidence
    source: FeedbackSource
    durable: bool = False


class ProposedConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    monthly_budget: float | None = None
    ingredient_exclusion: list[str] | None = None
    preference_notes: str | None = None


class EvidenceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paper_name: str | None = None
    paper_link: str | None = None
    status: str | None = None


class WaggyAIResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_AI_RESPONSE_SCHEMA, alias="schema")
    message: str
    response_type: ResponseType = "explanation"
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    feedback: list[FeedbackCandidate] = Field(default_factory=list)
    clarification_needed: bool = False
    clarification_question: str | None = None
    requested_recomputation: bool = False
    proposed_constraints: ProposedConstraints | None = None
    conversation_id: str | None = None
    analysis_signature: str | None = None
    ai_policy_version: str | None = None
    provider: str | None = None
    model: str | None = None
    unavailable_reason: str | None = None
    recalculation: dict[str, Any] | None = None


class ExplanationContext(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_EXPLANATION_CONTEXT_SCHEMA, alias="schema")
    analysis_signature: str
    role: RoleName = "customer"
    dog: dict[str, Any] = Field(default_factory=dict)
    findings: list[dict[str, Any]] = Field(default_factory=list)
    nutrient_targets: list[dict[str, Any]] = Field(default_factory=list)
    products: list[dict[str, Any]] = Field(default_factory=list)
    packages: list[dict[str, Any]] = Field(default_factory=list)
    selected_bundle_id: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    evidence_status: str = "NOT_AVAILABLE"
    optimizer: dict[str, Any] = Field(default_factory=dict)
    uncertainty: dict[str, Any] = Field(default_factory=dict)
    package_difference: dict[str, Any] | None = None
    recalculation: dict[str, Any] | None = None


class ConversationMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str


class ConversationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_CONVERSATION_SCHEMA, alias="schema")
    conversation_id: str
    dog_id: str | None = None
    analysis_signature: str
    selected_bundle_id: str | None = None
    messages: list[ConversationMessage] = Field(default_factory=list)
    created_at: str
    updated_at: str
    policy_version: str | None = None
    provider: str | None = None
    model: str | None = None


class ProfileEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: str = Field(default=WAGGY_PROFILE_EVENT_SCHEMA, alias="schema")
    event_id: str
    dog_id: str
    source: EventSource
    kind: EventKind
    value: str
    timestamp: str
    session_id: str | None = None
    confirmed: bool = False
    notes: str | None = None
    event_type: EventTypeName = "SYSTEM_EVENT"
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "recorded"
    created_at: str | None = None
    correlation_id: str | None = None
    observed_at: str | None = Field(
        default=None,
        description="When the fact was observed. None means observation time is unknown. Not timestamp.",
    )
    recorded_at: str | None = Field(
        default=None,
        description="When Waggy stored the event. Distinct from observed_at and from legacy timestamp.",
    )


class ModelProviderResult(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str
    structured_output: dict[str, Any] | None = None
    provider: str
    model: str
    ok: bool = True
    error: str | None = None


class ExplainRequest(BaseModel):
    """HTTP body for POST /api/v1/ai/explain. Does not trigger the engine."""

    model_config = ConfigDict(extra="forbid")

    analysis_signature: str
    canonical: dict[str, Any]
    user_message: str
    conversation_id: str | None = None
    messages: list[ConversationMessage] = Field(default_factory=list)
    role: RoleName = "customer"
    bundle_id: str | None = None
    dog_id: str | None = None
    previous_canonical: dict[str, Any] | None = None
    recalculation: dict[str, Any] | None = None


class ProfileEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dog_id: str
    source: EventSource
    kind: EventKind
    value: str
    session_id: str | None = None
    confirmed: bool = False
    notes: str | None = None
