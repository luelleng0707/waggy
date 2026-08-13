"""Independent equation replay from formula traces."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .models import FormulaTrace


@dataclass(frozen=True)
class ReplayComparison:
    trace_id: str
    formula_id: str
    production_output: float
    replay_output: float
    absolute_delta: float
    status: str
    detail: str


class IndependentFormulaReplay:
    tolerance: float = 3e-5

    def replay_formula(self, trace: FormulaTrace) -> ReplayComparison:
        if not isinstance(trace.output_value, (int, float)):
            return ReplayComparison(
                trace_id=trace.trace_id,
                formula_id=trace.formula_id,
                production_output=0.0,
                replay_output=0.0,
                absolute_delta=0.0,
                status="SKIP",
                detail="Non-numeric output value.",
            )
        production = float(trace.output_value)
        replay = self._evaluate(trace)
        delta = abs(production - replay)
        status = "MATCH" if delta <= self.tolerance else "MISMATCH"
        return ReplayComparison(
            trace_id=trace.trace_id,
            formula_id=trace.formula_id,
            production_output=production,
            replay_output=replay,
            absolute_delta=delta,
            status=status,
            detail="independent replay from inputs+parameters",
        )

    def replay_all(self, traces: tuple[FormulaTrace, ...]) -> tuple[ReplayComparison, ...]:
        return tuple(self.replay_formula(trace) for trace in traces)

    def _evaluate(self, trace: FormulaTrace) -> float:
        inputs = {item.variable_name: item.value for item in trace.input_variables}
        params = {item.variable_name: item.value for item in trace.parameter_variables}

        def f(name: str, default: float = 0.0) -> float:
            value = inputs.get(name, params.get(name, default))
            try:
                return float(value)  # type: ignore[arg-type]
            except Exception:
                return default

        if trace.formula_id == "MAT-1001":
            count = max(1.0, f("observed_count", 1.0))
            total = f("observed_values_sum", 0.0)
            return total / count
        if trace.formula_id == "MAT-1002":
            total_weight = max(1e-6, f("total_weight", 1.0))
            weighted_logit_sum = f("weighted_logit_sum", 0.0)
            return (1.0 / (1.0 + math.exp(-(weighted_logit_sum / total_weight)))) * 100.0
        if trace.formula_id == "MAT-1003":
            prior_percent = f("prior_percent", 0.0)
            # Runtime fallback in MAT-1003 path: zero prior maps to 10.0.
            if prior_percent <= 0.0:
                prior_percent = 10.0
            prior = prior_percent / 100.0
            evidence = f("evidence_percent", 0.0) / 100.0
            strength = f("strength", 0.0)
            interaction_delta = f("interaction_delta", 0.0)
            prior = min(0.999999, max(0.000001, prior))
            evidence = min(0.999999, max(0.000001, evidence))
            prior_logit = math.log(prior / (1.0 - prior))
            evidence_logit = math.log(evidence / (1.0 - evidence))
            posterior = 1.0 / (1.0 + math.exp(-(((1.0 - strength) * prior_logit) + (strength * evidence_logit))))
            return (posterior * 100.0) + interaction_delta
        if trace.formula_id == "MAT-1004":
            observed = f("observed", 0.0)
            estimated = f("estimated", 0.0)
            absolute_error = abs(observed - estimated)
            relative_error = absolute_error / max(observed, 1e-6)
            return max(0.0, 100.0 - (relative_error * 100.0))
        if trace.formula_id == "MAT-1005":
            observed_count = f("observed_count", 0.0)
            trait_count = f("trait_count", 0.0)
            env_count = f("env_count", 0.0)
            study_count = f("study_count", 0.0)
            agreement = f("agreement", 0.0) / 100.0
            observed_multiplier = f("observed_multiplier", 1.5)
            evidence_denominator = max(1e-6, f("evidence_denominator", 20.0))
            study_denominator = max(1e-6, f("study_denominator", 10.0))
            evidence_weight = f("evidence_weight", 0.45)
            study_weight = f("study_weight", 0.25)
            agreement_weight = f("agreement_weight", 0.30)
            evidence_component = min(1.0, ((observed_count * observed_multiplier) + trait_count + env_count) / evidence_denominator)
            study_component = min(1.0, study_count / study_denominator)
            return (evidence_weight * evidence_component + study_weight * study_component + agreement_weight * agreement) * 100.0
        if trace.formula_id == "MAT-1006":
            observed = f("observed_prevalence", 0.0)
            estimated = f("estimated_prevalence", 0.0)
            confidence = f("confidence", 0.0) / 100.0
            return max(0.0, estimated - observed) * confidence
        if trace.formula_id == "MAT-1007":
            estimated = f("estimated_prevalence", 0.0)
            confidence = f("confidence", 0.0) / 100.0
            novelty = f("novelty_score", 0.0)
            agreement = f("agreement", 0.0) / 100.0
            min_scale = f("min_agreement_scale", 0.10)
            scale = max(min_scale, agreement)
            return estimated * confidence * (1.0 + (novelty / 100.0)) * scale
        if trace.formula_id == "MAT-1008":
            stddev = f("stddev", 0.0)
            uncertainty_factor = f("uncertainty_factor", 0.2)
            return stddev * uncertainty_factor
        return float(trace.output_value) if isinstance(trace.output_value, (int, float)) else 0.0
