"""Phase C — offline legacy BreedNode vs Ω12 resolve_breed() comparison.

Observe only. Does not migrate consumers or score either resolver.
Identity equality uses canonical_id when both sides expose one
(legacy breed_id on the selected projection row; Ω12
NormalizationResult.canonical_id).

Classification labels are SAME / AMBIGUOUS / UNRESOLVED / REGRESSION.
There is no quality label, score, ranking, or winner.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from app.agent.execution_context import ExecutionContext
from app.agent.nodes.breed_node import BreedNode
from app.agent.state import DogProfileInput
from app.core.paths import clinical_root_str
from app.data.repository import DataRepository
from app.normalization.catalog import ALIAS_FILES, MAPPING_DIR, load_catalog
from app.normalization.enums import EntityKind
from app.normalization.identity import VARIANT_ALIAS, breed_identity_provider
from app.normalization.resolver import resolve_breed
from app.normalization.text import fold_lookup_key
from app.normalization.version import MAPPING_CONFIG_VERSION

SAME = "SAME"
AMBIGUOUS = "AMBIGUOUS"
UNRESOLVED = "UNRESOLVED"
REGRESSION = "REGRESSION"
CLASSIFICATIONS = (SAME, AMBIGUOUS, UNRESOLVED, REGRESSION)

# Drift detectors only. Corpus rows still come from live identities/aliases.
EXPECTED_CANONICAL_COUNT = 48
EXPECTED_ALIAS_COUNT = 5
REPRESENTATIVE_UNIQUE_TOKENS = ("corgi", "husky", "bulldog")
UNKNOWN_INPUTS = ("__unknown_breed_phase_c__",)
MIXED_SEPARATORS = (" x ", " × ", " / ")
COMPARISON_BASIS = "canonical_id"

CATEGORY_ORDER = (
    "canonical",
    "approved_alias",
    "shared_token",
    "unique_token",
    "blank",
    "mixed",
    "intra_word_x",
    "punctuation_boundary",
    "unknown",
    "normalization",
)

DEFAULT_REPORT_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "PHASE_C_LEGACY_VS_OMEGA12_BREED_IDENTITY.md"
)


class CorpusDriftError(RuntimeError):
    """Live warehouse/Ω12 identity surface does not match the frozen expected counts."""


@dataclass(frozen=True, slots=True)
class CorpusItem:
    input: str
    category: str
    source: str
    related_canonical_names: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LegacyOutcome:
    selected: bool
    canonical_name: str | None
    canonical_id: str | None
    resolved_count: int


@dataclass(frozen=True, slots=True)
class Omega12Outcome:
    status: str
    canonical_name: str | None
    canonical_id: str | None
    mapping_rule: str | None
    mapping_source: str | None
    candidates: tuple[tuple[str, str | None], ...]
    components: tuple[tuple[str, str | None, str | None, str | None], ...]


@dataclass(frozen=True, slots=True)
class ComparisonRow:
    input: str
    category: str
    source: str
    related_canonical_names: tuple[str, ...]
    legacy: LegacyOutcome
    omega12: Omega12Outcome
    classification: str
    notes: str


@dataclass(frozen=True, slots=True)
class ComparisonReport:
    mapping_config_version: str
    warehouse_version: str
    comparison_basis: str
    corpus: tuple[CorpusItem, ...]
    rows: tuple[ComparisonRow, ...]


def _surface_token(token: str, canonical_name: str) -> str:
    for part in canonical_name.split(" "):
        if fold_lookup_key(part) == token:
            return part
    return token


def build_corpus() -> tuple[CorpusItem, ...]:
    """Deterministic corpus from current warehouse identities + Ω12 mapping knowledge."""
    provider = breed_identity_provider()
    identities = provider.identities()
    if len(identities) != EXPECTED_CANONICAL_COUNT:
        raise CorpusDriftError(
            f"canonical identity count is {len(identities)}, expected {EXPECTED_CANONICAL_COUNT}"
        )
    id_to_name = {item.canonical_id: item.canonical_name for item in identities}
    index = load_catalog().kinds[EntityKind.BREED]

    items: list[CorpusItem] = []

    for record in identities:
        items.append(
            CorpusItem(
                input=record.canonical_name,
                category="canonical",
                source="warehouse_identity",
                related_canonical_names=(record.canonical_name,),
            )
        )

    alias_rows: list[tuple[str, str, str]] = []
    alias_path = MAPPING_DIR / ALIAS_FILES[EntityKind.BREED]
    with alias_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            alias = str(row.get("alias") or "").strip()
            canonical_id = str(row.get("canonical_id") or "").strip()
            if not alias or not canonical_id:
                continue
            variants = provider.variants_for(alias)
            if not variants or any(item.variant_type != VARIANT_ALIAS for item in variants):
                raise CorpusDriftError(f"mapping alias {alias!r} is not an Ω12 VARIANT_ALIAS")
            if any(item.canonical_id != canonical_id for item in variants):
                raise CorpusDriftError(f"mapping alias {alias!r} does not match provider identity")
            related = tuple(id_to_name[item.canonical_id] for item in variants if item.canonical_id in id_to_name)
            alias_rows.append((alias, canonical_id, related[0] if related else ""))
            items.append(
                CorpusItem(
                    input=alias,
                    category="approved_alias",
                    source="omega12_mapping",
                    related_canonical_names=related,
                )
            )
    if len(alias_rows) != EXPECTED_ALIAS_COUNT:
        raise CorpusDriftError(
            f"approved alias count is {len(alias_rows)}, expected {EXPECTED_ALIAS_COUNT}"
        )

    for token in sorted(index.name_tokens):
        records = index.name_tokens[token]
        if len(records) < 2:
            continue
        names = tuple(record.canonical_name for record in records)
        items.append(
            CorpusItem(
                input=_surface_token(token, records[0].canonical_name),
                category="shared_token",
                source="derived_from_warehouse_identity",
                related_canonical_names=names,
            )
        )

    for token in REPRESENTATIVE_UNIQUE_TOKENS:
        records = index.name_tokens.get(token) or []
        if len(records) != 1:
            continue
        items.append(
            CorpusItem(
                input=_surface_token(token, records[0].canonical_name),
                category="unique_token",
                source="derived_from_warehouse_identity",
                related_canonical_names=(records[0].canonical_name,),
            )
        )

    items.append(CorpusItem(input="", category="blank", source="boundary_input"))
    items.append(CorpusItem(input="   ", category="blank", source="boundary_input"))

    first_alias, first_id, _first_name = alias_rows[0]
    partner_alias = None
    for alias, canonical_id, _name in alias_rows[1:]:
        if canonical_id != first_id:
            partner_alias = alias
            break
    if partner_alias is None:
        raise CorpusDriftError("approved aliases do not supply two distinct identities for mixed expressions")
    partner_id = next(cid for alias, cid, _name in alias_rows if alias == partner_alias)
    mixed_related = (id_to_name[first_id], id_to_name[partner_id])
    for separator in MIXED_SEPARATORS:
        items.append(
            CorpusItem(
                input=f"{first_alias}{separator}{partner_alias}",
                category="mixed",
                source="derived_from_omega12_mapping",
                related_canonical_names=mixed_related,
            )
        )
    items.append(
        CorpusItem(
            input=f"{identities[0].canonical_name} x {identities[1].canonical_name}",
            category="mixed",
            source="derived_from_warehouse_identity",
            related_canonical_names=(identities[0].canonical_name, identities[1].canonical_name),
        )
    )

    for record in identities:
        if "x" in record.canonical_name.lower():
            items.append(
                CorpusItem(
                    input=record.canonical_name,
                    category="intra_word_x",
                    source="warehouse_identity",
                    related_canonical_names=(record.canonical_name,),
                )
            )

    spaced = next((record for record in identities if " " in record.canonical_name), None)
    if spaced is not None:
        items.append(
            CorpusItem(
                input=spaced.canonical_name.replace(" ", "-"),
                category="punctuation_boundary",
                source="derived_from_warehouse_identity",
                related_canonical_names=(spaced.canonical_name,),
            )
        )

    for raw in UNKNOWN_INPUTS:
        items.append(CorpusItem(input=raw, category="unknown", source="synthetic_test_input"))

    first_name = identities[0].canonical_name
    items.append(
        CorpusItem(
            input=f"  {first_name}  ",
            category="normalization",
            source="derived_from_warehouse_identity",
            related_canonical_names=(first_name,),
        )
    )
    lowered = first_name.lower()
    if lowered != first_name:
        items.append(
            CorpusItem(
                input=lowered,
                category="normalization",
                source="derived_from_warehouse_identity",
                related_canonical_names=(first_name,),
            )
        )
    raised = first_name.upper()
    if raised != first_name:
        items.append(
            CorpusItem(
                input=raised,
                category="normalization",
                source="derived_from_warehouse_identity",
                related_canonical_names=(first_name,),
            )
        )
    first_alias_name = alias_rows[0][0]
    items.append(
        CorpusItem(
            input=f"  {first_alias_name}  ",
            category="normalization",
            source="derived_from_omega12_mapping",
            related_canonical_names=(id_to_name[first_id],),
        )
    )

    return tuple(items)


def legacy_resolve_breed_for_comparison(
    raw_value: str,
    *,
    repository: DataRepository,
) -> LegacyOutcome:
    """Call the current BreedNode.execute path. Does not copy matcher logic."""
    context = ExecutionContext(
        profile=DogProfileInput(
            name="PhaseC",
            primary_breed=raw_value,
            secondary_breed=None,
            age_years=5.4,
            weight_kg=30.0,
            current_environment="Temperate Outdoor",
            activity_level="Moderate",
        ),
        repository=repository,
    )
    BreedNode().run(context)
    payload = context.get_output("breed")
    rows = payload["breed_rows"]
    if not rows:
        return LegacyOutcome(
            selected=False,
            canonical_name=None,
            canonical_id=None,
            resolved_count=int(payload["resolved_count"]),
        )
    row = rows[0]
    breed = row.get("breed")
    breed_id = row.get("breed_id")
    return LegacyOutcome(
        selected=True,
        canonical_name=None if breed is None else str(breed),
        canonical_id=None if breed_id is None else str(breed_id),
        resolved_count=int(payload["resolved_count"]),
    )


def omega12_resolve_breed_for_comparison(raw_value: str) -> Omega12Outcome:
    """Call the public Ω12 facade. Does not reimplement matching."""
    result = resolve_breed(raw_value)
    return Omega12Outcome(
        status=str(result.status),
        canonical_name=result.canonical_name,
        canonical_id=result.canonical_id,
        mapping_rule=result.mapping_rule,
        mapping_source=result.mapping_source,
        candidates=tuple(
            (item.canonical_id, item.canonical_name) for item in result.candidates
        ),
        components=tuple(
            (str(item.status), item.canonical_id, item.canonical_name, item.mapping_rule)
            for item in result.components
        ),
    )


def classify(legacy: LegacyOutcome, omega: Omega12Outcome) -> str:
    """Factual comparison. Never returns IMPROVED. Never ranks resolvers.

    SAME: both selected the same canonical_id, or both selected no identity.
    AMBIGUOUS: Ω12 did not commit to a single identity (AMBIGUOUS or MIXED),
        or Ω12 RESOLVED to a different/missing legacy identity (review case).
    UNRESOLVED: Ω12 UNRESOLVED while legacy selected an identity.
    REGRESSION: reserved for an existing contractual requirement that Ω12
        violates. Legacy-vs-Ω12 disagreement is not automatically a regression.
        This observe-only pass never assigns REGRESSION.
    """
    status = omega.status
    if status == "RESOLVED" and legacy.selected:
        if omega.canonical_id and legacy.canonical_id and omega.canonical_id == legacy.canonical_id:
            return SAME
        if (not omega.canonical_id or not legacy.canonical_id) and (
            omega.canonical_name and omega.canonical_name == legacy.canonical_name
        ):
            return SAME
        return AMBIGUOUS
    if status == "UNRESOLVED" and not legacy.selected:
        return SAME
    if status == "AMBIGUOUS":
        return AMBIGUOUS
    if status == "MIXED":
        return AMBIGUOUS
    if status == "UNRESOLVED":
        return UNRESOLVED
    if status == "RESOLVED":
        return AMBIGUOUS
    raise CorpusDriftError(
        f"Ω12 status {status!r} is not in the approved comparison set and requires human approval"
    )


def comparison_notes(legacy: LegacyOutcome, omega: Omega12Outcome, classification: str) -> str:
    candidate_names = [name for _cid, name in omega.candidates if name]
    candidate_text = ", ".join(candidate_names)
    if classification == SAME:
        if legacy.selected:
            return (
                f"Both paths selected the same canonical identity "
                f"({legacy.canonical_id} {legacy.canonical_name}) using {COMPARISON_BASIS}."
            )
        return "Both paths selected no identity."
    if omega.status == "AMBIGUOUS":
        extra = f" Candidates: {candidate_text}." if candidate_text else ""
        if legacy.selected:
            return (
                f"Ω12 identified multiple canonical candidates and selected none; "
                f"legacy returned a single result ({legacy.canonical_name}).{extra}"
            )
        return f"Ω12 identified multiple canonical candidates and selected none; legacy selected none.{extra}"
    if omega.status == "MIXED":
        n = len(omega.components)
        if legacy.selected:
            return (
                f"Ω12 status is MIXED with {n} components in expression order; "
                f"legacy treated the input as a single matcher string and returned "
                f"{legacy.canonical_name}."
            )
        return (
            f"Ω12 status is MIXED with {n} components in expression order; "
            f"legacy treated the input as a single matcher string and selected none."
        )
    if omega.status == "UNRESOLVED" and legacy.selected:
        return f"Ω12 did not establish an identity; legacy returned {legacy.canonical_name}."
    if omega.status == "RESOLVED" and not legacy.selected:
        return f"Ω12 selected {omega.canonical_name}; legacy selected none."
    if omega.status == "RESOLVED" and legacy.selected:
        return (
            f"Ω12 selected {omega.canonical_id} {omega.canonical_name}; "
            f"legacy selected {legacy.canonical_id} {legacy.canonical_name}."
        )
    return f"Factual disagreement. classification={classification} Ω12 status={omega.status}."


def run_comparison(*, repository: DataRepository | None = None) -> ComparisonReport:
    repo = repository if repository is not None else DataRepository(clinical_root_str())
    try:
        warehouse_version = str(repo.version)
    except Exception:
        warehouse_version = "unavailable"
    corpus = build_corpus()
    rows: list[ComparisonRow] = []
    for item in corpus:
        legacy = legacy_resolve_breed_for_comparison(item.input, repository=repo)
        omega = omega12_resolve_breed_for_comparison(item.input)
        classification = classify(legacy, omega)
        rows.append(
            ComparisonRow(
                input=item.input,
                category=item.category,
                source=item.source,
                related_canonical_names=item.related_canonical_names,
                legacy=legacy,
                omega12=omega,
                classification=classification,
                notes=comparison_notes(legacy, omega, classification),
            )
        )
    return ComparisonReport(
        mapping_config_version=MAPPING_CONFIG_VERSION,
        warehouse_version=warehouse_version,
        comparison_basis=COMPARISON_BASIS,
        corpus=corpus,
        rows=tuple(rows),
    )


def _classification_counts(rows: tuple[ComparisonRow, ...]) -> dict[str, int]:
    counts = Counter(row.classification for row in rows)
    return {label: int(counts.get(label, 0)) for label in CLASSIFICATIONS}


def _category_counts(corpus: tuple[CorpusItem, ...]) -> dict[str, int]:
    counts = Counter(item.category for item in corpus)
    return {label: int(counts.get(label, 0)) for label in CATEGORY_ORDER}


def _format_legacy(outcome: LegacyOutcome) -> str:
    if not outcome.selected:
        return "selected=no"
    return (
        f"selected=yes canonical_id={outcome.canonical_id} "
        f"canonical_name={outcome.canonical_name} resolved_count={outcome.resolved_count}"
    )


def _format_omega(outcome: Omega12Outcome) -> str:
    return (
        f"status={outcome.status} canonical_id={outcome.canonical_id} "
        f"canonical_name={outcome.canonical_name} rule={outcome.mapping_rule}"
    )


def _format_candidates(outcome: Omega12Outcome) -> str:
    if not outcome.candidates:
        return "(none)"
    return "; ".join(f"{cid} {name}" for cid, name in outcome.candidates)


def render_report(report: ComparisonReport) -> str:
    category_counts = _category_counts(report.corpus)
    class_counts = _classification_counts(report.rows)
    lines: list[str] = [
        "# Phase C — Legacy vs Ω12 Breed Identity Comparison",
        "",
        "Observe only. This report does not rank resolvers or recommend a migration.",
        "",
        "## Environment / versions",
        "",
        f"- mapping_config_version: {report.mapping_config_version}",
        f"- warehouse version: {report.warehouse_version}",
        f"- comparison basis: {report.comparison_basis}",
        f"- corpus counts: {len(report.corpus)} inputs",
        "",
        "## Corpus composition",
        "",
    ]
    for category in CATEGORY_ORDER:
        lines.append(f"- {category}: {category_counts[category]}")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "Counts are tallies, not scores.",
            "",
        ]
    )
    for label in CLASSIFICATIONS:
        lines.append(f"- {label}: {class_counts[label]}")
    lines.extend(["", "## Detailed results — disagreements", ""])
    disagreements = [row for row in report.rows if row.classification != SAME]
    if not disagreements:
        lines.append("No non-SAME rows.")
    else:
        for row in disagreements:
            lines.extend(
                [
                    f"### Input: {row.input!r}",
                    "",
                    f"- Category: {row.category}",
                    f"- Source: {row.source}",
                    f"- Legacy: {_format_legacy(row.legacy)}",
                    f"- Ω12: {_format_omega(row.omega12)}",
                    f"- Classification: {row.classification}",
                    f"- Candidates: {_format_candidates(row.omega12)}",
                    f"- Rule: {row.omega12.mapping_rule}",
                    f"- Related canonical names: {', '.join(row.related_canonical_names) or '(none)'}",
                    f"- Notes: {row.notes}",
                    "",
                ]
            )
            if row.omega12.components:
                lines.append("- Components:")
                for status, cid, name, rule in row.omega12.components:
                    lines.append(f"  - {status} {cid} {name} rule={rule}")
                lines.append("")
    lines.extend(["", "## SAME cases (compact)", ""])
    for row in report.rows:
        if row.classification != SAME:
            continue
        if row.legacy.selected:
            identity = f"{row.legacy.canonical_id} {row.legacy.canonical_name}"
        else:
            identity = "(no identity)"
        lines.append(f"- {row.input!r} [{row.category}] → {identity}")
    lines.append("")
    return "\n".join(lines)


def write_report(path: Path | None = None, *, report: ComparisonReport | None = None) -> Path:
    target = path if path is not None else DEFAULT_REPORT_PATH
    payload = report if report is not None else run_comparison()
    target.write_text(render_report(payload), encoding="utf-8")
    return target


def main() -> None:
    path = write_report()
    print(path)


if __name__ == "__main__":
    main()
