"""Trait/environment aggregation engine (MAT-1002, MAT-1003)."""

from __future__ import annotations

from .bayesian import posterior_percent
from .formula_access import coefficient
from .formulas import FORMULA_REGISTRY
from .interaction import interaction_adjustment
from .models import EstimatedEpidemiology, MathematicalFormulaTrace, ObservedEpidemiology
from .normalization import canonical_percent, logistic, logit, percent_to_probability, probability_to_percent
from .weights import evidence_weight


class TraitAggregationEngine:
    def __init__(self, version_overrides: dict[str, str] | None = None):
        self.version_overrides = version_overrides or {}

    def estimate(
        self,
        condition_id: str,
        condition_name: str,
        observed: ObservedEpidemiology,
        edges: tuple[dict[str, str], ...],
    ) -> EstimatedEpidemiology:
        non_observed = [
            edge for edge in edges if edge.get("evidence_type", "").strip().lower() in {
                "trait",
                "environment",
                "interaction",
                "life_stage",
                "activity",
                "ingredient",
            }
        ]
        source_fact_ids = tuple(
            sorted(
                set(
                    [
                        str(edge.get("source_fact_id", "")).strip()
                        for edge in non_observed
                        if str(edge.get("source_fact_id", "")).strip()
                    ]
                )
            )
        )

        weighted_logits: list[float] = []
        total_weight = 0.0
        trait_values: list[float] = []
        env_values: list[float] = []
        for edge in non_observed:
            ev_type = edge.get("evidence_type", "").strip().lower()
            prevalence = canonical_percent(edge.get("value_number", ""))
            probability = percent_to_probability(prevalence)
            weight = evidence_weight(ev_type)
            weighted_logits.append(logit(probability) * weight)
            total_weight += weight
            if ev_type in {"trait", "life_stage", "activity"}:
                trait_values.append(prevalence)
            if ev_type in {"environment", "interaction", "ingredient"}:
                env_values.append(prevalence)

        aggregated_probability = 0.0
        if total_weight > 0:
            aggregated_probability = logistic(sum(weighted_logits) / total_weight)
        evidence_percent = probability_to_percent(aggregated_probability) if total_weight > 0 else observed.observed_prevalence

        evidence_count = len(non_observed)
        min_strength = coefficient("MAT-1002", "min_strength", 0.20, self.version_overrides)
        max_strength = coefficient("MAT-1002", "max_strength", 0.90, self.version_overrides)
        strength_divisor = max(0.000001, coefficient("MAT-1002", "strength_divisor", 10.0, self.version_overrides))
        strength = min(max_strength, max(min_strength, evidence_count / strength_divisor))
        posterior = posterior_percent(observed.observed_prevalence or 10.0, evidence_percent, strength)
        interaction_delta = interaction_adjustment(tuple([edge for edge in non_observed if edge.get("evidence_type", "").strip().lower() == "interaction"]))
        estimated = max(0.0, posterior + interaction_delta)

        trait_prevalence = (sum(trait_values) / len(trait_values)) if trait_values else 0.0
        env_prevalence = (sum(env_values) / len(env_values)) if env_values else 0.0

        f_agg = FORMULA_REGISTRY["MAT-1002"]
        f_bayes = FORMULA_REGISTRY["MAT-1003"]
        traces = (
            MathematicalFormulaTrace(
                formula_id=f_agg.formula_id,
                formula_version=f_agg.version,
                formula_name=f_agg.description,
                status="active",
                equation=f_agg.equation,
                substituted_equation=(
                    f"evidence_percent = logistic(weighted_logit_sum / total_weight)"
                    f" = logistic({round(sum(weighted_logits), 6)} / {round(total_weight, 6)})"
                ),
                python_file="repository/mathematics/aggregation.py",
                python_function="TraitAggregationEngine.estimate",
                source_line_start=14,
                source_line_end=120,
                input_variables=("edge_prevalence", "evidence_type_weights"),
                inputs={
                    "weighted_logit_sum": round(sum(weighted_logits), 6),
                    "total_weight": round(total_weight, 6),
                    "evidence_count": evidence_count,
                },
                intermediate_values={
                    "aggregated_probability": round(aggregated_probability, 6),
                    "trait_prevalence": round(trait_prevalence, 6),
                    "environment_prevalence": round(env_prevalence, 6),
                },
                output_variable="evidence_percent",
                unit="percent",
                warehouse_row_ids=tuple([f"fact_id:{fact_id}" for fact_id in source_fact_ids]),
                evidence_ids=source_fact_ids,
                parameter_values={
                    "min_strength": round(min_strength, 6),
                    "max_strength": round(max_strength, 6),
                    "strength_divisor": round(strength_divisor, 6),
                },
                output=round(evidence_percent, 6),
            ),
            MathematicalFormulaTrace(
                formula_id=f_bayes.formula_id,
                formula_version=f_bayes.version,
                formula_name=f_bayes.description,
                status="active",
                equation=f_bayes.equation,
                substituted_equation=(
                    f"posterior = logistic((1-{round(strength, 6)})*logit({round(observed.observed_prevalence, 6)})"
                    f"+{round(strength, 6)}*logit({round(evidence_percent, 6)})) + interaction_delta({round(interaction_delta, 6)})"
                ),
                python_file="repository/mathematics/aggregation.py",
                python_function="TraitAggregationEngine.estimate",
                source_line_start=14,
                source_line_end=120,
                input_variables=("prior_percent", "evidence_percent", "strength", "interaction_delta"),
                inputs={
                    "prior_percent": round(observed.observed_prevalence, 6),
                    "evidence_percent": round(evidence_percent, 6),
                    "strength": round(strength, 6),
                    "interaction_delta": round(interaction_delta, 6),
                },
                intermediate_values={"posterior_without_interaction": round(posterior, 6)},
                output_variable="estimated_prevalence",
                unit="percent",
                warehouse_row_ids=tuple([f"fact_id:{fact_id}" for fact_id in source_fact_ids]),
                evidence_ids=source_fact_ids,
                output=round(estimated, 6),
            ),
        )
        return EstimatedEpidemiology(
            condition_id=condition_id,
            condition_name=condition_name,
            estimated_prevalence=round(estimated, 6),
            trait_prevalence=round(trait_prevalence, 6),
            environment_prevalence=round(env_prevalence, 6),
            interaction_adjustment=round(interaction_delta, 6),
            evidence_count=evidence_count,
            formula_traces=traces,
        )
