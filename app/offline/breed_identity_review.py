"""Phase D — offline breed identity semantic review.

Consumes Phase C observations. Does not decide identity meaning.
Does not add aliases, change Ω12, or migrate Core consumers.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from app.offline.breed_identity_compare import (
    SAME,
    ComparisonReport,
    ComparisonRow,
    DEFAULT_REPORT_PATH as PHASE_C_REPORT_PATH,
    run_comparison,
)

REQUIRES_HUMAN_DECISION = "REQUIRES_HUMAN_DECISION"
ACCEPT_OMEGA12_SEMANTICS = "ACCEPT_OMEGA12_SEMANTICS"
RETAIN_LEGACY_SEMANTICS = "RETAIN_LEGACY_SEMANTICS"
ADD_APPROVED_KNOWLEDGE = "ADD_APPROVED_KNOWLEDGE"
DEFER = "DEFER"
DECISION_STATUSES = (
    REQUIRES_HUMAN_DECISION,
    ACCEPT_OMEGA12_SEMANTICS,
    RETAIN_LEGACY_SEMANTICS,
    ADD_APPROVED_KNOWLEDGE,
    DEFER,
)

EXISTING_TEST_CONTRACT = "EXISTING_TEST_CONTRACT"
EXISTING_RUNTIME_BEHAVIOR = "EXISTING_RUNTIME_BEHAVIOR"
EXISTING_APPROVED_MAPPING = "EXISTING_APPROVED_MAPPING"
EXISTING_WAREHOUSE_IDENTITY = "EXISTING_WAREHOUSE_IDENTITY"
NO_EXPLICIT_CONTRACT = "NO_EXPLICIT_CONTRACT"
EVIDENCE_KINDS = (
    EXISTING_TEST_CONTRACT,
    EXISTING_RUNTIME_BEHAVIOR,
    EXISTING_APPROVED_MAPPING,
    EXISTING_WAREHOUSE_IDENTITY,
    NO_EXPLICIT_CONTRACT,
)

PROPOSED_ACTION_NONE = "NONE"

GROUP_A_SHARED_TOKEN = "GROUP_A_SHARED_TOKEN"
GROUP_B_UNIQUE_TOKEN = "GROUP_B_UNIQUE_TOKEN"
GROUP_C_BLANK = "GROUP_C_BLANK"
GROUP_D_MIXED = "GROUP_D_MIXED"
GROUP_E_PUNCTUATION = "GROUP_E_PUNCTUATION"
GROUP_F_OTHER = "GROUP_F_OTHER"

CATEGORY_TO_GROUP = {
    "shared_token": GROUP_A_SHARED_TOKEN,
    "unique_token": GROUP_B_UNIQUE_TOKEN,
    "blank": GROUP_C_BLANK,
    "mixed": GROUP_D_MIXED,
    "punctuation_boundary": GROUP_E_PUNCTUATION,
}

DEFAULT_REVIEW_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "PHASE_D_BREED_IDENTITY_SEMANTIC_REVIEW.md"
)

# Named tests freeze current behavior. They do not, by themselves, decide
# product identity meaning for a later consumer migration.
_NAMED_TESTS: dict[str, tuple[str, ...]] = {
    "Retriever": (
        "tests/normalization/test_omega12_mapping.py::test_f_ambiguous_retriever",
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved",
        "tests/data/test_breed_node_baseline.py::test_contains_retriever_is_first_dataframe_contains_hit (current-behavior capture; not a product-meaning contract)",
    ),
    "Terrier": (
        "tests/normalization/test_omega12_mapping.py::test_f_ambiguous_terrier",
    ),
    "Corgi": (
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved",
        "tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants",
    ),
    "Husky": (
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved",
        "tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants",
    ),
    "Bulldog": (
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved",
        "tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants",
    ),
    "": (
        "tests/normalization/test_omega12_mapping.py::test_q_blank_breed_is_not_provided",
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x",
        "tests/data/test_breed_node_baseline.py::test_empty_primary_contains_all_and_takes_first_dataframe_row (current-behavior capture; not a product-meaning contract)",
    ),
    "Lab x Golden": (
        "tests/normalization/test_omega12_mapping.py::test_r_mixed_breed_is_not_a_new_canonical_breed (exact test string is 'Labrador x Golden'; same mixed_breed_separator rule)",
    ),
    "Lab × Golden": (
        "tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x (uses 'Labrador × Golden')",
    ),
    "Lab / Golden": (
        "tests/normalization/test_omega12_mapping.py::test_r_slash_mixed_breed (uses 'Labrador Retriever / Golden Retriever')",
    ),
}


class ReviewDriftError(RuntimeError):
    """Live Phase C disagreements do not match the Phase C artifact."""


@dataclass(frozen=True, slots=True)
class ReviewCase:
    case_id: str
    input: str
    corpus_category: str
    review_group: str
    legacy_result: str
    omega12_result: str
    omega12_status: str
    omega12_rule: str | None
    candidates: tuple[tuple[str, str | None], ...]
    components: tuple[tuple[str, str | None, str | None, str | None], ...]
    observed_difference: str
    existing_evidence: tuple[str, ...]
    evidence_notes: str
    decision_status: str
    proposed_action: str
    human_decision_question: str
    notes: str
    candidate_knowledge: str | None


@dataclass(frozen=True, slots=True)
class ReviewMatrix:
    mapping_config_version: str
    warehouse_version: str
    cases: tuple[ReviewCase, ...]


def _artifact_disagreement_inputs(path: Path = PHASE_C_REPORT_PATH) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    inputs: list[str] = []
    in_detail = False
    for line in text.splitlines():
        if line.startswith("## Detailed results"):
            in_detail = True
            continue
        if in_detail and line.startswith("## "):
            break
        if in_detail and line.startswith("### Input: "):
            inputs.append(ast.literal_eval(line[len("### Input: ") :]))
    return tuple(inputs)


def _format_legacy(row: ComparisonRow) -> str:
    if not row.legacy.selected:
        return "selected=no"
    return f"{row.legacy.canonical_id} {row.legacy.canonical_name}"


def _format_omega(row: ComparisonRow) -> str:
    return (
        f"status={row.omega12.status} canonical_id={row.omega12.canonical_id} "
        f"rule={row.omega12.mapping_rule}"
    )


def _candidate_names(row: ComparisonRow) -> tuple[str, ...]:
    return tuple(name for _cid, name in row.omega12.candidates if name)


def _observed_difference(row: ComparisonRow) -> str:
    if row.category == "shared_token":
        extra = ""
        candidate_ids = {cid for cid, _name in row.omega12.candidates}
        if row.legacy.selected and row.legacy.canonical_id and row.legacy.canonical_id not in candidate_ids:
            extra = (
                f" Legacy selected {row.legacy.canonical_name}, which is not in the Ω12 candidate set."
            )
        return (
            f"Legacy selected {row.legacy.canonical_name}. Ω12 status is AMBIGUOUS "
            f"with {len(row.omega12.candidates)} candidates and selected none. "
            f"Ω12 rule is {row.omega12.mapping_rule}.{extra}"
        )
    if row.category == "unique_token":
        return (
            f"Legacy selected {row.legacy.canonical_name}. Ω12 status is UNRESOLVED "
            f"({row.omega12.mapping_rule}). Catalog uniqueness is not an approved mapping."
        )
    if row.category == "blank":
        return (
            f"Legacy selected {row.legacy.canonical_name}. Ω12 status is UNRESOLVED "
            f"({row.omega12.mapping_rule})."
        )
    if row.category == "mixed":
        n = len(row.omega12.components)
        legacy = (
            f"returned {row.legacy.canonical_name}"
            if row.legacy.selected
            else "selected none"
        )
        return (
            f"Ω12 status is MIXED with {n} components in expression order and no "
            f"inferred percentages. Legacy treated the input as a single matcher string "
            f"and {legacy}."
        )
    return row.notes


def _evidence(row: ComparisonRow) -> tuple[tuple[str, ...], str]:
    kinds: list[str] = [EXISTING_RUNTIME_BEHAVIOR, NO_EXPLICIT_CONTRACT]
    notes: list[str] = [
        "Observed current behavior is not automatically intended product meaning.",
        "Ω12 current rules are not automatically final product policy.",
        "BreedNode baseline tests are current-behavior capture, not a meaning contract.",
    ]
    named = _NAMED_TESTS.get(row.input, ())
    if named:
        kinds.insert(0, EXISTING_TEST_CONTRACT)
        notes.append("Named tests freeze current resolver/capture behavior: " + "; ".join(named))
    if row.category == "shared_token":
        kinds.append(EXISTING_WAREHOUSE_IDENTITY)
        notes.append("Ω12 candidates are current warehouse canonical names containing this token.")
    if row.category == "unique_token":
        kinds.append(EXISTING_WAREHOUSE_IDENTITY)
        notes.append(
            "A warehouse canonical name contains this token once. "
            "That token is not in warehouse/mapping/breed_aliases.csv."
        )
    if row.category == "mixed":
        kinds.append(EXISTING_WAREHOUSE_IDENTITY)
        if row.omega12.components and any(rule == "explicit_alias" for _s, _i, _n, rule in row.omega12.components):
            kinds.append(EXISTING_APPROVED_MAPPING)
            notes.append("Mixed components resolve through existing canonical names or approved aliases.")
        notes.append("docs/WAGGY_SYSTEM.md documents MIXED as not a new canonical breed.")
    if row.input == "Retriever":
        notes.append(
            "docs/WAGGY_SYSTEM.md documents that Ω12 does not pick Labrador for retriever. "
            "That describes current Ω12 design, not a Core-consumer migration decision."
        )
    # Preserve deterministic kind order without set iteration.
    ordered: list[str] = []
    for kind in EVIDENCE_KINDS:
        if kind in kinds and kind not in ordered:
            ordered.append(kind)
    return tuple(ordered), " ".join(notes)


def _human_question(row: ComparisonRow) -> str:
    names = ", ".join(_candidate_names(row))
    if row.category == "shared_token" and row.input == "Dog":
        return (
            "Should bare 'Dog' remain identity-ambiguous across the Ω12 candidates "
            f"({names}), remain unresolved, or resolve to a single canonical breed? "
            "Legacy currently selects French Bulldog, which is not in the Ω12 candidate set."
        )
    if row.category == "shared_token":
        return (
            f"Should bare {row.input!r} resolve to a single canonical breed, remain "
            f"unresolved, or remain identity-ambiguous across the Ω12 candidates ({names})?"
        )
    if row.category == "unique_token":
        return (
            f"Should bare {row.input!r} be treated as an approved alias for a specific "
            "canonical breed, or remain unresolved?"
        )
    if row.category == "blank":
        return (
            "Should blank breed input remain unresolved rather than inherit a legacy "
            "first-row result?"
        )
    if row.category == "mixed":
        return (
            "Should mixed breed strings using x / × remain multi-component MIXED "
            "identities in expression order without inferred percentages, rather than "
            "a single matcher string?"
        )
    return f"What identity semantics should Waggy use for {row.input!r}?"


def _candidate_knowledge(row: ComparisonRow) -> str | None:
    if row.category != "unique_token":
        return None
    return (
        f"INACTIVE candidate knowledge: {row.input!r} is not an approved alias. "
        f"Legacy selected {row.legacy.canonical_name}. Ω12 is UNRESOLVED. "
        "No canonical target is assigned. Do not write this into breed_aliases.csv "
        "until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity."
    )


def _case_from_row(index: int, row: ComparisonRow) -> ReviewCase:
    evidence, evidence_notes = _evidence(row)
    return ReviewCase(
        case_id=f"D-{index:02d}",
        input=row.input,
        corpus_category=row.category,
        review_group=CATEGORY_TO_GROUP.get(row.category, GROUP_F_OTHER),
        legacy_result=_format_legacy(row),
        omega12_result=_format_omega(row),
        omega12_status=row.omega12.status,
        omega12_rule=row.omega12.mapping_rule,
        candidates=row.omega12.candidates,
        components=row.omega12.components,
        observed_difference=_observed_difference(row),
        existing_evidence=evidence,
        evidence_notes=evidence_notes,
        decision_status=REQUIRES_HUMAN_DECISION,
        proposed_action=PROPOSED_ACTION_NONE,
        human_decision_question=_human_question(row),
        notes=(
            "Observation only. proposed_action remains NONE. "
            "No B2C clarification flow is implied."
        ),
        candidate_knowledge=_candidate_knowledge(row),
    )


def build_review(*, report: ComparisonReport | None = None) -> ReviewMatrix:
    comparison = report if report is not None else run_comparison()
    live = tuple(row for row in comparison.rows if row.classification != SAME)
    artifact_inputs = _artifact_disagreement_inputs()
    live_inputs = tuple(row.input for row in live)
    if live_inputs != artifact_inputs:
        raise ReviewDriftError(
            "Phase C artifact disagreements do not match live comparison: "
            f"artifact={artifact_inputs!r} live={live_inputs!r}"
        )
    cases = tuple(_case_from_row(i, row) for i, row in enumerate(live, start=1))
    if any(case.decision_status != REQUIRES_HUMAN_DECISION for case in cases):
        raise ReviewDriftError("Phase D must not auto-assign semantic decisions")
    return ReviewMatrix(
        mapping_config_version=comparison.mapping_config_version,
        warehouse_version=comparison.warehouse_version,
        cases=cases,
    )


def _md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _display_input(value: str) -> str:
    return repr(value)


def render_review_document(review: ReviewMatrix) -> str:
    counts: dict[str, int] = {}
    for case in review.cases:
        counts[case.decision_status] = counts.get(case.decision_status, 0) + 1
    lines: list[str] = [
        "# Phase D — Breed Identity Semantic Review",
        "",
        "## Scope",
        "",
        "Phase A+B established the Ω12 breed identity provider and `resolve_breed()` facade.",
        "Phase C observed disagreements between legacy BreedNode matching and Ω12.",
        "Phase D records the human/domain/product decisions still required.",
        "",
        "This artifact does not decide breed meaning. Cursor is not the reviewer.",
        "No aliases were added. No resolver rules changed. No Core consumer migrated.",
        "No API or B2C UI changed.",
        "",
        f"- mapping_config_version: {review.mapping_config_version}",
        f"- warehouse version: {review.warehouse_version}",
        f"- review cases: {len(review.cases)}",
        f"- {REQUIRES_HUMAN_DECISION}: {counts.get(REQUIRES_HUMAN_DECISION, 0)}",
        f"- {ACCEPT_OMEGA12_SEMANTICS}: {counts.get(ACCEPT_OMEGA12_SEMANTICS, 0)}",
        f"- {RETAIN_LEGACY_SEMANTICS}: {counts.get(RETAIN_LEGACY_SEMANTICS, 0)}",
        f"- {ADD_APPROVED_KNOWLEDGE}: {counts.get(ADD_APPROVED_KNOWLEDGE, 0)}",
        f"- {DEFER}: {counts.get(DEFER, 0)}",
        "",
        "Review groups are organizational only. They are not a priority ranking.",
        "",
        "## Evidence rules",
        "",
        "- EXISTING_RUNTIME_BEHAVIOR: what BreedNode or Ω12 currently returns.",
        "- EXISTING_TEST_CONTRACT: a test currently asserts that current behavior.",
        "  A capture test is not a product-meaning contract.",
        "- EXISTING_APPROVED_MAPPING: an alias already present in `breed_aliases.csv`.",
        "- EXISTING_WAREHOUSE_IDENTITY: a canonical row in `warehouse/biology/breeds.csv`.",
        "- NO_EXPLICIT_CONTRACT: the repository does not establish intended identity meaning.",
        "",
        "Legacy selected X is runtime behavior. It is not automatically Waggy's intended identity.",
        "Ω12 AMBIGUOUS/UNRESOLVED/MIXED is current resolver behavior. It is not automatically",
        "final product policy, and it does not by itself require a B2C clarification prompt.",
        "",
        "## Review matrix",
        "",
        "| Case | Input | Category | Legacy | Ω12 | Evidence | Decision |",
        "|------|-------|----------|--------|-----|----------|----------|",
    ]
    for case in review.cases:
        evidence = ", ".join(case.existing_evidence)
        lines.append(
            "| "
            + " | ".join(
                [
                    case.case_id,
                    _md_escape(_display_input(case.input)),
                    case.corpus_category,
                    _md_escape(case.legacy_result),
                    _md_escape(case.omega12_result),
                    _md_escape(evidence),
                    case.decision_status,
                ]
            )
            + " |"
        )
    lines.extend(["", "## Review cases", ""])
    current_group = None
    for case in review.cases:
        if case.review_group != current_group:
            current_group = case.review_group
            lines.extend([f"### {case.review_group}", ""])
        candidate_text = "(none)"
        if case.candidates:
            candidate_text = "; ".join(f"{cid} {name}" for cid, name in case.candidates)
        lines.extend(
            [
                f"#### {case.case_id} — {_display_input(case.input)}",
                "",
                f"- Category: {case.corpus_category}",
                f"- Legacy result: {case.legacy_result}",
                f"- Ω12 result: {case.omega12_result}",
                f"- Candidates: {candidate_text}",
                f"- Ω12 rule: {case.omega12_rule}",
                f"- Existing evidence: {', '.join(case.existing_evidence)}",
                f"- Evidence notes: {case.evidence_notes}",
                f"- Observed difference: {case.observed_difference}",
                f"- Decision status: {case.decision_status}",
                f"- Proposed action: {case.proposed_action}",
                f"- Human decision question: {case.human_decision_question}",
                f"- Notes: {case.notes}",
                "",
            ]
        )
        if case.components:
            lines.append("- Components:")
            for status, cid, name, rule in case.components:
                lines.append(f"  - {status} {cid} {name} rule={rule}")
            lines.append("")
        if case.candidate_knowledge:
            lines.extend([f"- Candidate knowledge: {case.candidate_knowledge}", ""])

    unique_candidates = [case for case in review.cases if case.candidate_knowledge]
    lines.extend(
        [
            "## Candidate knowledge changes",
            "",
            "These rows are inactive. They must not be written to mapping CSVs,",
            "the Ω12 provider, or KindIndex until a human supplies ADD_APPROVED_KNOWLEDGE",
            "with an explicit canonical identity.",
            "",
        ]
    )
    if unique_candidates:
        for case in unique_candidates:
            lines.append(f"- {case.case_id} {case.input!r}: {case.candidate_knowledge}")
        lines.append("")
    else:
        lines.append("None.")
        lines.append("")

    lines.extend(
        [
            "## Future product implications",
            "",
            "Non-binding architecture notes only. Not implemented in this phase.",
            "",
            "- IDENTITY ENGINE vs PRODUCT UX remain separate layers.",
            "- AMBIGUOUS means Ω12 did not establish a single identity. A future product",
            "  layer may present candidates without ranking, or may choose another policy.",
            "  Candidate order is warehouse encounter order, not recommendation.",
            "- UNRESOLVED means Ω12 has no approved mapping. A future product layer may",
            "  ask for refinement, show supported breeds, allow uncertainty, or continue",
            "  without breed-specific reasoning. Phase D does not choose among these.",
            "- MIXED already carries component identities in expression order and must not",
            "  infer 50/50 or collapse to one canonical breed unless a later human decision",
            "  says otherwise.",
            "- Structured profile fields `primary_breed` / `secondary_breed` / `breed_split_pct`",
            "  remain separate from mixed identity strings.",
            "",
            "FUTURE_PRODUCT_DECISION applies to UX strategy. It is not a substitute for the",
            "identity-meaning questions above.",
            "",
            "## Explicit non-decisions",
            "",
            "- no aliases were added",
            "- no resolver rules changed",
            "- no Core consumer migrated",
            "- no API changed",
            "- no B2C UI changed",
            "- no Mongo added",
            "- no LLM used",
            "- no fuzzy matching added",
            "- no semantic winner was selected",
            "",
        ]
    )
    return "\n".join(lines)


def write_review(path: Path | None = None, *, review: ReviewMatrix | None = None) -> Path:
    target = path if path is not None else DEFAULT_REVIEW_PATH
    payload = review if review is not None else build_review()
    target.write_text(render_review_document(payload), encoding="utf-8")
    return target


def main() -> None:
    path = write_review()
    print(path)


if __name__ == "__main__":
    main()
