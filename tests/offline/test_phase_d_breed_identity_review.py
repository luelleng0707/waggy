"""Phase D review-structure tests. Do not assert speculative identity meaning."""

from __future__ import annotations

import hashlib
from pathlib import Path

from app.agent.version import ALGORITHM_VERSION
from app.normalization.identity import breed_identity_provider
from app.normalization.version import MAPPING_CONFIG_VERSION
from app.offline.breed_identity_compare import SAME, run_comparison
from app.offline.breed_identity_review import (
    ADD_APPROVED_KNOWLEDGE,
    DEFAULT_REVIEW_PATH,
    EXISTING_RUNTIME_BEHAVIOR,
    NO_EXPLICIT_CONTRACT,
    PROPOSED_ACTION_NONE,
    REQUIRES_HUMAN_DECISION,
    build_review,
    render_review_document,
)

ROOT = Path(__file__).resolve().parents[2]
ALIASES_CSV = ROOT / "warehouse" / "mapping" / "breed_aliases.csv"
BREEDS_CSV = ROOT / "warehouse" / "biology" / "breeds.csv"
REVIEW_SOURCE = ROOT / "app" / "offline" / "breed_identity_review.py"


def test_every_phase_c_disagreement_appears_in_review():
    comparison = run_comparison()
    disagreements = [row for row in comparison.rows if row.classification != SAME]
    review = build_review(report=comparison)
    assert len(review.cases) == 21
    assert len(review.cases) == len(disagreements)
    assert [case.input for case in review.cases] == [row.input for row in disagreements]
    assert {case.case_id for case in review.cases} == {f"D-{i:02d}" for i in range(1, 22)}


def test_unresolved_decisions_default_to_requires_human_decision():
    review = build_review()
    assert all(case.decision_status == REQUIRES_HUMAN_DECISION for case in review.cases)
    assert all(case.proposed_action == PROPOSED_ACTION_NONE for case in review.cases)
    text = render_review_document(review)
    assert "approved by Cursor" not in text.lower()
    assert "product-approved" not in text
    assert "Ω12 is correct" not in text
    assert "Golden is wrong" not in text
    assert "ask the customer" not in text.lower()
    assert "ask customer to choose" not in text.lower()
    assert ADD_APPROVED_KNOWLEDGE not in [case.decision_status for case in review.cases]


def test_review_records_preserve_legacy_and_omega12_results():
    comparison = run_comparison()
    review = build_review(report=comparison)
    by_input = {row.input: row for row in comparison.rows if row.classification != SAME}
    for case in review.cases:
        row = by_input[case.input]
        if row.legacy.selected:
            assert row.legacy.canonical_id in case.legacy_result
            assert row.legacy.canonical_name in case.legacy_result
        else:
            assert case.legacy_result == "selected=no"
        assert case.omega12_status == row.omega12.status
        assert case.omega12_rule == row.omega12.mapping_rule
        assert case.candidates == row.omega12.candidates
        assert case.components == row.omega12.components
        assert EXISTING_RUNTIME_BEHAVIOR in case.existing_evidence
        assert NO_EXPLICIT_CONTRACT in case.existing_evidence


def test_no_proposed_knowledge_change_alters_provider_behavior():
    before = ALIASES_CSV.read_bytes()
    before_breeds = BREEDS_CSV.read_bytes()
    before_hash = hashlib.sha256(before).hexdigest()
    provider = breed_identity_provider()
    assert provider.variants_for("Corgi") == ()
    assert provider.variants_for("Husky") == ()
    assert provider.variants_for("Bulldog") == ()
    assert provider.variants_for("Retriever") == ()
    review = build_review()
    unique = [case for case in review.cases if case.corpus_category == "unique_token"]
    assert [case.input for case in unique] == ["Corgi", "Husky", "Bulldog"]
    assert all(case.candidate_knowledge and "INACTIVE" in case.candidate_knowledge for case in unique)
    assert "Pembroke Welsh Corgi" in unique[0].candidate_knowledge
    assert "breed_aliases.csv until a human" in unique[0].candidate_knowledge
    assert provider.variants_for("Corgi") == ()
    assert hashlib.sha256(ALIASES_CSV.read_bytes()).hexdigest() == before_hash
    assert BREEDS_CSV.read_bytes() == before_breeds
    assert ALGORITHM_VERSION == "2.1.0"
    assert MAPPING_CONFIG_VERSION == "1.0.0"


def test_named_shared_unique_blank_mixed_questions_are_specific():
    review = build_review()
    by_input = {case.input: case for case in review.cases}
    assert "remain identity-ambiguous" in by_input["Retriever"].human_decision_question
    assert "French Bulldog" in by_input["Dog"].human_decision_question
    assert "not in the Ω12 candidate set" in by_input["Dog"].observed_difference
    assert "approved alias" in by_input["Corgi"].human_decision_question
    assert "blank breed input remain unresolved" in by_input[""].human_decision_question
    assert "without inferred percentages" in by_input["Lab x Golden"].human_decision_question
    source = REVIEW_SOURCE.read_text(encoding="utf-8")
    assert "if name == \"Corgi\"" not in source
    assert "return ACCEPT_OMEGA12_SEMANTICS" not in source
    assert "return RETAIN_LEGACY_SEMANTICS" not in source
    assert "return ADD_APPROVED_KNOWLEDGE" not in source


def test_review_is_deterministic_and_artifact_matches():
    comparison = run_comparison()
    left = build_review(report=comparison)
    right = build_review(report=comparison)
    assert left == right
    text = render_review_document(left)
    assert text == render_review_document(right)
    assert DEFAULT_REVIEW_PATH.read_text(encoding="utf-8") == text
    for case in left.cases:
        assert case.case_id in text
        assert case.human_decision_question in text
        assert case.decision_status in text
